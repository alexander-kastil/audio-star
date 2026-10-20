using AudioStar.Core;
using AudioStar.Devices.Settings;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using NSubstitute;

namespace AudioStar.Devices.Tests;

public class DeviceSettingsServiceTests
{
    private static readonly SpeakerInfo Speaker = Fakes.Info("FF98F2F7708C470F538415B3", "Wiim Audio", "192.168.0.67");

    private readonly Dictionary<string, string> _replies = new()
    {
        ["getStatusEx"] = """{ "DeviceName": "Wiim Audio", "volume_control": "0", "max_volume": "100" }""",
        ["getPowerModeTime"] = """{"idleInterval":"120","standbyInterval":"120","sleepInterval":"60","poweroffInterval":"0","semiactiveInterval":"15"}""",
        ["getWlanBandConfig"] = "1",
        ["getNetworkPreferDNS"] = "8.8.8.8",
        ["getWlanRoamConfig"] = "0",
        ["getIPV6Enable"] = "1",
        ["getChannelBalance"] = "0",
        ["GetFadeFeature"] = """{"FadeFeature": 1}""",
        ["getChannelMode"] = "0",
        ["getSubLPF"] = """{"status":0,"delay_main_sub":"1.0","plugged":1,"output_mode":1,"cross":80.000000,"phase":0.000000,"level":0.000000,"mix_sub":1,"main_filter":1,"sub_filter":1,"sub_delay":0.000000,"linein_delay":0.00}""",
        ["GetSyncPlayExtraDelay"] = """{"SyncPlayExtraDelay":0.000}""",
        ["getAuxAutoSenseEnable"] = "0",
        ["getAuxInMaxCap"] = "48000:16:0",
        ["getSpdifOutMaxCap"] = "48000:16:0",
        ["getCoaxOutMaxCap"] = "44100:24:1",
        ["getSpdifOutSwitchDelayMs"] = "0",
        ["getOutputVoltage"] = "2",
        ["getAuxVoltageSupportList"] = "no parameters",
        ["getDigitalFilterTypeSupportList"] = "no parameters",
        ["getDigitalFilterType"] = "1",
        ["getSoundCardModeSupportList"] = """[ { "index": 1, "mode": "AUDIO_OUTPUT_SPEAKER_MODE", "soundCard": { "cardName": "AMLAUGESOUND", "devName": "Speaker Out", "cardId": "hw:0,1", "bitDepthSupportList": [ 16, 24, 32 ], "sampleRateSupportList": [ 44100, 48000 ], "supportDigitalFilter": 1 } } ]""",
        ["getActiveSoundCardOutputMode"] = """{"index":"1","mode":"AUDIO_OUTPUT_SPEAKER_MODE","cardId":"hw:0,1","devName":"Speaker Out","btSource":"0","audioCast":"0"}""",
        ["LED_SWITCH_GET"] = "1",
        ["getAlexaCountry"] = "Failed",
        ["alexaGetLanguage"] = "en-US",
        ["getAvsMusicHDEnable"] = "AvsMusicHDEnable:1",
        ["getbthistory"] = """{ "num": 0, "scan_status": 0 }""",
        ["getbtdiscoveryresult"] = """{ "num": 1, "scan_status": 1, "list": [ { "name": "Headphones", "ad": "aa:bb:cc:dd:ee:ff", "ct": 0, "role": 0 } ] }""",
        ["audio_cast:get_speaker_list"] = "Failed",
    };

    private readonly ISpeakerController _controller;
    private readonly DeviceSettingsService _service;
    private readonly List<string> _sent = [];

    public DeviceSettingsServiceTests()
    {
        _controller = Fakes.Controller(_replies);
        _controller.SendCommandAsync(Arg.Do<string>(c => _sent.Add(c)), Arg.Any<CancellationToken>())
            .Returns(call => Task.FromResult(_replies.TryGetValue(call.Arg<string>(), out var reply) ? reply : "OK"));
        _service = new DeviceSettingsService(Fakes.Hub(Fakes.Session(Speaker, _controller)), NullLogger<DeviceSettingsService>.Instance);
    }

