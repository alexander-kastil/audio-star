using System.Xml.Linq;
using AudioStar.Core;
using AudioStar.Speakers.Playback;
using AudioStar.Speakers.Protocol;
using FluentAssertions;

namespace AudioStar.Speakers.Tests;

public class PlayQueueTests
{
    private const string Didl = """
        <?xml version="1.0" encoding="UTF-8"?><DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:song="www.linkplay.com/song/" xmlns:custom="www.linkplay.com/custom/" xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"><upnp:class>object.item.audioItem.musicTrack</upnp:class><item><custom:uuid>pc-1</custom:uuid><song:id>42</song:id><song:albumid></song:albumid><song:singerid></song:singerid><dc:title>Song &amp; Co</dc:title><upnp:artist>Artist</upnp:artist><upnp:album>Album</upnp:album><res protocolInfo="http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;" duration="201000">http://192.168.0.10:22545/media/music/abcd</res><upnp:albumArtURI>http://192.168.0.10:22545/media/cover/abcd</upnp:albumArtURI></item></DIDL-Lite>
        """;

    private static PlayItem Item(string id = "42", string title = "Song & Co", string path = "/media/music/abcd") => new(
        id,
        title,
        "Artist",
        "Album",
        new Uri("http://192.168.0.10:22545" + path),
        new Uri("http://192.168.0.10:22545/media/cover/abcd"),
        TimeSpan.FromSeconds(201));

    private static string EscapeLikePython(string text) => text.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;");

    [Fact]
    public void PlayList_GoldenXml_MatchesLpPlayListGenerateXml()
    {
        var xml = PlayListBuilder.Build("My & List", "PC_RemoteLocal", [Item()], new Uri("http://192.168.0.10:22545/media/cover/list"), radio: false, pcUuid: "pc-1");

        var expected = "<?xml version=\"1.0\"?><PlayList>"
            + "<ListName>My &amp; List</ListName>"
            + "<ListInfo><Radio>0</Radio><SourceName>PC_RemoteLocal</SourceName><TrackNumber>1</TrackNumber><SearchUrl></SearchUrl><Quality>0</Quality><PicUrl>http://192.168.0.10:22545/media/cover/list</PicUrl><StartPlayIndex></StartPlayIndex></ListInfo>"
            + "<Tracks><Track1><URL>http://192.168.0.10:22545/media/music/abcd</URL><Source>PC_RemoteLocal</Source><Id>42</Id><Metadata>"
            + EscapeLikePython(Didl)
            + "</Metadata></Track1></Tracks></PlayList>";
        xml.Should().Be(expected);
    }

    [Fact]
    public void PlayList_MetadataUnescapesToTheDidl()
    {
        var xml = PlayListBuilder.Build("L", "PC_RemoteLocal", [Item(), Item("43", "Second", "/media/music/ef01")], null, false, "pc-1");

        var document = XDocument.Parse(xml);
        var tracks = document.Descendants("Tracks").Single().Elements().ToList();

        tracks.Select(t => t.Name.LocalName).Should().Equal("Track1", "Track2");
        tracks[0].Element("Metadata")!.Value.Should().Be(Didl);
        document.Descendants("TrackNumber").Single().Value.Should().Be("2");
        XDocument.Parse(tracks[1].Element("Metadata")!.Value).Descendants().Any(e => e.Name.LocalName == "title" && e.Value == "Second").Should().BeTrue();
    }

    [Fact]
    public void PlayList_RadioFlagAndNonLocalSource_OmitPcUuid()
    {
        var xml = PlayListBuilder.Build("Radio X", "WiiMRadio", [Item("u", "Radio X", "/live")], null, radio: true, pcUuid: "pc-1");

        xml.Should().Contain("<Radio>1</Radio>");
        xml.Should().Contain("<SourceName>WiiMRadio</SourceName>");
        xml.Should().NotContain("custom:uuid");
    }

