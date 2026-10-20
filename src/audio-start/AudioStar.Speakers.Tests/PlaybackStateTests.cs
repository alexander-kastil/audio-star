using System.Xml.Linq;
using AudioStar.Core;
using AudioStar.Speakers.Events;
using AudioStar.Speakers.Protocol;
using FluentAssertions;

namespace AudioStar.Speakers.Tests;

public class PlaybackStateTests
{
    private const string DeviceIp = "192.168.0.67";

    [Fact]
    public void GetInfoEx_LiveNoMediaSample_MapsToIdleState()
    {
        var reply = SoapEnvelope.ParseResponse(LiveSamples.NoMediaInfoExXml);

        var state = PlaybackMapper.FromGetInfoEx(reply, DeviceIp);

        state.State.Should().Be(TransportState.NoMedia);
        state.Track.Should().BeNull();
        state.Volume.Should().Be(33);
        state.Muted.Should().BeFalse();
        state.LoopMode.Should().Be(LoopMode.Shuffle);
        state.PlayMedium.Should().Be("NONE");
        state.TrackSource.Should().BeNull();
        state.Position.Should().Be(TimeSpan.Zero);
    }

    [Fact]
    public void GetInfoEx_PlayingReply_ParsesDidlAndPosition()
    {
        var reply = new Dictionary<string, string>
        {
            ["CurrentTransportState"] = "PLAYING",
            ["TrackDuration"] = "00:05:29",
            ["TrackMetaData"] = LiveSamples.PlayingDidl,
            ["TrackURI"] = "http://192.168.0.10:22545/media/music/ab12",
            ["RelTime"] = "00:01:05",
            ["CurrentVolume"] = "40",
            ["CurrentMute"] = "1",
            ["LoopMode"] = "1",
            ["TrackSource"] = "PC_RemoteLocal",
            ["PlayMedium"] = "SONGLIST-NETWORK"
        };

        var state = PlaybackMapper.FromGetInfoEx(reply, DeviceIp);

        state.State.Should().Be(TransportState.Playing);
        state.Position.Should().Be(TimeSpan.FromSeconds(65));
        state.Volume.Should().Be(40);
        state.Muted.Should().BeTrue();
        state.LoopMode.Should().Be(LoopMode.SingleRepeat);
        state.TrackSource.Should().Be("PC_RemoteLocal");
        state.PlayMedium.Should().Be("SONGLIST-NETWORK");
        state.Track.Should().NotBeNull();
        state.Track!.Title.Should().Be("Teardrop");
        state.Track.Artist.Should().Be("Massive Attack");
        state.Track.Album.Should().Be("Mezzanine");
        state.Track.Duration.Should().Be(TimeSpan.FromMilliseconds(329000));
        state.Track.BitDepth.Should().Be(16);
        state.Track.SampleRateHz.Should().Be(44100);
        state.Track.BitrateKbps.Should().Be(1411);
        state.Track.ArtworkUri.Should().Be(new Uri("http://192.168.0.67:8080/cover.jpg"));
        state.Track.TrackUri.Should().Be("http://192.168.0.10:22545/media/music/ab12");
    }

    [Fact]
    public void LastChange_CraftedTransportEvent_ProducesDelta()
    {
        var lastChange = new XElement(
            "Event",
            new XElement(
                "InstanceID",
                new XAttribute("val", "0"),
                new XElement("TransportState", new XAttribute("val", "PLAYING")),
                new XElement("CurrentTrackMetaData", new XAttribute("val", LiveSamples.PlayingDidl)),
                new XElement("CurrentTrackURI", new XAttribute("val", "http://192.168.0.10:22545/media/music/ab12")),
                new XElement("TrackSource", new XAttribute("val", "PC_RemoteLocal")),
                new XElement("PlaybackStorageMedium", new XAttribute("val", "SONGLIST-NETWORK")),
                new XElement("Volume", new XAttribute("val", "27.0")),
                new XElement("Mute", new XAttribute("val", "0")),
                new XElement("LoopMode", new XAttribute("val", "2")))).ToString();

        var delta = PlaybackMapper.ParseLastChange(lastChange, DeviceIp);

        delta.Should().NotBeNull();
        delta!.State.Should().Be(TransportState.Playing);
        delta.Track!.Title.Should().Be("Teardrop");
        delta.Volume.Should().Be(27);
        delta.Muted.Should().BeFalse();
        delta.LoopMode.Should().Be(LoopMode.RepeatShuffle);
        delta.TrackSource.Should().Be("PC_RemoteLocal");
        delta.PlayMedium.Should().Be("SONGLIST-NETWORK");
        delta.GroupSignal.Should().BeFalse();

        var merged = delta.ApplyTo(PlaybackState.Empty);
        merged.State.Should().Be(TransportState.Playing);
        merged.Track!.TrackUri.Should().Be("http://192.168.0.10:22545/media/music/ab12");
        merged.Volume.Should().Be(27);
    }

