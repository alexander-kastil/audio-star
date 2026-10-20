namespace AudioStar.Speakers.Tests;

internal static class LiveSamples
{
    public const string StatusJson = """
        { "language": "en_us", "ssid": "WiiM Amp-E6E8", "firmware": "Linkplay.5.2.830149", "build": "release", "project": "WiiM_Amp_4layer", "priv_prj": "WiiM_Amp_4layer", "group": "0", "wmrm_version": "4.3", "uuid": "FF98F2F7708C470F538415B3", "MAC": "40:FD:F3:95:E6:E8", "apcli0": "192.168.0.67", "capability": "0x20084808", "plm_support": "0x2b00416", "preset_key": "12", "upnp_uuid": "uuid:FF98F2F7-708C-470F-5384-15B3FF98F2F7", "security_capabilities": { "ver": "1.0", "aes_ver": "1.0" }, "app_timezone_id": "Europe\/Vienna", "udisk": "0", "DeviceName": "Wiim Audio", "GroupName": "Wiim Audio" }
        """;

    public const string ControlDeviceInfoXml = """
        <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>
        <u:GetControlDeviceInfoResponse xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1">
        <MultiType>1</MultiType>
        <Ssid>WiiM Amp-E6E8</Ssid>
        <CurrentVolume>33</CurrentVolume>
        <CurrentMute>0</CurrentMute>
        <Status>{ "language": "en_us", "project": "WiiM_Amp_4layer", "group": "0", "uuid": "FF98F2F7708C470F538415B3", "DeviceName": "Wiim Audio" }</Status>
        </u:GetControlDeviceInfoResponse>
        </s:Body> </s:Envelope>
        """;

    public const string NoMediaInfoExXml = """
        <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>
        <u:GetInfoExResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
        <CurrentTransportState>NO_MEDIA_PRESENT</CurrentTransportState>
        <CurrentTransportStatus>OK</CurrentTransportStatus>
        <CurrentSpeed>1</CurrentSpeed>
        <Track>0</Track>
        <TrackDuration>00:00:00</TrackDuration>
        <TrackMetaData></TrackMetaData>
        <TrackURI></TrackURI>
        <RelTime>00:00:00</RelTime>
        <AbsTime>NOT_IMPLEMENTED</AbsTime>
        <CurrentVolume>33</CurrentVolume>
        <CurrentMute>0</CurrentMute>
        <CurrentChannel>0</CurrentChannel>
        <LoopMode>3</LoopMode>
        <PlayType>-1</PlayType>
        <PlayMedium>NONE</PlayMedium>
        <TrackSource></TrackSource>
        </u:GetInfoExResponse>
        </s:Body> </s:Envelope>
        """;

    public const string KeyMappingEmptyXml = """
        <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>
        <u:GetKeyMappingResponse xmlns:u="urn:schemas-wiimu-com:service:PlayQueue:1">
        <QueueContext>&lt;?xml version=&quot;1.0&quot;?&gt;
        &lt;KeyList&gt;
        &lt;ListName&gt;KeyMappingQueue&lt;/ListName&gt;
        &lt;MaxNumber&gt;0&lt;/MaxNumber&gt;
        &lt;/KeyList&gt;
        </QueueContext>
        </u:GetKeyMappingResponse>
        </s:Body> </s:Envelope>
        """;

    public const string PlayingDidl = """
        <DIDL-Lite xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:song="www.linkplay.com/song/"><upnp:class>object.item.audioItem.musicTrack</upnp:class><item id="1"><dc:title>Teardrop</dc:title><upnp:artist>Massive Attack</upnp:artist><upnp:album>Mezzanine</upnp:album><upnp:albumArtURI>http://127.0.0.1:8080/cover.jpg</upnp:albumArtURI><song:rate_hz>44100</song:rate_hz><song:format_s>16</song:format_s><song:bitrate>1411</song:bitrate><res protocolInfo="http-get:*:audio/flac:*" duration="329000">http://192.168.0.10:22545/media/music/ab12</res></item></DIDL-Lite>
        """;
}
