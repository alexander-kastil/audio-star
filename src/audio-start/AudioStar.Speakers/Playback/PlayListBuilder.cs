using AudioStar.Speakers.Protocol;

namespace AudioStar.Speakers.Playback;

internal static class PlayListBuilder
{
    private const string DidlHeader = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><DIDL-Lite xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:upnp=\"urn:schemas-upnp-org:metadata-1-0/upnp/\" xmlns:song=\"www.linkplay.com/song/\" xmlns:custom=\"www.linkplay.com/custom/\" xmlns=\"urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/\"><upnp:class>object.item.audioItem.musicTrack</upnp:class><item>";

    public const string LocalMusicSource = "PC_RemoteLocal";

    public static string Build(
        string listName,
        string sourceName,
        IReadOnlyList<PlayItem> items,
        Uri? pictureUri = null,
        bool radio = false,
        string? pcUuid = null)
    {
        var xml = new StringBuilder("<?xml version=\"1.0\"?><PlayList>");
        xml.Append("<ListName>").Append(XmlText.Escape(listName)).Append("</ListName>");
        xml.Append("<ListInfo>");
        xml.Append("<Radio>").Append(radio ? '1' : '0').Append("</Radio>");
        xml.Append("<SourceName>").Append(XmlText.Escape(sourceName)).Append("</SourceName>");
        xml.Append("<TrackNumber>").Append(items.Count).Append("</TrackNumber>");
        xml.Append("<SearchUrl></SearchUrl>");
        xml.Append("<Quality>0</Quality>");
        xml.Append("<PicUrl>").Append(XmlText.Escape(pictureUri?.ToString())).Append("</PicUrl>");
        xml.Append("<StartPlayIndex></StartPlayIndex>");
        xml.Append("</ListInfo>");
        xml.Append("<Tracks>");
        for (var i = 0; i < items.Count; i++)
        {
            var item = items[i];
            var url = item.StreamUri.ToString();
            xml.Append("<Track").Append(i + 1).Append('>');
            xml.Append("<URL>").Append(XmlText.Escape(url)).Append("</URL>");
            xml.Append("<Source>").Append(XmlText.Escape(sourceName)).Append("</Source>");
            xml.Append("<Id>").Append(XmlText.Escape(item.Id)).Append("</Id>");
            xml.Append("<Metadata>").Append(XmlText.Escape(BuildDidl(item, sourceName, pcUuid))).Append("</Metadata>");
            xml.Append("</Track").Append(i + 1).Append('>');
        }
        xml.Append("</Tracks></PlayList>");
        return xml.ToString();
    }

    public static string BuildDidl(PlayItem item, string sourceName, string? pcUuid)
    {
        var url = item.StreamUri.ToString();
        var didl = new StringBuilder(DidlHeader);
        if (sourceName == LocalMusicSource && !string.IsNullOrEmpty(pcUuid))
        {
            didl.Append("<custom:uuid>").Append(pcUuid).Append("</custom:uuid>");
        }
        didl.Append("<song:id>").Append(XmlText.Escape(item.Id)).Append("</song:id>");
        didl.Append("<song:albumid></song:albumid>");
        didl.Append("<song:singerid></song:singerid>");
        didl.Append("<dc:title>").Append(XmlText.Escape(item.Title)).Append("</dc:title>");
        didl.Append("<upnp:artist>").Append(XmlText.Escape(item.Artist)).Append("</upnp:artist>");
        didl.Append("<upnp:album>").Append(XmlText.Escape(item.Album)).Append("</upnp:album>");
        didl.Append("<res protocolInfo=\"").Append(MimeTypes.ProtocolInfo(item.StreamUri)).Append("\" duration=\"")
            .Append((long)(item.Duration?.TotalMilliseconds ?? 0)).Append("\">").Append(XmlText.Escape(url)).Append("</res>");
        didl.Append("<upnp:albumArtURI>").Append(XmlText.Escape(item.ArtworkUri?.ToString())).Append("</upnp:albumArtURI>");
        didl.Append("</item></DIDL-Lite>");
        return didl.ToString();
    }
}