    [Fact]
    public void LastChange_PartialEvent_KeepsExistingValues()
    {
        var before = new PlaybackState(TransportState.Playing, new TrackInfo("T", null, null, null, TimeSpan.FromMinutes(3), null, null, null, "u"), TimeSpan.FromSeconds(10), 30, false, LoopMode.Default, "src", "SONGLIST-NETWORK");
        var delta = PlaybackMapper.ParseLastChange("""<Event><InstanceID val="0"><Volume val="55"/></InstanceID></Event>""", DeviceIp)!;

        var after = delta.ApplyTo(before);

        after.Volume.Should().Be(55);
        after.State.Should().Be(TransportState.Playing);
        after.Track.Should().Be(before.Track);
        after.Position.Should().Be(TimeSpan.FromSeconds(10));
    }

    [Fact]
    public void LastChange_NoMedia_ClearsTrackAndPosition()
    {
        var before = new PlaybackState(TransportState.Playing, new TrackInfo("T", null, null, null, TimeSpan.Zero, null, null, null, null), TimeSpan.FromSeconds(10), 30, false, LoopMode.Default, null, null);
        var delta = PlaybackMapper.ParseLastChange("""<Event><InstanceID val="0"><TransportState val="NO_MEDIA_PRESENT"/></InstanceID></Event>""", DeviceIp)!;

        var after = delta.ApplyTo(before);

        after.State.Should().Be(TransportState.NoMedia);
        after.Track.Should().BeNull();
        after.Position.Should().Be(TimeSpan.Zero);
    }

    [Theory]
    [InlineData("""<Event><InstanceID val="0"><Slave action="add" val="AAAA"/></InstanceID></Event>""")]
    [InlineData("""<Event><InstanceID val="0"><commonevent>{"lpmrm":{"x":1}}</commonevent></InstanceID></Event>""")]
    public void LastChange_SlaveOrMultiroomEvent_RaisesGroupSignal(string xml)
    {
        PlaybackMapper.ParseLastChange(xml, DeviceIp)!.GroupSignal.Should().BeTrue();
    }

    [Fact]
    public void LastChange_Garbage_ReturnsNull()
    {
        PlaybackMapper.ParseLastChange("not xml", DeviceIp).Should().BeNull();
        PlaybackMapper.ParseLastChange("", DeviceIp).Should().BeNull();
    }

    [Fact]
    public void NotifyBody_ExtractsEscapedLastChange()
    {
        var inner = """<Event><InstanceID val="0"><Volume val="12"/></InstanceID></Event>""";
        var body = new XElement(
            XName.Get("propertyset", "urn:schemas-upnp-org:event-1-0"),
            new XElement(XName.Get("property", "urn:schemas-upnp-org:event-1-0"), new XElement("LastChange", inner))).ToString();

        SpeakerEventListener.ExtractLastChanges(body).Should().ContainSingle().Which.Should().Be(inner);
    }

    [Fact]
    public void Router_ReplaysEventsThatArrivedBeforeRegistration()
    {
        var router = new SpeakerEventRouter();
        var received = new List<string>();

        router.Dispatch("uuid:sid-1", "early");
        router.Register("uuid:sid-1", received.Add);
        router.Dispatch("uuid:sid-1", "late");

        received.Should().Equal("early", "late");
    }

    [Theory]
    [InlineData("PLAYING", TransportState.Playing)]
    [InlineData("PAUSED_PLAYBACK", TransportState.Paused)]
    [InlineData("STOPPED", TransportState.Stopped)]
    [InlineData("TRANSITIONING", TransportState.Transitioning)]
    [InlineData("NO_MEDIA_PRESENT", TransportState.NoMedia)]
    [InlineData("whatever", TransportState.Unknown)]
    public void TransportState_MapsUpnpValues(string text, TransportState expected)
    {
        PlaybackMapper.ParseTransportState(text).Should().Be(expected);
    }

    [Theory]
    [InlineData("00:03:21", 201)]
    [InlineData("0:03:21.500", 201.5)]
    [InlineData("25:00:00", 90000)]
    [InlineData("NOT_IMPLEMENTED", 0)]
    [InlineData("", 0)]
    public void ClockText_ParsesTimes(string text, double seconds)
    {
        ClockText.Parse(text).TotalSeconds.Should().Be(seconds);
    }

    [Fact]
    public void ClockText_FormatsSeekTargets()
    {
        ClockText.Format(TimeSpan.FromSeconds(3725)).Should().Be("01:02:05");
        ClockText.Format(TimeSpan.FromSeconds(-4)).Should().Be("00:00:00");
    }

    [Fact]
    public void ClockText_DidlDurationAcceptsMillisecondsAndClock()
    {
        ClockText.ParseDidlDuration("329000").Should().Be(TimeSpan.FromSeconds(329));
        ClockText.ParseDidlDuration("0:05:29").Should().Be(TimeSpan.FromSeconds(329));
    }
}
