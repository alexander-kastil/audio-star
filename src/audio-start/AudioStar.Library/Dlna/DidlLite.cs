using System.Globalization;
using System.Xml.Linq;
using AudioStar.Core;

namespace AudioStar.Library.Dlna;

internal sealed record DidlObject(
    string Id,
    string ParentId,
    string Title,
    bool IsContainer,
    string UpnpClass,
    int? ChildCount = null,
    string? Artist = null,
    string? Album = null,
    int? TrackNumber = null,
    Uri? Resource = null,
    string? MimeType = null,
    long? Size = null,
    Uri? Artwork = null,
    TimeSpan? Duration = null);

internal static class DidlLite
{
    public const string ContainerClass = "object.container";
    public const string AlbumClass = "object.container.album.musicAlbum";
    public const string ArtistClass = "object.container.person.musicArtist";
    public const string GenreClass = "object.container.genre.musicGenre";
    public const string StorageFolderClass = "object.container.storageFolder";
    public const string TrackClass = "object.item.audioItem.musicTrack";

    private static readonly XNamespace Didl = "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/";
    private static readonly XNamespace Dc = "http://purl.org/dc/elements/1.1/";
    private static readonly XNamespace Upnp = "urn:schemas-upnp-org:metadata-1-0/upnp/";

    public static string Build(IEnumerable<DidlObject> objects)
    {
        var root = new XElement(
            Didl + "DIDL-Lite",
            new XAttribute(XNamespace.Xmlns + "dc", Dc.NamespaceName),
            new XAttribute(XNamespace.Xmlns + "upnp", Upnp.NamespaceName));
        foreach (var item in objects)
        {
            root.Add(item.IsContainer ? BuildContainer(item) : BuildItem(item));
        }
        return root.ToString(SaveOptions.DisableFormatting);
    }

    public static IReadOnlyList<DlnaItem> Parse(string xml)
    {
        if (string.IsNullOrWhiteSpace(xml))
        {
            return [];
        }
        var root = XDocument.Parse(xml).Root;
        if (root is null)
        {
            return [];
        }
        var result = new List<DlnaItem>();
        foreach (var element in root.Elements().Where(e => e.Name.LocalName is "container" or "item"))
        {
            var isContainer = element.Name.LocalName == "container";
            var resources = element.Elements().Where(e => e.Name.LocalName == "res").ToList();
            var audio = resources.FirstOrDefault(r => ((string?)r.Attribute("protocolInfo"))?.Contains(":audio/", StringComparison.OrdinalIgnoreCase) == true) ?? resources.FirstOrDefault();
            result.Add(new DlnaItem(
                (string?)element.Attribute("id") ?? "",
                (string?)element.Attribute("parentID") ?? "",
                Child(element, "title") ?? "",
                isContainer,
                Child(element, "artist") ?? Child(element, "creator"),
                Child(element, "album"),
                audio is null ? null : ToUri(audio.Value),
                ToUri(Child(element, "albumArtURI")),
                audio is null ? null : ParseDuration((string?)audio.Attribute("duration"))));
        }
        return result;
    }

    public static string FormatDuration(TimeSpan duration) =>
        string.Create(CultureInfo.InvariantCulture, $"{(int)duration.TotalHours}:{duration.Minutes:00}:{duration.Seconds:00}.{duration.Milliseconds:000}");

    public static TimeSpan? ParseDuration(string? value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            return null;
        }
        var parts = value.Split(':');
        if (parts.Length != 3 || !int.TryParse(parts[0], out var hours) || !int.TryParse(parts[1], out var minutes) || !double.TryParse(parts[2], NumberStyles.Float, CultureInfo.InvariantCulture, out var seconds))
        {
            return null;
        }
        return new TimeSpan(0, hours, minutes, 0) + TimeSpan.FromSeconds(seconds);
    }

    private static XElement BuildContainer(DidlObject item)
    {
        var element = new XElement(
            Didl + "container",
            new XAttribute("id", item.Id),
            new XAttribute("parentID", item.ParentId),
            new XAttribute("restricted", "1"),
            new XAttribute("searchable", "0"));
        if (item.ChildCount is not null)
        {
            element.SetAttributeValue("childCount", item.ChildCount.Value);
        }
        element.Add(new XElement(Dc + "title", item.Title), new XElement(Upnp + "class", item.UpnpClass));
        if (item.Artist is not null)
        {
            element.Add(new XElement(Upnp + "artist", item.Artist));
        }
        if (item.Artwork is not null)
        {
            element.Add(new XElement(Upnp + "albumArtURI", item.Artwork.AbsoluteUri));
        }
        return element;
    }

    private static XElement BuildItem(DidlObject item)
    {
        var element = new XElement(
            Didl + "item",
            new XAttribute("id", item.Id),
            new XAttribute("parentID", item.ParentId),
            new XAttribute("restricted", "1"),
            new XElement(Dc + "title", item.Title),
            new XElement(Upnp + "class", item.UpnpClass));
        if (item.Artist is not null)
        {
            element.Add(new XElement(Dc + "creator", item.Artist), new XElement(Upnp + "artist", item.Artist));
        }
        if (item.Album is not null)
        {
            element.Add(new XElement(Upnp + "album", item.Album));
        }
        if (item.TrackNumber is not null)
        {
            element.Add(new XElement(Upnp + "originalTrackNumber", item.TrackNumber.Value));
        }
        if (item.Artwork is not null)
        {
            element.Add(new XElement(Upnp + "albumArtURI", item.Artwork.AbsoluteUri));
        }
        if (item.Resource is not null)
        {
            var res = new XElement(Didl + "res", new XAttribute("protocolInfo", $"http-get:*:{item.MimeType ?? "audio/mpeg"}:*"), item.Resource.AbsoluteUri);
            if (item.Size is not null)
            {
                res.SetAttributeValue("size", item.Size.Value);
            }
            if (item.Duration is not null)
            {
                res.SetAttributeValue("duration", FormatDuration(item.Duration.Value));
            }
            element.Add(res);
        }
        return element;
    }

    private static string? Child(XElement element, string localName) => element.Elements().FirstOrDefault(e => e.Name.LocalName == localName)?.Value;

    private static Uri? ToUri(string? value) => Uri.TryCreate(value?.Trim(), UriKind.Absolute, out var uri) ? uri : null;
}