    [Fact]
    public void Definitions_have_unique_keys_and_cover_every_category()
    {
        _service.Definitions.Select(d => d.Key).Should().OnlyHaveUniqueItems();
        var categories = new[]
        {
            SettingCategories.Device, SettingCategories.Network, SettingCategories.Sound, SettingCategories.Input,
            SettingCategories.Output, SettingCategories.Hardware, SettingCategories.Bluetooth, SettingCategories.Voice, SettingCategories.AudioCast,
        };
        _service.Definitions.Select(d => d.Category).Distinct().Should().BeEquivalentTo(categories);
    }

    [Fact]
    public void Factory_reset_carries_the_confirm_text()
    {
        _service.Definitions.Single(d => d.Key == "device.factoryReset").ConfirmText.Should().Be("Restore Factory Settings");
    }

    [Fact]
    public async Task ReadAsync_parses_the_device_category_from_live_replies()
    {
        var values = await _service.ReadAsync(Speaker, SettingCategories.Device);

        values["device.name"].Should().Be("Wiim Audio");
        values["device.standby"].Should().Be("120");
        values["device.reboot"].Should().BeNull();
        values.Should().ContainKey("device.factoryReset");
    }

    [Fact]
    public async Task ReadAsync_parses_network_toggles_and_dns()
    {
        var values = await _service.ReadAsync(Speaker, SettingCategories.Network);

        values["network.band5ghz"].Should().Be("1");
        values["network.roaming"].Should().Be("0");
        values["network.dns"].Should().Be("8.8.8.8");
        values["network.ipv6"].Should().Be("1");
    }

    [Fact]
    public async Task ReadAsync_parses_sound_values_and_normalizes_numbers()
    {
        var values = await _service.ReadAsync(Speaker, SettingCategories.Sound);

        values["sound.maxVolume"].Should().Be("100");
        values["sound.fixedVolume"].Should().Be("0");
        values["sound.balance"].Should().Be("0");
        values["sound.crossfade"].Should().Be("1");
        values["sound.channelMode"].Should().Be("0");
        values["sound.sub.cross"].Should().Be("80");
        values["sound.sub.status"].Should().Be("0");
        values["sound.syncDelay"].Should().Be("0");
        values.Should().ContainKey("sound.autoSyncStart");
    }

    [Fact]
    public async Task ReadAsync_omits_settings_the_speaker_does_not_support()
    {
        var values = await _service.ReadAsync(Speaker, SettingCategories.Sound);

        values.Should().NotContainKey("sound.digitalFilter");

        var voice = await _service.ReadAsync(Speaker, SettingCategories.Voice);
        voice.Should().NotContainKey("voice.alexaCountry");
        voice["voice.alexaLanguage"].Should().Be("en-US");
        voice["voice.musicHd"].Should().Be("1");

        var cast = await _service.ReadAsync(Speaker, SettingCategories.AudioCast);
        cast.Should().BeEmpty();
    }

    [Fact]
    public async Task ReadAsync_omits_the_voltage_when_the_support_list_is_missing()
    {
        var values = await _service.ReadAsync(Speaker, SettingCategories.Output);

        values.Should().NotContainKey("output.auxVoltage");
        values["output.mode"].Should().Be("1");
        values["output.spdifRate"].Should().Be("48000");
        values["output.spdifBits"].Should().Be("16");
        values["output.spdifFixed"].Should().Be("0");
        values["output.coaxRate"].Should().Be("44100");
        values["output.coaxBits"].Should().Be("24");
        values["output.coaxFixed"].Should().Be("1");
    }

    [Fact]
    public async Task ReadAsync_treats_an_unreachable_getter_as_unsupported()
    {
        _controller.SendCommandAsync("LED_SWITCH_GET", Arg.Any<CancellationToken>()).Returns<string>(_ => throw new HttpRequestException());

        var values = await _service.ReadAsync(Speaker, SettingCategories.Hardware);

        values.Should().NotContainKey("hardware.led");
    }

    [Fact]
    public async Task ReadAsync_shows_bluetooth_actions_when_the_history_getter_answers()
    {
        var values = await _service.ReadAsync(Speaker, SettingCategories.Bluetooth);

        values["bluetooth.history"].Should().Be("0");
        values.Keys.Should().Contain(["bluetooth.scan", "bluetooth.connect", "bluetooth.disconnect", "bluetooth.forget"]);
    }

