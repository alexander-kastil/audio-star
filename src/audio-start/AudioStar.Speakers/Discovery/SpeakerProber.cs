using AudioStar.Speakers.Protocol;

namespace AudioStar.Speakers.Discovery;

internal sealed record ProbeResult(SpeakerInfo Info, SpeakerStatus Status);

internal sealed class SpeakerProber(IHttpClientFactory httpFactory, ILogger<SpeakerProber> logger)
{
    public const int DefaultUpnpPort = 59152;

    private static readonly TimeSpan ProbeTimeout = TimeSpan.FromSeconds(5);

    public async Task<ProbeResult?> ProbeAsync(string ip, int upnpPort, CancellationToken cancellationToken)
    {
        var client = new SpeakerClient(ip, upnpPort, httpFactory);
        try
        {
            var reply = await client.SoapAsync(
                SoapService.RenderControl,
                "GetControlDeviceInfo",
                [("InstanceID", "0")],
                cancellationToken,
                ProbeTimeout);
            var status = reply.TryGetValue("Status", out var json) ? SpeakerStatus.Parse(json) : null;
            if (status is null)
            {
                return null;
            }
            var name = status.DeviceName.Length > 0 ? status.DeviceName : ip;
            var info = new SpeakerInfo(status.Uuid, name, ip, upnpPort, ModelNames.Friendly(status.Project), status.Firmware);
            return new ProbeResult(info, status);
        }
        catch (Exception ex) when (ex is HttpRequestException or TimeoutException or SpeakerRequestException or System.Xml.XmlException)
        {
            logger.LogDebug("Probe of {Ip}:{Port} failed: {Message}", ip, upnpPort, ex.Message);
            return null;
        }
    }
}
