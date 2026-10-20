using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Text;
using AudioStar.Core;
using Microsoft.Extensions.Logging;

namespace AudioStar.Library.Dlna;

internal sealed class DlnaServer(IMediaServer mediaServer, DlnaHttp http, ILogger<DlnaServer> logger) : IDlnaServer
{
    private static readonly TimeSpan AliveInterval = TimeSpan.FromSeconds(MaxAgeHalf());

    private readonly SemaphoreSlim _gate = new(1, 1);
    private readonly int _bootId = (int)DateTimeOffset.UtcNow.ToUnixTimeSeconds();
    private CancellationTokenSource? _cts;
    private UdpClient? _listener;
    private Task? _listenTask;
    private Task? _aliveTask;

    public bool IsRunning { get; private set; }

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        await _gate.WaitAsync(cancellationToken);
        try
        {
            if (IsRunning)
            {
                return;
            }
            await mediaServer.StartAsync(cancellationToken);
            http.Enabled = true;
            _cts = new CancellationTokenSource();
            _listener = OpenListener();
            if (_listener is not null)
            {
                _listenTask = Task.Run(() => ListenAsync(_listener, _cts.Token));
            }
            _aliveTask = Task.Run(() => AliveLoopAsync(_cts.Token));
            IsRunning = true;
        }
        finally
        {
            _gate.Release();
        }
    }

    public async Task StopAsync(CancellationToken cancellationToken)
    {
        await _gate.WaitAsync(cancellationToken);
        try
        {
            if (!IsRunning)
            {
                return;
            }
            IsRunning = false;
            await SendNotifyAsync("ssdp:byebye");
            http.Enabled = false;
            _cts?.Cancel();
            _listener?.Dispose();
            await Task.WhenAll(new[] { _listenTask, _aliveTask }.OfType<Task>().Select(IgnoreAsync));
            _listener = null;
            _cts?.Dispose();
            _cts = null;
        }
        finally
        {
            _gate.Release();
        }
    }

    private UdpClient? OpenListener()
    {
        try
        {
            var client = new UdpClient(AddressFamily.InterNetwork);
            client.Client.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
            client.Client.Bind(new IPEndPoint(IPAddress.Any, SsdpMessages.Port));
            foreach (var address in LocalIPv4Addresses())
            {
                try
                {
                    client.Client.SetSocketOption(SocketOptionLevel.IP, SocketOptionName.AddMembership, new MulticastOption(SsdpMessages.MulticastAddress, address));
                }
                catch (SocketException ex)
                {
                    logger.LogDebug(ex, "Cannot join SSDP group on {Address}", address);
                }
            }
            return client;
        }
        catch (SocketException ex)
        {
            logger.LogWarning(ex, "Cannot listen on UDP {Port}; DLNA discovery replies are disabled", SsdpMessages.Port);
            return null;
        }
    }

    private async Task ListenAsync(UdpClient listener, CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested)
        {
            UdpReceiveResult received;
            try
            {
                received = await listener.ReceiveAsync(cancellationToken);
            }
            catch (Exception ex) when (ex is OperationCanceledException or ObjectDisposedException)
            {
                return;
            }
            catch (SocketException)
            {
                continue;
            }
            var message = SsdpMessages.Parse(Encoding.UTF8.GetString(received.Buffer));
            if (message is null || !SsdpMessages.IsMSearch(message))
            {
                continue;
            }
            var targets = SsdpMessages.MatchSearchTarget(message.Get("ST"), http.Udn);
            if (targets.Count == 0)
            {
                continue;
            }
            _ = ReplyAsync(listener, received.RemoteEndPoint, targets, message.Get("MX"), cancellationToken);
        }
    }

    private async Task ReplyAsync(UdpClient listener, IPEndPoint remote, IReadOnlyList<string> targets, string? mx, CancellationToken cancellationToken)
    {
        try
        {
            var wait = int.TryParse(mx, out var seconds) ? Math.Clamp(seconds, 1, 5) : 1;
            await Task.Delay(Random.Shared.Next(0, wait * 1000), cancellationToken);
            var location = LocationFor(NetworkInfo.LocalAddressFor(remote.Address));
            foreach (var target in targets)
            {
                var payload = SsdpMessages.BuildSearchResponse(target, http.Udn, location, _bootId);
                await listener.SendAsync(payload, remote, cancellationToken);
            }
        }
        catch (Exception ex) when (ex is OperationCanceledException or ObjectDisposedException or SocketException)
        {
        }
    }

    private async Task AliveLoopAsync(CancellationToken cancellationToken)
    {
        try
        {
            await SendNotifyAsync("ssdp:alive");
            using var timer = new PeriodicTimer(AliveInterval);
            while (await timer.WaitForNextTickAsync(cancellationToken))
            {
                await SendNotifyAsync("ssdp:alive");
            }
        }
        catch (OperationCanceledException)
        {
        }
    }

    private async Task SendNotifyAsync(string subtype)
    {
        foreach (var address in LocalIPv4Addresses())
        {
            try
            {
                using var sender = new UdpClient(new IPEndPoint(address, 0));
                sender.Client.SetSocketOption(SocketOptionLevel.IP, SocketOptionName.MulticastTimeToLive, 2);
                var location = LocationFor(address);
                foreach (var type in SsdpMessages.NotificationTypes(http.Udn))
                {
                    var payload = SsdpMessages.BuildNotify(type, subtype, http.Udn, location, _bootId);
                    await sender.SendAsync(payload, new IPEndPoint(SsdpMessages.MulticastAddress, SsdpMessages.Port));
                }
            }
            catch (SocketException ex)
            {
                logger.LogDebug(ex, "SSDP notify failed on {Address}", address);
            }
        }
    }

    private string LocationFor(IPAddress local) => $"http://{local}:{mediaServer.BaseUri.Port}{DlnaDescriptions.DescriptionPath}";

    private static IEnumerable<IPAddress> LocalIPv4Addresses() =>
        NetworkInterface.GetAllNetworkInterfaces()
            .Where(n => n.OperationalStatus == OperationalStatus.Up && n.SupportsMulticast && n.NetworkInterfaceType != NetworkInterfaceType.Loopback)
            .SelectMany(n => n.GetIPProperties().UnicastAddresses)
            .Select(a => a.Address)
            .Where(a => a.AddressFamily == AddressFamily.InterNetwork && !a.ToString().StartsWith("169.254", StringComparison.Ordinal));

    private static async Task IgnoreAsync(Task task)
    {
        try
        {
            await task;
        }
        catch (Exception ex) when (ex is OperationCanceledException or ObjectDisposedException)
        {
        }
    }

    private static double MaxAgeHalf() => SsdpMessages.MaxAgeSeconds / 2.0;
}
