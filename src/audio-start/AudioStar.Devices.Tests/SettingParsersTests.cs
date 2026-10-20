using AudioStar.Devices.Settings;
using FluentAssertions;

namespace AudioStar.Devices.Tests;

public class SettingParsersTests
{
    [Theory]
    [InlineData("Failed", false)]
    [InlineData("unknown command", false)]
    [InlineData("no parameters", false)]
    [InlineData("", false)]
    [InlineData("[]", false)]
    [InlineData("1", true)]
    [InlineData("[ { \"index\": 1 } ]", true)]
    public void GateAccepts_follows_the_wiim_home_checks(string reply, bool expected)
    {
        SettingParsers.GateAccepts(reply).Should().Be(expected);
    }

    [Theory]
    [InlineData("{\"FadeFeature\": 1}", "FadeFeature", "1")]
    [InlineData("{\"SyncPlayExtraDelay\":0.000}", "SyncPlayExtraDelay", "0")]
    [InlineData("{\"cross\":80.000000}", "cross", "80")]
    [InlineData("{\"delay_main_sub\":\"1.0\"}", "delay_main_sub", "1.0")]
    public void Key_reads_scalar_values(string reply, string key, string expected)
    {
        SettingParsers.Key(key)(reply).Should().Be(expected);
    }

    [Fact]
    public void NumberKey_normalizes_floats()
    {
        SettingParsers.NumberKey("delay_main_sub")("{\"delay_main_sub\":\"1.0\"}").Should().Be("1");
        SettingParsers.NumberKey("missing")("{\"a\":1}").Should().BeNull();
    }

    [Fact]
    public void Field_splits_capability_replies()
    {
        SettingParsers.Field(1)("48000:16:0").Should().Be("16");
        SettingParsers.Field(2)("48000:16:0").Should().Be("0");
        SettingParsers.Field(2)("48000:16").Should().BeNull();
    }

    [Fact]
    public void Prefixed_strips_the_alexa_hd_token()
    {
        SettingParsers.Prefixed("AvsMusicHDEnable:")("AvsMusicHDEnable:1").Should().Be("1");
        SettingParsers.Prefixed("AvsMusicHDEnable:")("Failed").Should().BeNull();
    }

    [Fact]
    public void Number_trims_and_normalizes()
    {
        SettingParsers.Number(" 0 \r\n").Should().Be("0");
        SettingParsers.Number("0.50").Should().Be("0.5");
    }

    [Fact]
    public void BluetoothDevices_reads_the_history_list()
    {
        var reply = "{ \"num\": 2, \"scan_status\": 0, \"list\": [ { \"name\": \"Buds\", \"ad\": \"11:22\", \"ct\": 1, \"role\": 0 }, { \"name\": \"\", \"ad\": \"33:44\" } ] }";

        var devices = SettingParsers.BluetoothDevices(reply);

        devices.Select(d => (d.Value, d.Label)).Should().Equal(("11:22", "Buds"), ("33:44", "33:44"));
    }

    [Fact]
    public void BluetoothDevices_reads_the_live_empty_reply()
    {
        SettingParsers.BluetoothDevices("{ \"num\": 0, \"scan_status\": 0 }").Should().BeEmpty();
    }

    [Fact]
    public void CastSpeakers_reads_outputs_or_a_bare_array()
    {
        SettingParsers.CastSpeakers("{\"outputs\":[{\"id\":\"a1\",\"name\":\"HomePod\",\"selected\":0}]}")
            .Should().ContainSingle().Which.Label.Should().Be("HomePod");
        SettingParsers.CastSpeakers("[{\"id\":\"a1\"}]").Should().ContainSingle().Which.Label.Should().Be("a1");
        SettingParsers.CastSpeakers("Failed").Should().BeEmpty();
    }

    [Fact]
    public void SoundCardModes_reads_the_live_support_list()
    {
        var reply = "[ { \"index\": 1, \"mode\": \"AUDIO_OUTPUT_SPEAKER_MODE\", \"soundCard\": { \"devName\": \"Speaker Out\", \"cardId\": \"hw:0,1\" } } ]";

        SettingParsers.SoundCardModes(reply).Should().ContainSingle().Which.Should().Be(new AudioStar.Core.SettingChoice("1", "Speaker Out"));
    }

    [Fact]
    public void IndexedList_reads_objects_and_scalars()
    {
        SettingParsers.IndexedList("[\"Fast\",\"Slow\"]", SettingParsers.FilterLabel)
            .Select(c => (c.Value, c.Label)).Should().Equal(("0", "Fast"), ("1", "Slow"));
        SettingParsers.IndexedList("[{\"index\":3,\"name\":\"Sharp\"}]", SettingParsers.FilterLabel)
            .Should().ContainSingle().Which.Should().Be(new AudioStar.Core.SettingChoice("3", "Sharp"));
        SettingParsers.IndexedList("no parameters", SettingParsers.FilterLabel).Should().BeEmpty();
    }

    [Theory]
    [InlineData("2000", "2 Vrms")]
    [InlineData("500mVrms", "500 mVrms")]
    public void VoltageLabel_formats_like_wiim_home(string value, string expected)
    {
        var entry = System.Text.Json.Nodes.JsonNode.Parse("{\"index\":1,\"value\":\"" + value + "\"}")!.AsObject();

        SettingParsers.VoltageLabel(entry).Should().Be(expected);
    }

    [Fact]
    public void CapCommand_replaces_one_field_and_keeps_the_others()
    {
        SettingsCatalog.CapCommand("setSpdifOutMaxCap", "48000:16:0", 3, 1, "24").Should().Be("setSpdifOutMaxCap:48000:24:0");
        SettingsCatalog.CapCommand("setAuxInMaxCap", "48000:16:0", 2, 0, "96000").Should().Be("setAuxInMaxCap:96000:16");
        SettingsCatalog.CapCommand("setCoaxOutMaxCap", "48000", 3, 2, "1").Should().Be("setCoaxOutMaxCap:48000:0:1");
    }

    [Fact]
    public void Hex_encodes_utf8()
    {
        SpeakerReply.Hex("Wiim Audio").Should().Be("5769696D20417564696F");
    }

    [Fact]
    public void Soap_envelope_names_the_rendering_control_action()
    {
        var envelope = RenderControlSoap.Envelope("AirplayAutoSyncDelay", "Name", "Start");

        envelope.Should().Contain("<u:AirplayAutoSyncDelay xmlns:u=\"urn:schemas-upnp-org:service:RenderingControl:1\"><Name>Start</Name></u:AirplayAutoSyncDelay>");
    }
}