    [Theory]
    [InlineData("/a/b.flac", "audio/flac", "http-get:*:audio/flac:DLNA.ORG_OP=01;")]
    [InlineData("/a/b.MP3", "audio/mpeg", "http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;")]
    [InlineData("/a/b.m4a", "audio/mp4", "http-get:*:audio/mp4:DLNA.ORG_OP=01;")]
    [InlineData("/media/music/6162", "audio/mpeg", "http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;")]
    public void MimeTypes_FollowTheStreamExtension(string path, string mime, string protocolInfo)
    {
        var uri = new Uri("http://h" + path);

        MimeTypes.For(uri).Should().Be(mime);
        MimeTypes.ProtocolInfo(uri).Should().Be(protocolInfo);
    }

    [Fact]
    public void FastPlay_SingleTrack_HasOnlyTheInitialQueue()
    {
        var plan = FastPlayPlanner.Plan(1, 0);

        plan.Initial.Should().Equal(0);
        plan.TailChunks.Should().BeEmpty();
        plan.HeadChunks.Should().BeEmpty();
    }

    [Fact]
    public void FastPlay_MiddleStart_SendsStartAndNextThenTailThenHead()
    {
        var plan = FastPlayPlanner.Plan(10, 3);

        plan.Initial.Should().Equal(3, 4);
        plan.TailChunks.Should().ContainSingle().Which.Should().Equal(5, 6, 7, 8, 9);
        plan.HeadChunks.Should().ContainSingle().Which.Should().Equal(0, 1, 2);
    }

    [Fact]
    public void FastPlay_LastTrack_StartsAloneAndPrependsTheHead()
    {
        var plan = FastPlayPlanner.Plan(4, 3);

        plan.Initial.Should().Equal(3);
        plan.TailChunks.Should().BeEmpty();
        plan.HeadChunks.Should().ContainSingle().Which.Should().Equal(0, 1, 2);
    }

    [Fact]
    public void FastPlay_LongListFromTheMiddle_CapsHeadAt250AndExtraAt500()
    {
        var plan = FastPlayPlanner.Plan(1000, 500);

        plan.Initial.Should().Equal(500, 501);
        plan.TailChunks.Select(c => c.Count).Should().Equal(50, 50, 50, 50, 50);
        plan.TailChunks[0][0].Should().Be(502);
        plan.TailChunks[^1][^1].Should().Be(751);
        plan.HeadChunks.Select(c => c.Count).Should().Equal(50, 50, 50, 50, 50);
        plan.HeadChunks[0][0].Should().Be(450);
        plan.HeadChunks[^1][0].Should().Be(250);
        plan.HeadChunks[^1][^1].Should().Be(299);
        (plan.TailChunks.Sum(c => c.Count) + plan.HeadChunks.Sum(c => c.Count)).Should().Be(500);
    }

    [Fact]
    public void FastPlay_LongListFromTheStart_AppendsAtMost500InChunksOf50()
    {
        var plan = FastPlayPlanner.Plan(1000, 0);

        plan.TailChunks.Should().HaveCount(10).And.OnlyContain(c => c.Count == 50);
        plan.HeadChunks.Should().BeEmpty();
    }

    [Fact]
    public void SoapEnvelope_CreateQueue_IsExactlyWhatTheSpeakerReceives()
    {
        var args = SpeakerController.CreateQueueArgs("<PlayList/>");

        var envelope = SoapEnvelope.Build(SoapService.PlayQueue, "CreateQueue", args);

        envelope.Should().Be(
            "<?xml version=\"1.0\" encoding=\"utf-8\"?><s:Envelope s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\" xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\"><s:Body><u:CreateQueue xmlns:u=\"urn:schemas-wiimu-com:service:PlayQueue:1\"><QueueContext>&lt;PlayList/&gt;</QueueContext><QueuePolicy>0</QueuePolicy></u:CreateQueue></s:Body></s:Envelope>");
        SoapEnvelope.SoapAction(SoapService.PlayQueue, "CreateQueue").Should().Be("\"urn:schemas-wiimu-com:service:PlayQueue:1#CreateQueue\"");
    }

