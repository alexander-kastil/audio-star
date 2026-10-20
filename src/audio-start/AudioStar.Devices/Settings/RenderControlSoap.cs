using System.Text;
using AudioStar.Core;

namespace AudioStar.Devices.Settings;

internal static class RenderControlSoap
{
    private const string ServiceType = "urn:schemas-upnp-org:service:RenderingControl:1";

    private static readonly HttpClient Client = new() { Timeout = TimeSpan.FromSeconds(15) };

    public static string Envelope(string action, string name, string value)
    {
        return "<?xml version=\"1.0\"?>"
            + "<s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\">"
            + $"<s:Body><u:{action} xmlns:u=\"{ServiceType}\"><{name}>{value}</{name}></u:{action}></s:Body></s:Envelope>";
    }

    public static async Task StartAutoSyncAsync(SpeakerInfo speaker, CancellationToken cancellationToken)
    {
        using var request = new HttpRequestMessage(HttpMethod.Post, $"http://{speaker.IpAddress}:{speaker.UpnpPort}/upnp/control/rendercontrol1")
        {
            Content = new StringContent(Envelope("AirplayAutoSyncDelay", "Name", "Start"), Encoding.UTF8, "text/xml"),
        };
        request.Headers.TryAddWithoutValidation("SOAPACTION", $"\"{ServiceType}#AirplayAutoSyncDelay\"");
        using var response = await Client.SendAsync(request, cancellationToken);
        response.EnsureSuccessStatusCode();
    }
}
