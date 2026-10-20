using System.Text.Json;
using AudioStar.Speakers.Discovery;
using AudioStar.Speakers.Events;
using AudioStar.Speakers.Protocol;

namespace AudioStar.Speakers;

internal sealed class SpeakerSession : ISpeakerSession, IAsyncDisposable
{
    private static readonly string[] EventServices = ["rendertransport1", "rendercontrol1", "PlayQueue1"];
    private static readonly TimeSpan Reconcile = TimeSpan.FromSeconds(30);

    private readonly object _gate = new();
    private readonly SpeakerEventRouter _router;
    private readonly int _eventPort;
    private readonly ILogger<SpeakerSession> _logger;
    private readonly CancellationTokenSource _stop = new();
    private readonly List<Task> _tasks = [];
    private PlaybackState _state = PlaybackState.Empty;
    private string? _leaderId;
    private IReadOnlyList<string> _followerIds = [];
    private int _groupDirty;
    private long _notifyCount;
    private long _lastSeen = Environment.TickCount64;

    public SpeakerSession(
        SpeakerInfo info,
        SpeakerStatus status,
        SpeakerClient client,
        SpeakerEventRouter router,
        int eventPort,
        ILogger<SpeakerSession> logger)
    {
        Info = info;
        Status = status;
        Client = client;
        _router = router;
        _eventPort = eventPort;
        _logger = logger;
        Controller = new SpeakerController(this, client, logger);
    }

    public SpeakerInfo Info { get; }

    public SpeakerStatus Status { get; }

    public SpeakerClient Client { get; }

    public ISpeakerController Controller { get; }

    public PlaybackState State
    {
        get
        {
            lock (_gate)
            {
                return _state;
            }
        }
    }

    public string? LeaderId
    {
        get
        {
            lock (_gate)
            {
                return _leaderId;
            }
        }
    }

    public IReadOnlyList<string> FollowerIds
    {
        get
        {
            lock (_gate)
            {
                return _followerIds;
            }
        }
    }

    public bool ReceivesEvents => Interlocked.Read(ref _notifyCount) > 0;

    public TimeSpan SinceLastSeen => TimeSpan.FromMilliseconds(Environment.TickCount64 - Interlocked.Read(ref _lastSeen));

    public event EventHandler<PlaybackState>? StateChanged;

    public event EventHandler? GroupChanged;