    [Fact]
    public void SoapEnvelope_PlayQueueWithIndex_IsOneBasedAndNamedAfterTheList()
    {
        var envelope = SoapEnvelope.Build(SoapService.PlayQueue, "PlayQueueWithIndex", SpeakerController.PlayQueueWithIndexArgs("My & List", 1));

        envelope.Should().Be(
            "<?xml version=\"1.0\" encoding=\"utf-8\"?><s:Envelope s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\" xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\"><s:Body><u:PlayQueueWithIndex xmlns:u=\"urn:schemas-wiimu-com:service:PlayQueue:1\"><QueueName>My &amp; List</QueueName><Index>1</Index></u:PlayQueueWithIndex></s:Body></s:Envelope>");
    }

    [Fact]
    public void SoapEnvelope_Transport_UsesUpnpUrnAndEndpoint()
    {
        SoapService.RenderTransport.Endpoint.Should().Be("rendertransport1");
        SoapEnvelope.SoapAction(SoapService.RenderTransport, "Seek").Should().Be("\"urn:schemas-upnp-org:service:AVTransport:1#Seek\"");
        SoapEnvelope.Build(SoapService.RenderTransport, "Seek", ("InstanceID", "0"), ("Unit", "REL_TIME"), ("Target", "00:01:05"))
            .Should().Contain("<u:Seek xmlns:u=\"urn:schemas-upnp-org:service:AVTransport:1\"><InstanceID>0</InstanceID><Unit>REL_TIME</Unit><Target>00:01:05</Target></u:Seek>");
    }

    [Fact]
    public void BrowseQueue_ParsesNameIndexAndTracks()
    {
        var queue = QueueXml(
            ("1", "First", "A1", "Alb1", "201000"),
            ("2", "Second", "A2", "Alb2", "00:03:00"));

        var parsed = QueueParser.Parse(queue, "192.168.0.67");

        parsed.Should().NotBeNull();
        parsed!.Name.Should().Be("My List");
        parsed.SourceName.Should().Be("PC_RemoteLocal");
        parsed.CurrentIndex.Should().Be(1);
        parsed.Tracks.Should().HaveCount(2);
        parsed.Tracks[0].Should().Be(new QueueTrack(0, "First", "A1", "Alb1", new Uri("http://192.168.0.67/x"), TimeSpan.FromSeconds(201)));
        parsed.Tracks[1].Index.Should().Be(1);
        parsed.Tracks[1].Duration.Should().Be(TimeSpan.FromMinutes(3));
    }

    [Fact]
    public void BrowseQueue_EmptyOrInvalid_IsNull()
    {
        QueueParser.Parse("", "192.168.0.67").Should().BeNull();
        QueueParser.Parse("nope", "192.168.0.67").Should().BeNull();
    }

    [Fact]
    public void KeyMapping_LiveAmpReply_HasNoPresets()
    {
        var reply = SoapEnvelope.ParseResponse(LiveSamples.KeyMappingEmptyXml);

        var mapping = KeyMapping.Parse(reply["QueueContext"]);

        mapping.MaxNumber.Should().Be(0);
        mapping.Presets.Should().BeEmpty();
    }

    [Fact]
    public void KeyMapping_ParsesFilledAndEmptySlots()
    {
        const string xml = """
            <?xml version="1.0"?><KeyList><ListName>KeyMappingQueue</ListName><MaxNumber>3</MaxNumber>
            <Key1><Name>Jazz Radio_#~291</Name><Source>newTuneIn</Source><PicUrl>http://img/jazz.png</PicUrl></Key1>
            <Key2><RoutineId>Empty</RoutineId></Key2></KeyList>
            """;

        var presets = KeyMapping.Parse(xml).Presets;

        presets.Should().HaveCount(3);
        presets[0].Should().Be(new Preset(1, "Jazz Radio", "newTuneIn", new Uri("http://img/jazz.png"), false));
        presets[1].IsEmpty.Should().BeTrue();
        presets[2].IsEmpty.Should().BeTrue();
        presets[2].Number.Should().Be(3);
    }

