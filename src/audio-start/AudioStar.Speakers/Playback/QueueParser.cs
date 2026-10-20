using System.Globalization;
using AudioStar.Speakers.Events;

namespace AudioStar.Speakers.Playback;

internal static class QueueParser
{
    public static SpeakerQueue? Parse(string? queueXml, string deviceIp)
    {
        if (string.IsNullOrWhiteSpace(queueXml))
        {
            return null;
        }
        XDocument document;
        try
        {
            document = XDocument.Parse(queueXml);
        }
        catch (System.Xml.XmlException)
        {
            return null;
        }

        string Text(string name) => document.Descendants().FirstOrDefault(e => e.Name.LocalName == name)?.Value.Trim() ?? "";

        var tracksElement = document.Descendants().FirstOrDefault(e => e.Name.LocalName == "Tracks");
        var tracks = new List<QueueTrack>();
        var position = -1;
        foreach (var track in tracksElement?.Elements() ?? [])
        {
            position++;
            var item = DidlParser.ParseItem(track.Elements().FirstOrDefault(e => e.Name.LocalName == "Metadata")?.Value);
            var id = track.Elements().FirstOrDefault(e => e.Name.LocalName == "Id")?.Value ?? "";
            var songId = item is null ? "" : (item.Element(DidlParser.Song + "id")?.Value ?? "");
            if (string.IsNullOrWhiteSpace(id) && string.IsNullOrWhiteSpace(songId))
            {
                continue;
            }
            var title = item?.Element(DidlParser.Dc + "title")?.Value.Trim() ?? "";
            var res = item?.Elements().FirstOrDefault(e => e.Name.LocalName == "res");
            tracks.Add(new QueueTrack(
                position,
                title,
                NullIfEmpty(item?.Element(DidlParser.Upnp + "artist")?.Value),
                NullIfEmpty(item?.Element(DidlParser.Upnp + "album")?.Value),
                item is null ? null : DidlParser.ArtworkUri(item, deviceIp),
                res?.Attribute("duration")?.Value is { } duration && ClockText.ParseDidlDuration(duration) is { } parsed && parsed > TimeSpan.Zero ? parsed : null));
        }

        var current = int.TryParse(Text("LastPlayIndex"), NumberStyles.Integer, CultureInfo.InvariantCulture, out var last) ? Math.Max(0, last - 1) : 0;
        return new SpeakerQueue(Text("ListName"), NullIfEmpty(Text("SourceName")), current, tracks);
    }

    private static string? NullIfEmpty(string? value) => string.IsNullOrWhiteSpace(value) ? null : value.Trim();
}
