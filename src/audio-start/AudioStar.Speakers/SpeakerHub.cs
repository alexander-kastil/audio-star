using System.Collections.Concurrent;
using AudioStar.Speakers.Discovery;
using AudioStar.Speakers.Events;
using AudioStar.Speakers.Protocol;

namespace AudioStar.Speakers;

internal sealed class SpeakerHub(
    ISettingsStore settings,
    IHttpClientFactory httpFactory,
    SpeakerEventRouter router,
    SpeakerEventListener listener,
    SpeakerProber prober,
    SsdpDiscovery ssdp,
    MdnsDiscovery mdns,
    SpeakerCache cache,
    ILoggerFactory loggerFactory) : ISpeakerHub, IAsyncDisposable
{
    private static readonly TimeSpan ExpireAfter = TimeSpan.FromSeconds(90);

    private readonly ILogger<SpeakerHub> _logger = loggerFactory.CreateLogger<SpeakerHub>();
    private readonly ConcurrentDictionary<string, SpeakerSession> _sessions = new(StringComparer.OrdinalIgnoreCase);
    private readonly ConcurrentDictionary<string, byte> _probing = new();
    private readonly SemaphoreSlim _addGate = new(1, 1);
    private CancellationTokenSource? _run;
    private List<Task> _tasks = [];

    public IReadOnlyList<ISpeakerSession> Speakers => [.. _sessions.Values.OrderBy(s => s.Info.Name, StringComparer.OrdinalIgnoreCase)];

    public event EventHandler<ISpeakerSession>? SpeakerAdded;

    public event EventHandler<ISpeakerSession>? SpeakerRemoved;

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        if (_run is not null)
        {
            return;
        }
        _run = new CancellationTokenSource();
        var token = _run.Token;
        await listener.StartAsync(settings.Current.EventListenerPort, cancellationToken);
        settings.Changed += OnSettingsChanged;
        _tasks =
        [
            Task.Run(() => ProbeCacheAsync(token)),
            Task.Run(() => ssdp.RunAsync(OnSsdpReplyAsync, token)),
            Task.Run(() => mdns.RunAsync(OnMdnsAddressAsync, token)),
            Task.Run(() => RunManualAndSweepAsync(token))
        ];
    }

    public async Task StopAsync(CancellationToken cancellationToken)
    {
        if (_run is null)
        {
            return;
        }
        settings.Changed -= OnSettingsChanged;
        await _run.CancelAsync();
        try
        {
            await Task.WhenAll(_tasks).WaitAsync(TimeSpan.FromSeconds(5), cancellationToken);
        }
        catch (Exception ex) when (ex is TimeoutException or OperationCanceledException)
        {
        }
        foreach (var session in _sessions.Values)
        {
            await session.DisposeAsync();
        }
        _sessions.Clear();
        await listener.StopAsync(cancellationToken);
        _run.Dispose();
        _run = null;
    }

    public async Task RefreshAsync(CancellationToken cancellationToken = default)
    {
        await Task.WhenAll(
            ssdp.SearchOnceAsync(OnSsdpReplyAsync, cancellationToken),
            mdns.ScanOnceAsync(OnMdnsAddressAsync, cancellationToken),
            ProbeManualAsync(cancellationToken));
    }

    public async Task<ISpeakerSession?> AddByIpAsync(string ipAddress, CancellationToken cancellationToken = default)
    {
        if (!IPAddress.TryParse(ipAddress?.Trim(), out var ip))
        {
            return null;
        }
        var probe = await prober.ProbeAsync(ip.ToString(), SpeakerProber.DefaultUpnpPort, cancellationToken);
        return probe is null ? null : await AddOrUpdateAsync(probe, cancellationToken);
    }

    public ISpeakerSession? Find(string speakerId)
    {
        return _sessions.TryGetValue(SpeakerIdentity.Normalize(speakerId), out var session) ? session : null;
    }

    public async ValueTask DisposeAsync()
    {
        await StopAsync(CancellationToken.None);
    }

    private Task OnSsdpReplyAsync(SsdpReply reply, CancellationToken cancellationToken)
    {
        return HandleCandidateAsync(reply.Host, reply.Port, cancellationToken);
    }

    private Task OnMdnsAddressAsync(string address, CancellationToken cancellationToken)
    {
        return HandleCandidateAsync(address, SpeakerProber.DefaultUpnpPort, cancellationToken);
    }

    private void OnSettingsChanged(object? sender, EventArgs e)
    {
        var token = _run?.Token ?? CancellationToken.None;
        _ = Task.Run(() => ProbeManualAsync(token), token);
    }

    private async Task HandleCandidateAsync(string host, int port, CancellationToken cancellationToken)
    {
        if (_sessions.Values.FirstOrDefault(s => s.Info.IpAddress == host) is { } known)
        {
            known.Touch();
            return;
        }
        if (!_probing.TryAdd(host, 0))
        {
            return;
        }
        try
        {
            var probe = await prober.ProbeAsync(host, port, cancellationToken);
            if (probe is not null)
            {
                await AddOrUpdateAsync(probe, cancellationToken);
            }
        }
        catch (OperationCanceledException)
        {
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Adding speaker at {Host} failed", host);
        }
        finally
        {
            _probing.TryRemove(host, out _);
        }
    }

    private async Task<ISpeakerSession> AddOrUpdateAsync(ProbeResult probe, CancellationToken cancellationToken)
    {
        await _addGate.WaitAsync(cancellationToken);
        SpeakerSession session;
        SpeakerSession? replaced = null;
        try
        {
            if (_sessions.TryGetValue(probe.Info.Id, out var existing))
            {
                if (existing.Info.IpAddress == probe.Info.IpAddress && existing.Info.UpnpPort == probe.Info.UpnpPort)
                {
                    existing.Touch();
                    return existing;
                }
                replaced = existing;
                _sessions.TryRemove(probe.Info.Id, out _);
            }
            var client = new SpeakerClient(probe.Info.IpAddress, probe.Info.UpnpPort, httpFactory);
            session = new SpeakerSession(probe.Info, probe.Status, client, router, settings.Current.EventListenerPort, loggerFactory.CreateLogger<SpeakerSession>());
            await session.StartAsync(cancellationToken);
            _sessions[probe.Info.Id] = session;
        }
        finally
        {
            _addGate.Release();
        }
        if (replaced is not null)
        {
            await replaced.DisposeAsync();
            SpeakerRemoved?.Invoke(this, replaced);
        }
        SpeakerAdded?.Invoke(this, session);
        _logger.LogInformation("Speaker {Name} ({Id}) at {Ip}", probe.Info.Name, probe.Info.Id, probe.Info.IpAddress);
        await cache.UpsertAsync(new CachedSpeaker(probe.Info.Id, probe.Info.Name, probe.Info.IpAddress, probe.Info.UpnpPort), cancellationToken);
        return session;
    }

    private async Task ProbeCacheAsync(CancellationToken cancellationToken)
    {
        try
        {
            var rows = await cache.LoadAsync(cancellationToken);
            await Task.WhenAll(rows.Select(async row =>
            {
                if (_sessions.Values.Any(s => s.Info.IpAddress == row.Ip))
                {
                    return;
                }
                var probe = await prober.ProbeAsync(row.Ip, row.Port, cancellationToken);
                if (probe is null)
                {
                    await cache.RemoveAsync(row.Id, cancellationToken);
                    return;
                }
                await AddOrUpdateAsync(probe, cancellationToken);
            }));
        }
        catch (OperationCanceledException)
        {
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Cached speakers could not be probed");
        }
    }

    private async Task ProbeManualAsync(CancellationToken cancellationToken)
    {
        foreach (var address in settings.Current.ManualSpeakerIps.ToArray())
        {
            if (cancellationToken.IsCancellationRequested)
            {
                return;
            }
            if (IPAddress.TryParse(address?.Trim(), out var ip))
            {
                await HandleCandidateAsync(ip.ToString(), SpeakerProber.DefaultUpnpPort, cancellationToken);
            }
        }
    }

    private async Task RunManualAndSweepAsync(CancellationToken cancellationToken)
    {
        var tick = 0;
        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                if (tick % 3 == 0)
                {
                    await ProbeManualAsync(cancellationToken);
                }
                tick++;
                await SweepAsync();
                await Task.Delay(TimeSpan.FromSeconds(10), cancellationToken);
            }
            catch (OperationCanceledException)
            {
                return;
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Speaker sweep failed");
            }
        }
    }

    private async Task SweepAsync()
    {
        foreach (var session in _sessions.Values.Where(s => s.SinceLastSeen > ExpireAfter).ToList())
        {
            if (!_sessions.TryRemove(session.Info.Id, out _))
            {
                continue;
            }
            _logger.LogInformation("Speaker {Name} ({Id}) stopped answering", session.Info.Name, session.Info.Id);
            await session.DisposeAsync();
            SpeakerRemoved?.Invoke(this, session);
        }
    }
}
