using System.Net;
using System.Text;

namespace AudioStar.Library.Dlna;

internal sealed record SsdpMessage(string StartLine, IReadOnlyDictionary<string, string> Headers)
{
    public string? Get(string name) => Headers.GetValueOrDefault(name);
}

internal static class SsdpMessages
{
    public const int Port = 1900;
    public const int MaxAgeSeconds = 900;
    public const string RootDevice = "upnp:rootdevice";
    public const string MediaServerType = "urn:schemas-upnp-org:device:MediaServer:1";
    public const string ContentDirectoryType = "urn:schemas-upnp-org:service:ContentDirectory:1";
    public static readonly IPAddress MulticastAddress = IPAddress.Parse("239.255.255.250");
    public static readonly string ServerString = "Windows/10 UPnP/1.0 AudioStar/1.0";

    public static SsdpMessage? Parse(string text)
    {
        var lines = text.Split("\r\n", StringSplitOptions.None);
        if (lines.Length == 0 || lines[0].Length == 0)
        {
            return null;
        }
        var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        foreach (var line in lines.Skip(1))
        {
            var colon = line.IndexOf(':');
            if (colon > 0)
            {
                headers[line[..colon].Trim()] = line[(colon + 1)..].Trim();
            }
        }
        return new SsdpMessage(lines[0].Trim(), headers);
    }

    public static bool IsMSearch(SsdpMessage message) => message.StartLine.StartsWith("M-SEARCH", StringComparison.OrdinalIgnoreCase);

    public static IReadOnlyList<string> NotificationTypes(string udn) => [udn, RootDevice, MediaServerType, ContentDirectoryType];

    public static IReadOnlyList<string> MatchSearchTarget(string? searchTarget, string udn)
    {
        var all = NotificationTypes(udn);
        if (string.IsNullOrWhiteSpace(searchTarget))
        {
            return [];
        }
        if (searchTarget.Trim().Equals("ssdp:all", StringComparison.OrdinalIgnoreCase))
        {
            return all;
        }
        return all.Where(t => t.Equals(searchTarget.Trim(), StringComparison.OrdinalIgnoreCase)).ToList();
    }

    public static string Usn(string udn, string notificationType) => notificationType == udn ? udn : $"{udn}::{notificationType}";

    public static byte[] BuildSearchResponse(string notificationType, string udn, string location, int bootId)
    {
        var text = "HTTP/1.1 200 OK\r\n" +
            $"CACHE-CONTROL: max-age={MaxAgeSeconds}\r\n" +
            "EXT:\r\n" +
            $"LOCATION: {location}\r\n" +
            $"SERVER: {ServerString}\r\n" +
            $"ST: {notificationType}\r\n" +
            $"USN: {Usn(udn, notificationType)}\r\n" +
            $"BOOTID.UPNP.ORG: {bootId}\r\n\r\n";
        return Encoding.UTF8.GetBytes(text);
    }

    public static byte[] BuildNotify(string notificationType, string subtype, string udn, string location, int bootId)
    {
        var text = "NOTIFY * HTTP/1.1\r\n" +
            $"HOST: {MulticastAddress}:{Port}\r\n" +
            $"CACHE-CONTROL: max-age={MaxAgeSeconds}\r\n" +
            (subtype == "ssdp:alive" ? $"LOCATION: {location}\r\n" : "") +
            $"SERVER: {ServerString}\r\n" +
            $"NT: {notificationType}\r\n" +
            $"NTS: {subtype}\r\n" +
            $"USN: {Usn(udn, notificationType)}\r\n" +
            $"BOOTID.UPNP.ORG: {bootId}\r\n\r\n";
        return Encoding.UTF8.GetBytes(text);
    }

    public static byte[] BuildSearch(string searchTarget, int maxWaitSeconds)
    {
        var text = "M-SEARCH * HTTP/1.1\r\n" +
            $"HOST: {MulticastAddress}:{Port}\r\n" +
            "MAN: \"ssdp:discover\"\r\n" +
            $"MX: {maxWaitSeconds}\r\n" +
            $"ST: {searchTarget}\r\n\r\n";
        return Encoding.UTF8.GetBytes(text);
    }
}