    [Fact]
    public async Task GetChoices_lists_bluetooth_devices_from_scan_results()
    {
        var choices = await _service.GetChoicesAsync(Speaker, "bluetooth.connect");

        choices.Should().ContainSingle().Which.Should().Be(new SettingChoice("aa:bb:cc:dd:ee:ff", "Headphones"));
    }

    [Fact]
    public async Task GetChoices_lists_sound_card_modes()
    {
        var choices = await _service.GetChoicesAsync(Speaker, "output.mode");

        choices.Should().ContainSingle().Which.Should().Be(new SettingChoice("1", "Speaker Out"));
    }

    [Fact]
    public async Task GetChoices_for_standby_drops_never_on_the_amp()
    {
        var choices = await _service.GetChoicesAsync(Speaker, "device.standby");

        choices.Select(c => c.Value).Should().Equal("30", "120", "300", "900", "1800", "3600");
    }

    [Fact]
    public async Task GetChoices_for_standby_keeps_never_on_other_models()
    {
        var other = Fakes.Info("X", "Pro", "192.168.0.80", "WiiM Pro");
        var service = new DeviceSettingsService(Fakes.Hub(Fakes.Session(other, _controller)), NullLogger<DeviceSettingsService>.Instance);

        var choices = await service.GetChoicesAsync(other, "device.standby");

        choices.Select(c => c.Value).Should().EndWith("-1");
    }

    [Theory]
    [InlineData("device.name", "Küche", "setHexDeviceName:4BC3BC636865")]
    [InlineData("device.standby", "300", "setPowerModeTime:{\"idleInterval\":\"300\"}")]
    [InlineData("network.band5ghz", "1", "setWlanBandConfig:1")]
    [InlineData("network.roaming", "0", "setWlanRoamConfig:0")]
    [InlineData("network.dns", "1.1.1.1", "setNetworkPreferDNS:1.1.1.1")]
    [InlineData("network.ipv6", "true", "setIPV6Enable:1")]
    [InlineData("sound.maxVolume", "80", "setMaxVolume:80")]
    [InlineData("sound.maxVolume", "180", "setMaxVolume:100")]
    [InlineData("sound.fixedVolume", "1", "setVolumeControl:1")]
    [InlineData("sound.balance", "0.5", "setChannelBalance:0.50")]
    [InlineData("sound.balance", "-0.125", "setChannelBalance:-0.12")]
    [InlineData("sound.crossfade", "1", "SetFadeFeature:1")]
    [InlineData("sound.channelMode", "3", "setChannelMode:3")]
    [InlineData("sound.digitalFilter", "2", "setDigitalFilterType:2")]
    [InlineData("sound.sub.status", "1", "setSubLPF:status:1")]
    [InlineData("sound.sub.level", "-3", "setSubLPF:level:-3")]
    [InlineData("sound.sub.cross", "80.0", "setSubLPF:cross:80")]
    [InlineData("sound.sub.phase", "180", "setSubLPF:phase:180")]
    [InlineData("sound.sub.sub_delay", "20", "setSubLPF:sub_delay:20")]
    [InlineData("sound.syncDelay", "35", "SetSyncPlayExtraDelay:35")]
    [InlineData("output.spdifSwitchDelay", "100", "setSpdifOutSwitchDelayMs:100")]
    [InlineData("output.auxVoltage", "3", "setOutputVoltage:3")]
    [InlineData("input.auxAutoSense", "1", "setAuxAutoSenseEnable:1")]
    [InlineData("input.spdifAutoSense", "0", "setSpdifAutoSenseEnable:0")]
    [InlineData("input.perSourceVolume", "1", "setPlayModeVolumeEnable:1")]
    [InlineData("input.cec", "1", "setCecPowerCtrl:1")]
    [InlineData("input.phonoType", "1", "PHONO_MODE_SWITCH_SET:1")]
    [InlineData("hardware.led", "0", "LED_SWITCH_SET:0")]
    [InlineData("hardware.volumeLed", "1", "VOL_LED_SWITCH_SET:1")]
    [InlineData("hardware.buttons", "1", "Button_Enable_SET:1")]
    [InlineData("voice.alexaCountry", "AT", "setAlexaCountry:AT")]
    [InlineData("voice.alexaLanguage", "de-DE", "alexaSetLanguage:de-DE")]
    [InlineData("voice.musicHd", "1", "setAvsMusicHDEnable:1")]
    public async Task WriteAsync_sends_the_exact_command(string key, string value, string expected)
    {
        await _service.WriteAsync(Speaker, key, value);

        _sent.Should().Contain(expected);
    }