    public void Touch() => Interlocked.Exchange(ref _lastSeen, Environment.TickCount64);

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        await SafeAsync(() => RefreshStateAsync(cancellationToken), "initial state");
        await SafeAsync(() => RefreshGroupAsync(cancellationToken), "initial group");
        foreach (var service in EventServices)
        {
            _tasks.Add(Task.Run(() => RunSubscriptionAsync(service, _stop.Token)));
        }
        _tasks.Add(Task.Run(() => RunAsync(_stop.Token)));
    }

    public void Apply(Func<PlaybackState, PlaybackState> change)
    {
        PlaybackState next;
        lock (_gate)
        {
            next = change(_state);
            if (next == _state)
            {
                return;
            }
            _state = next;
        }
        try
        {
            StateChanged?.Invoke(this, next);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "StateChanged handler failed for {Speaker}", Info.Id);
        }
    }

    public async Task<PlaybackState> RefreshStateAsync(CancellationToken cancellationToken)
    {
        var reply = await Client.SoapAsync(SoapService.RenderTransport, "GetInfoEx", [("InstanceID", "0")], cancellationToken, TimeSpan.FromSeconds(5));
        Touch();
        var fresh = PlaybackMapper.FromGetInfoEx(reply, Info.IpAddress);
        Apply(_ => fresh);
        return State;
    }

    public async Task RefreshGroupAsync(CancellationToken cancellationToken)
    {
        var statusText = await Client.HttpGetAsync("getStatusEx", cancellationToken, TimeSpan.FromSeconds(8));
        Touch();
        var status = SpeakerStatus.Parse(statusText);
        if (status is null)
        {
            return;
        }
        string? leader = null;
        IReadOnlyList<string> followers = [];
        if (status.IsFollower)
        {
            leader = status.MasterUuid.Length > 0 && status.MasterUuid != Info.Id ? status.MasterUuid : null;
        }
        else
        {
            followers = ParseSlaveList(await Client.HttpGetAsync("multiroom:getSlaveList", cancellationToken, TimeSpan.FromSeconds(8)));
        }
        bool changed;
        lock (_gate)
        {
            changed = _leaderId != leader || !_followerIds.SequenceEqual(followers);
            _leaderId = leader;
            _followerIds = followers;
        }
        if (changed)
        {
            try
            {
                GroupChanged?.Invoke(this, EventArgs.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "GroupChanged handler failed for {Speaker}", Info.Id);
            }
        }
    }

    internal static IReadOnlyList<string> ParseSlaveList(string? json)
    {
        if (string.IsNullOrWhiteSpace(json))
        {
            return [];
        }
        try
        {
            using var document = JsonDocument.Parse(json);
            if (!document.RootElement.TryGetProperty("slave_list", out var list) || list.ValueKind != JsonValueKind.Array)
            {
                return [];
            }
            return [.. list.EnumerateArray()
                .Select(item => SpeakerIdentity.Normalize(SpeakerStatus.Text(item, "uuid")))
                .Where(id => id.Length > 0)];
        }
        catch (JsonException)
        {
            return [];
        }
    }

    public async ValueTask DisposeAsync()
    {
        await _stop.CancelAsync();
        try
        {
            await Task.WhenAll(_tasks).WaitAsync(TimeSpan.FromSeconds(5));
        }
        catch (Exception ex) when (ex is TimeoutException or OperationCanceledException)
        {
        }
        _stop.Dispose();
    }

    private void OnNotify(string lastChange)
    {
        Touch();
        Interlocked.Increment(ref _notifyCount);
        var delta = PlaybackMapper.ParseLastChange(lastChange, Info.IpAddress);
        if (delta is null)
        {
            return;
        }
        Apply(delta.ApplyTo);
        if (delta.GroupSignal)
        {
            Interlocked.Exchange(ref _groupDirty, 1);
        }
    }

    private async Task RunAsync(CancellationToken cancellationToken)
    {
        var lastReconcile = Environment.TickCount64;
        var tick = 0L;
        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                tick++;
                var due = Environment.TickCount64 - lastReconcile >= Reconcile.TotalMilliseconds;
                var withoutEvents = !ReceivesEvents;
                if (due || Interlocked.Exchange(ref _groupDirty, 0) == 1 || (withoutEvents && tick % 10 == 0))
                {
                    await SafeAsync(() => RefreshGroupAsync(cancellationToken), "group");
                }
                if (due || State.State == TransportState.Playing || (withoutEvents && tick % 2 == 0))
                {
                    await SafeAsync(() => RefreshStateAsync(cancellationToken), "state");
                }
                if (due)
                {
                    lastReconcile = Environment.TickCount64;
                }
                await Task.Delay(TimeSpan.FromSeconds(1), cancellationToken);
            }
            catch (OperationCanceledException)
            {
                return;
            }
        }
    }

    private async Task RunSubscriptionAsync(string service, CancellationToken cancellationToken)
    {
        string? sid = null;
        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                int timeout;
                if (sid is null)
                {
                    var callback = $"http://{NetworkInfo.LocalAddressFor(IPAddress.Parse(Info.IpAddress))}:{_eventPort}/Event";
                    (sid, timeout) = await Client.SubscribeAsync(service, callback, 1800, cancellationToken);
                    _router.Register(sid, OnNotify);
                }
                else
                {
                    (_, timeout) = await Client.RenewAsync(service, sid, 1800, cancellationToken);
                }
                Touch();
                await Task.Delay(TimeSpan.FromSeconds(timeout * 0.8), cancellationToken);
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (Exception ex)
            {
                _logger.LogDebug("Subscription {Service} on {Speaker} failed: {Message}", service, Info.Id, ex.Message);
                if (sid is not null)
                {
                    _router.Unregister(sid);
                    sid = null;
                }
                try
                {
                    await Task.Delay(TimeSpan.FromSeconds(10), cancellationToken);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
            }
        }
        if (sid is not null)
        {
            _router.Unregister(sid);
            try
            {
                await Client.UnsubscribeAsync(service, sid, CancellationToken.None);
            }
            catch (Exception ex)
            {
                _logger.LogDebug("Unsubscribe {Service} on {Speaker} failed: {Message}", service, Info.Id, ex.Message);
            }
        }
    }

    private async Task SafeAsync(Func<Task> action, string what)
    {
        try
        {
            await action();
        }
        catch (OperationCanceledException)
        {
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogDebug("Refresh {What} on {Speaker} failed: {Message}", what, Info.Id, ex.Message);
        }
    }
}
