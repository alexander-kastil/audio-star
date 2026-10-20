using System.Globalization;

namespace AudioStar.Speakers.Events;

internal static class DidlParser
{
    public static readonly XNamespace Dc = "http://purl.org/dc/elements/1.1/";
    public static readonly XNamespace Upnp = "urn:schemas-upnp-org:metadata-1-0/upnp/";
    public static readonly XNamespace Song = "www.linkplay.com/song/";

    public static XElement? ParseItem(string? didl)
    {
        if (string.IsNullOrWhiteSpace(didl))
        {
            return null;
        }
        var document = TryLoad(didl) ?? TryLoad(WebUtility.HtmlDecode(didl));
        return document?.Descendants().FirstOrDefault(e => e.Name.LocalName == "item");
    }

    public static TrackInfo? ParseTrack(string? didl, string? trackUri, string deviceIp)
    {
        var item = ParseItem(didl);
        if (item is null)
        {
            return null;
        }
        var artwork = ArtworkUri(item, deviceIp);
        var res = item.Elements().FirstOrDefault(e => e.Name.LocalName == "res");
        var uri = !string.IsNullOrWhiteSpace(trackUri) ? trackUri : res?.Value;
        return new TrackInfo(
            NullIfEmpty(Child(item, Dc + "title")),
            NullIfEmpty(Child(item, Upnp + "artist")),
            NullIfEmpty(Child(item, Upnp + "album")),
            artwork,
            ClockText.ParseDidlDuration(res?.Attribute("duration")?.Value),
            PositiveInt(Child(item, Song + "format_s")),
            PositiveDouble(Child(item, Song + "rate_hz")),
            PositiveDouble(Child(item, Song + "bitrate")),
            NullIfEmpty(uri));
    }

    public static Uri? ArtworkUri(XElement item, string deviceIp)
    {
        var local = Child(item, Upnp + "localAlbumArtURI");
        var remote = Child(item, Upnp + "albumArtURI");
        var chosen = local.StartsWith("http", StringComparison.OrdinalIgnoreCase) ? local : remote;
        if (!Uri.TryCreate(chosen, UriKind.Absolute, out var uri))
        {
            return null;
        }
        if (uri.Host == "127.0.0.1")
        {
            var builder = new UriBuilder(uri) { Host = deviceIp };
            return builder.Uri;
        }
        return uri;
    }

    private static XDocument? TryLoad(string text)
    {
        try
        {
            return XDocument.Parse(text);
        }
        catch (System.Xml.XmlException)
        {
            return null;
        }
    }

    private static string Child(XElement item, XName name) => item.Element(name)?.Value.Trim() ?? "";

    private static string? NullIfEmpty(string? value) => string.IsNullOrWhiteSpace(value) ? null : value;

    private static int? PositiveInt(string text)
    {
        return double.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out var value) && value > 0 ? (int)Math.Round(value) : null;
    }

    private static double? PositiveDouble(string text)
    {
        return double.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out var value) && value > 0 ? value : null;
    }
}
