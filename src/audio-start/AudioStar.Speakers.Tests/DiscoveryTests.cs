using AudioStar.Speakers.Discovery;
using AudioStar.Speakers.Protocol;
using FluentAssertions;

namespace AudioStar.Speakers.Tests;

public class DiscoveryTests
{
    [Fact]
    public void BuildSearch_MatchesWiimHomeDatagram()
    {
        var text = System.Text.Encoding.ASCII.GetString(SsdpMessage.BuildSearch());

        text.Should().Be(
            "M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 3\r\nST: ssdp:wiimudevice\r\nUSER-AGENT: mac/1.0 UPnP/1.1 upnpx/1.0\r\n\r\n");
    }

    [Fact]
    public void ParseReply_ReadsLocationUsnAndTarget()
    {
        var reply = SsdpMessage.ParseReply(
            "HTTP/1.1 200 OK\r\nCACHE-CONTROL: max-age=100\r\nLocation: http://192.168.0.67:59152/description.xml\r\nST: ssdp:wiimudevice\r\nUSN: uuid:FF98F2F7-708C-470F-5384-15B3FF98F2F7::ssdp:wiimudevice\r\n\r\n");

        reply.Should().NotBeNull();
        reply!.Host.Should().Be("192.168.0.67");
        reply.Port.Should().Be(59152);
        reply.SearchTarget.Should().Be("ssdp:wiimudevice");
        SsdpMessage.UuidFromUsn(reply.Usn).Should().Be("FF98F2F7-708C-470F-5384-15B3FF98F2F7");
    }

    [Fact]
    public void ParseReply_IgnoresRepliesWithoutLocation()
    {
        SsdpMessage.ParseReply("HTTP/1.1 200 OK\r\nST: ssdp:wiimudevice\r\nUSN: uuid:abc\r\n\r\n").Should().BeNull();
    }

    [Fact]
    public void ParseReply_IgnoresNonReplies()
    {
        SsdpMessage.ParseReply("M-SEARCH * HTTP/1.1\r\nLOCATION: http://192.168.0.5/\r\n\r\n").Should().BeNull();
    }

    [Theory]
    [InlineData("uuid:FF98F2F7-708C-470F-5384-15B3FF98F2F7", "FF98F2F7708C470F538415B3")]
    [InlineData("FF98F2F7-708C-470F-5384-15B3FF98F2F7", "FF98F2F7708C470F538415B3")]
    [InlineData("FF98F2F7708C470F538415B3", "FF98F2F7708C470F538415B3")]
    [InlineData("ff98f2f7708c470f538415b3", "FF98F2F7708C470F538415B3")]
    [InlineData("FF98F2F7708C470F538415B3FF98F2F7", "FF98F2F7708C470F538415B3")]
    [InlineData("", "")]
    public void Normalize_ReducesUuidToTheStatusExId(string raw, string expected)
    {
        SpeakerIdentity.Normalize(raw).Should().Be(expected);
    }

    [Fact]
    public void Normalize_OfSsdpUuidEqualsGetStatusExUuid()
    {
        var fromSsdp = SpeakerIdentity.Normalize(SsdpMessage.UuidFromUsn("uuid:FF98F2F7-708C-470F-5384-15B3FF98F2F7::upnp:rootdevice"));
        var status = SpeakerStatus.Parse(LiveSamples.StatusJson);

        status.Should().NotBeNull();
        status!.Uuid.Should().Be("FF98F2F7708C470F538415B3");
        fromSsdp.Should().Be(status.Uuid);
    }

    [Fact]
    public void SpeakerStatus_ReadsTheLiveAmpFields()
    {
        var status = SpeakerStatus.Parse(LiveSamples.StatusJson)!;

        status.DeviceName.Should().Be("Wiim Audio");
        status.Project.Should().Be("WiiM_Amp_4layer");
        status.Firmware.Should().Be("Linkplay.5.2.830149");
        status.PlmSupport.Should().Be(0x2b00416);
        status.IsFollower.Should().BeFalse();
        ModelNames.Friendly(status.Project).Should().Be("WiiM Amp");
    }

    [Fact]
    public void SpeakerStatus_ReadsFollowerRelation()
    {
        var status = SpeakerStatus.Parse("""{ "uuid": "AAAA1111BBBB2222CCCC3333", "group": "1", "master_uuid": "uuid:FF98F2F7-708C-470F-5384-15B3FF98F2F7" }""")!;

        status.IsFollower.Should().BeTrue();
        status.MasterUuid.Should().Be("FF98F2F7708C470F538415B3");
    }

    [Fact]
    public void SpeakerStatus_RejectsJsonWithoutUuid()
    {
        SpeakerStatus.Parse("""{ "DeviceName": "x" }""").Should().BeNull();
        SpeakerStatus.Parse("Failed").Should().BeNull();
    }

    [Fact]
    public void ControlDeviceInfoReply_YieldsTheStatusJson()
    {
        var reply = SoapEnvelope.ParseResponse(LiveSamples.ControlDeviceInfoXml);

        reply["CurrentVolume"].Should().Be("33");
        SpeakerStatus.Parse(reply["Status"])!.Uuid.Should().Be("FF98F2F7708C470F538415B3");
    }

    [Fact]
    public void ParseSlaveList_ReadsFollowerUuids()
    {
        var json = """{ "slaves": 2, "wmrm_version": "4.3", "slave_list": [ { "name": "A", "uuid": "AAAA1111BBBB2222CCCC3333", "ip": "192.168.0.70" }, { "name": "B", "uuid": "uuid:BBBB1111-2222-3333-4444-5555BBBB1111" } ] }""";

        SpeakerSession.ParseSlaveList(json).Should().Equal("AAAA1111BBBB2222CCCC3333", "BBBB11112222333344445555");
        SpeakerSession.ParseSlaveList("""{ "slaves": 0, "group_type": -1 }""").Should().BeEmpty();
    }

    [Theory]
    [InlineData("Second-1800", 1800)]
    [InlineData("Second-infinite", 1800)]
    [InlineData("Second-300", 300)]
    [InlineData(null, 1800)]
    [InlineData("garbage", 1800)]
    public void ParseTimeout_ReadsTheSubscriptionLifetime(string? header, int expected)
    {
        SpeakerClient.ParseTimeout(header, 1800).Should().Be(expected);
    }
}