    [Theory]
    [InlineData("input.auxInRate", "96000", "setAuxInMaxCap:96000:16")]
    [InlineData("input.auxInBits", "32", "setAuxInMaxCap:48000:32")]
    [InlineData("output.spdifRate", "192000", "setSpdifOutMaxCap:192000:16:0")]
    [InlineData("output.spdifBits", "24", "setSpdifOutMaxCap:48000:24:0")]
    [InlineData("output.spdifFixed", "1", "setSpdifOutMaxCap:48000:16:1")]
    [InlineData("output.coaxBits", "16", "setCoaxOutMaxCap:44100:16:1")]
    [InlineData("output.coaxFixed", "0", "setCoaxOutMaxCap:44100:24:0")]
    public async Task WriteAsync_composes_capability_commands_from_the_current_value(string key, string value, string expected)
    {
        await _service.WriteAsync(Speaker, key, value);

        _sent.Should().Contain(expected);
    }

    [Fact]
    public async Task WriteAsync_for_the_output_mode_sends_the_sound_card_json()
    {
        await _service.WriteAsync(Speaker, "output.mode", "1");

        _sent.Should().Contain("setSoundCardOutputMode:{\"index\":1,\"mode\":\"AUDIO_OUTPUT_SPEAKER_MODE\",\"cardId\":\"hw:0,1\",\"devName\":\"Speaker Out\",\"devNameHex\":\"537065616B6572204F7574\"}");
    }

    [Fact]
    public async Task WriteAsync_rejects_an_unknown_output_mode()
    {
        var act = () => _service.WriteAsync(Speaker, "output.mode", "9");

        await act.Should().ThrowAsync<InvalidOperationException>();
    }

    [Fact]
    public async Task WriteAsync_throws_when_the_speaker_rejects_the_command()
    {
        _replies["setMaxVolume:50"] = "Failed";

        var act = () => _service.WriteAsync(Speaker, "sound.maxVolume", "50");

        await act.Should().ThrowAsync<InvalidOperationException>();
    }

    [Theory]
    [InlineData("device.reboot", null, "StartRebootTime:1")]
    [InlineData("device.factoryReset", null, "restoreToDefault")]
    [InlineData("bluetooth.scan", null, "startbtdiscovery:3")]
    [InlineData("bluetooth.scan", "5", "startbtdiscovery:5")]
    [InlineData("bluetooth.connect", "aa:bb", "connectbta2dpsynk:aa:bb")]
    [InlineData("bluetooth.disconnect", "aa:bb", "disconnectbta2dpsynk:aa:bb")]
    [InlineData("bluetooth.forget", "aa:bb", "delbthistory:aa:bb")]
    [InlineData("audiocast.enable", "spk1", "audio_cast:speaker_enable:spk1")]
    [InlineData("audiocast.disable", "spk1", "audio_cast:speaker_disable:spk1")]
    [InlineData("audiocast.password", "spk1\tsecret", "audio_cast:speaker_set_password:spk1:secret")]
    public async Task InvokeAsync_sends_the_exact_command(string key, string? argument, string expected)
    {
        await _service.InvokeAsync(Speaker, key, argument);

        _sent.Should().Contain(expected);
    }

    [Fact]
    public async Task WriteAsync_refuses_actions_and_InvokeAsync_refuses_settings()
    {
        var write = () => _service.WriteAsync(Speaker, "device.reboot", "1");
        var invoke = () => _service.InvokeAsync(Speaker, "device.name", "x");

        await write.Should().ThrowAsync<InvalidOperationException>();
        await invoke.Should().ThrowAsync<InvalidOperationException>();
    }

    [Fact]
    public async Task Unknown_keys_throw()
    {
        var act = () => _service.WriteAsync(Speaker, "nope", "1");

        await act.Should().ThrowAsync<KeyNotFoundException>();
    }
}
