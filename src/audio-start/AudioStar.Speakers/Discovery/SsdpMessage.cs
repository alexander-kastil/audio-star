namespace AudioStar.Speakers.Discovery;

internal sealed record SsdpReply(Uri Location, string? Usn, string? SearchTarget)
{
    public string Host => Location.Host;

    public int Port => Location.Port;
}

internal static class SsdpMessage
{
    public const string WiimDeviceTarget = "ssdp:wiimudevice";
    public const string MulticastAddress = "239.255.255.250";
    public const int MulticastPort = 1900;

    public static byte[] BuildSearch(string searchTarget = WiimDeviceTarget)
    {
        var text = "M-SEARCH * HTTP/1.1\r\n"
            + $"HOST: {MulticastAddress}:{MulticastPort}\r\n"
            + "MAN: \"ssdp:discover\"\r\n"
            + "MX: 3\r\n"
            + $"ST: {searchTarget}\r\n"
            + "USER-AGENT: mac/1.0 UPnP/1.1 upnpx/1.0\r\n"
            + "\r\n";
        return Encoding.ASCII.GetBytes(text);
    }

    public static SsdpReply? ParseReply(string text)
    {
        if (string.IsNullOrWhiteSpace(text))
        {
            return null;
        }
        var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        var lines = text.Split(["\r\n", "\n"], StringSplitOptions.None);
        if (lines.Length == 0 || !lines[0].StartsWith("HTTP/1.", StringComparison.OrdinalIgnoreCase) || !lines[0].Contains(" 200", StringComparison.Ordinal))
        {
            return null;
        }
        foreach (var line in lines.Skip(1))
        {
            var colon = line.IndexOf(':', StringComparison.Ordinal);
            if (colon <= 0)
            {
                continue;
            }
            headers.TryAdd(line[..colon].Trim(), line[(colon + 1)..].Trim());
        }
        if (!headers.TryGetValue("LOCATION", out var location) || !Uri.TryCreate(location, UriKind.Absolute, out var uri) || string.IsNullOrEmpty(uri.Host))
        {
            return null;
        }
        headers.TryGetValue("USN", out var usn);
        headers.TryGetValue("ST", out var st);
        return new SsdpReply(uri, usn, st);
    }

    public static string? UuidFromUsn(string? usn)
    {
        if (string.IsNullOrWhiteSpace(usn))
        {
            return null;
        }
        var start = usn.IndexOf("uuid:", StringComparison.OrdinalIgnoreCase);
        if (start < 0)
        {
            return null;
        }
        var rest = usn[(start + 5)..];
        var end = rest.IndexOf("::", StringComparison.Ordinal);
        return end >= 0 ? rest[..end] : rest;
    }
}