    [Fact]
    public void KeyMapping_EditWritesAndClearsASlot()
    {
        const string xml = """<?xml version="1.0"?><KeyList><ListName>K</ListName><MaxNumber>2</MaxNumber><Key1><RoutineId>Empty</RoutineId></Key1><Key2><RoutineId>Empty</RoutineId></Key2></KeyList>""";

        var saved = KeyMapping.Edit(xml, 2, [new XElement("Name", "Mix"), new XElement("Source", "Qobuz"), new XElement("Metadata", "<DIDL-Lite/>")]);
        var parsed = KeyMapping.Parse(saved).Presets;

        parsed[0].IsEmpty.Should().BeTrue();
        parsed[1].Name.Should().Be("Mix");
        saved.Should().Contain("<Metadata>&lt;DIDL-Lite/&gt;</Metadata>");

        var cleared = KeyMapping.Parse(KeyMapping.Edit(saved, 2, KeyMapping.EmptyKeyContent())).Presets;
        cleared[1].IsEmpty.Should().BeTrue();
    }

    [Fact]
    public void Inputs_LiveAmp_ListsTheAmpInputsInWiimOrder()
    {
        var inputs = InputCatalog.Build("WiiM_Amp_4layer", 0x2b00416, false, "Failed");

        inputs.Select(i => i.Mode).Should().Equal("wifi", "bluetooth", "line-in", "optical", "HDMI");
        inputs.Select(i => i.Title).Should().Equal("Wi-Fi", "Bluetooth", "Line In", "Optical In", "TV");
    }

    [Fact]
    public void Inputs_ModeRenameOverridesLineInAndOptical()
    {
        var inputs = InputCatalog.Build("WiiM_Amp_4layer", 0x2b00416, false, """{"SPDIF-In":"Toslink","Line-In":"Turntable"}""");

        inputs.Single(i => i.Mode == "optical").Title.Should().Be("Toslink");
        inputs.Single(i => i.Mode == "line-in").Title.Should().Be("Turntable");
    }

    [Fact]
    public void Inputs_ProWithoutHdmi_OmitsUnsupportedInputs()
    {
        var inputs = InputCatalog.Build("WiiM_Pro_Plus", 0x16, false, null);

        inputs.Select(i => i.Mode).Should().Equal("wifi", "bluetooth", "line-in", "optical");
    }

    private static string QueueXml(params (string Id, string Title, string Artist, string Album, string Duration)[] tracks)
    {
        var tracksElement = new XElement("Tracks");
        for (var i = 0; i < tracks.Length; i++)
        {
            var (id, title, artist, album, duration) = tracks[i];
            var didl = new XElement(
                XName.Get("DIDL-Lite", "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"),
                new XElement(
                    XName.Get("item", "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"),
                    new XElement(XName.Get("title", "http://purl.org/dc/elements/1.1/"), title),
                    new XElement(XName.Get("artist", "urn:schemas-upnp-org:metadata-1-0/upnp/"), artist),
                    new XElement(XName.Get("album", "urn:schemas-upnp-org:metadata-1-0/upnp/"), album),
                    new XElement(XName.Get("albumArtURI", "urn:schemas-upnp-org:metadata-1-0/upnp/"), "http://127.0.0.1/x"),
                    new XElement(XName.Get("res", "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"), new XAttribute("duration", duration), "http://h/" + id)));
            tracksElement.Add(new XElement(
                "Track" + (i + 1),
                new XElement("Source", "PC_RemoteLocal"),
                new XElement("Id", id),
                new XElement("URL", "http://h/" + id),
                new XElement("Metadata", didl.ToString(SaveOptions.DisableFormatting))));
        }
        return new XElement(
            "PlayList",
            new XElement("ListName", "My List"),
            new XElement("ListInfo", new XElement("SourceName", "PC_RemoteLocal"), new XElement("TrackNumber", tracks.Length)),
            new XElement("QueueVersion", "3"),
            new XElement("LastPlayIndex", "2"),
            tracksElement).ToString(SaveOptions.DisableFormatting);
    }
}
