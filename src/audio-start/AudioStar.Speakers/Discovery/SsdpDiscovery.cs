using System.Net.NetworkInformation;
using System.Net.Sockets;

namespace AudioStar.Speakers.Discovery;

internal sealed class SsdpDiscovery(ILogger<SsdpDiscovery> logger)
{
    private static readonly TimeSpan FastInterval = TimeSpan.FromSeconds(2);
    private static readonly TimeSpan SlowInterval = TimeSpan.FromSeconds(15);
    private static readonly TimeSpan FastPhase = TimeSpan.FromSeconds(20);
    private static readonly TimeSpan ReplyWindow = TimeSpan.FromSeconds(4);

    public async Task RunAsync(Func<SsdpReply, CancellationToken, Task> onReply, CancellationToken cancellationToken)
    {
        var started = DateTime.UtcNow;
        while (!cancellationToken.IsCancellationRequested)
        {
            _ = SearchOnceAsync(onReply, cancellationToken);
            var interval = DateTime.UtcNow - started < FastPhase ? FastInterval : SlowInterval;
            try
            {
                await Task.Delay(interval, cancellationToken);
            }
            catch (OperationCanceledException)
            {
                return;
            }
        }
    }

    public async Task SearchOnceAsync(Func<SsdpReply, CancellationToken, Task> onReply, CancellationToken cancellationToken)
    {
        var tasks = new List<Task>();
        foreach (var local in LocalAddresses())
        {
            tasks.Add(SearchOnInterfaceAsync(local, onReply, cancellationToken));
        }
        await Task.WhenAll(tasks);
    }

    private async Task SearchOnInterfaceAsync(IPAddress local, Func<SsdpReply, CancellationToken, Task> onReply, CancellationToken cancellationToken)
    {
        try
        {
            using var client = new UdpClient(new IPEndPoint(local, 0));
            client.Client.SetSocketOption(SocketOptionLevel.IP, SocketOptionName.MulticastInterface, local.GetAddressBytes());
            client.Client.SetSocketOption(SocketOptionLevel.IP, SocketOptionName.MulticastTimeToLive, 2);
            var payload = SsdpMessage.BuildSearch();
            await client.SendAsync(payload, new IPEndPoint(IPAddress.Parse(SsdpMessage.MulticastAddress), SsdpMessage.MulticastPort), cancellationToken);

            using var window = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
            window.CancelAfter(ReplyWindow);
            while (!window.IsCancellationRequested)
            {
                var received = await client.ReceiveAsync(window.Token);
                var reply = SsdpMessage.ParseReply(Encoding.ASCII.GetString(received.Buffer));
                if (reply is null)
                {
                    continue;
                }
                await onReply(reply, cancellationToken);
            }
        }
        catch (OperationCanceledException)
        {
        }
        catch (Exception ex) when (ex is SocketException or ObjectDisposedException or InvalidOperationException)
        {
            logger.LogDebug(ex, "SSDP search on {Address} failed", local);
        }
    }

    private static IEnumerable<IPAddress> LocalAddresses()
    {
        foreach (var nic in NetworkInterface.GetAllNetworkInterfaces())
        {
            if (nic.OperationalStatus != OperationalStatus.Up
                || !nic.SupportsMulticast
                || nic.NetworkInterfaceType is NetworkInterfaceType.Loopback or NetworkInterfaceType.Tunnel)
            {
                continue;
            }
            foreach (var unicast in nic.GetIPProperties().UnicastAddresses)
            {
                var address = unicast.Address;
                if (address.AddressFamily == AddressFamily.InterNetwork && !address.ToString().StartsWith("169.254.", StringComparison.Ordinal))
                {
                    yield return address;
                }
            }
        }
    }
}
