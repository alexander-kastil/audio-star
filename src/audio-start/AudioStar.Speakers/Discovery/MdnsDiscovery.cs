using Zeroconf;

namespace AudioStar.Speakers.Discovery;

internal sealed class MdnsDiscovery(ILogger<MdnsDiscovery> logger)
{
    public const string ServiceType = "_linkplay._tcp.local.";

    private static readonly TimeSpan Interval = TimeSpan.FromSeconds(30);

    public async Task RunAsync(Func<string, CancellationToken, Task> onAddress, CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested)
        {
            await ScanOnceAsync(onAddress, cancellationToken);
            try
            {
                await Task.Delay(Interval, cancellationToken);
            }
            catch (OperationCanceledException)
            {
                return;
            }
        }
    }

    public async Task ScanOnceAsync(Func<string, CancellationToken, Task> onAddress, CancellationToken cancellationToken)
    {
        try
        {
            var hosts = await ZeroconfResolver.ResolveAsync(ServiceType, TimeSpan.FromSeconds(4), cancellationToken: cancellationToken);
            foreach (var host in hosts)
            {
                if (!string.IsNullOrEmpty(host.IPAddress))
                {
                    await onAddress(host.IPAddress, cancellationToken);
                }
            }
        }
        catch (OperationCanceledException)
        {
        }
        catch (Exception ex)
        {
            logger.LogDebug(ex, "mDNS scan failed");
        }
    }
}
