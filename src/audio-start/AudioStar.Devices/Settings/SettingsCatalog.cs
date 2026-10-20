using System.Globalization;
using System.Text.Json.Nodes;
using AudioStar.Core;

namespace AudioStar.Devices.Settings;

internal static class SettingsCatalog
{
    public const string FactoryResetConfirmText = "Restore Factory Settings";
    public const string CastPasswordSeparator = "\t";

    private static readonly SettingChoice[] SampleRates =
    [
        new("44100", "44.1 kHz"),
        new("48000", "48 kHz"),
        new("96000", "96 kHz"),
        new("192000", "192 kHz"),
    ];

    private static readonly SettingChoice[] BitDepths = [new("16", "16 bits"), new("24", "24 bits")];

    private static readonly SettingChoice[] LineInBitDepths = [new("16", "16 bits"), new("32", "24 bits")];

    private static readonly SettingChoice[] StandbyTimes =
    [
        new("30", "30 seconds"),
        new("120", "2 minutes"),
        new("300", "5 minutes"),
        new("900", "15 minutes"),
        new("1800", "30 minutes"),
        new("3600", "1 hour"),
        new("-1", "Never"),
    ];

    private static readonly SettingChoice[] ChannelModes =
    [
        new("0", "Stereo"),
        new("3", "Mono"),
        new("1", "Left Channel"),
        new("2", "Right Channel"),
    ];

    private static readonly SettingChoice[] PhonoTypes = [new("0", "MM"), new("1", "MC")];

    private static readonly SettingChoice[] AlexaLanguages =
    [
        new("en-US", "English (United States)"),
        new("en-GB", "English (United Kingdom/Ireland)"),
        new("de-DE", "Deutsch (Deutschland/Österreich)"),
        new("en-CA", "English (Canada)"),
        new("ja-JP", "Japanese"),
        new("en-IN", "English (India)"),
        new("en-AU", "English (Australia/New Zealand)"),
        new("fr-FR", "French"),
        new("it-IT", "Italian"),
        new("es-MX", "Spanish (Mexico)"),
        new("es-ES", "Spanish"),
        new("fr-CA", "French (Canada)"),
        new("pt-BR", "Portuguese (Brazil)"),
        new("es-US", "Spanish (United States)"),
        new("hi-IN", "Hindi"),
    ];

    public static IReadOnlyList<SettingSpec> Build()
    {
        var specs = new List<SettingSpec>();
        AddDevice(specs);
        AddNetwork(specs);
        AddSound(specs);
        AddInput(specs);
        AddOutput(specs);
        AddHardware(specs);
        AddBluetooth(specs);
        AddVoice(specs);
        AddAudioCast(specs);
        return specs;
    }

    public static string ToggleValue(string? value)
    {
        return value is not null && (value == "1" || value.Equals("true", StringComparison.OrdinalIgnoreCase) || value.Equals("on", StringComparison.OrdinalIgnoreCase)) ? "1" : "0";
    }

    public static string SoundCardCommand(JsonObject entry)
    {
        var card = entry["soundCard"] as JsonObject;
        var devName = SpeakerReply.Scalar(card?["devName"]) ?? string.Empty;
        var payload = new JsonObject
        {
            ["index"] = entry["index"]?.DeepClone(),
            ["mode"] = entry["mode"]?.DeepClone(),
            ["cardId"] = card?["cardId"]?.DeepClone(),
            ["devName"] = devName,
            ["devNameHex"] = SpeakerReply.Hex(devName),
        };
        return $"setSoundCardOutputMode:{payload.ToJsonString()}";
    }

    public static string CapCommand(string setter, string currentReply, int fieldCount, int fieldIndex, string value)
    {
        var parts = currentReply.Trim().Split(':');
        var fields = new string[fieldCount];
        for (var i = 0; i < fieldCount; i++)
        {
            fields[i] = i < parts.Length ? parts[i] : "0";
        }

        fields[fieldIndex] = SpeakerReply.ToInt(value).ToString(CultureInfo.InvariantCulture);
        return $"{setter}:{string.Join(':', fields)}";
    }

    private static void AddDevice(List<SettingSpec> specs)
    {
        specs.Add(new SettingSpec(
            Def("device.name", SettingCategories.Device, "Device name", SettingKind.Text),
            "getStatusEx",
            SettingParsers.Key("DeviceName"),
            Execute: Simple(v => $"setHexDeviceName:{SpeakerReply.Hex(v)}")));
        specs.Add(new SettingSpec(
            Def("device.standby", SettingCategories.Device, "Standby time", SettingKind.Choice, StandbyTimes, dynamic: true),
            "getPowerModeTime",
            SettingParsers.NumberKey("idleInterval"),
            Execute: Simple(v => $"setPowerModeTime:{{\"idleInterval\":\"{SpeakerReply.ToInt(v)}\"}}"),
            Choices: execution => Task.FromResult<IReadOnlyList<SettingChoice>>(
                execution.Speaker.Model.Contains("Amp", StringComparison.OrdinalIgnoreCase)
                    ? StandbyTimes.Where(c => c.Value != "-1").ToList()
                    : StandbyTimes)));
        specs.Add(new SettingSpec(
            Def("device.reboot", SettingCategories.Device, "Reboot", SettingKind.Action),
            Execute: Action(_ => "StartRebootTime:1")));
        specs.Add(new SettingSpec(
            Def("device.factoryReset", SettingCategories.Device, "Factory reset", SettingKind.Action, confirmText: FactoryResetConfirmText),
            Execute: Action(_ => "restoreToDefault")));
    }

    private static void AddNetwork(List<SettingSpec> specs)
    {
        specs.Add(Toggle("network.band5ghz", SettingCategories.Network, "5 GHz band", "getWlanBandConfig", "setWlanBandConfig"));
        specs.Add(Toggle("network.roaming", SettingCategories.Network, "Wi-Fi roaming", "getWlanRoamConfig", "setWlanRoamConfig"));
        specs.Add(new SettingSpec(
            Def("network.dns", SettingCategories.Network, "Preferred DNS", SettingKind.Text),
            "getNetworkPreferDNS",
            SettingParsers.Raw,
            Execute: Simple(v => $"setNetworkPreferDNS:{v.Trim()}")));
        specs.Add(Toggle("network.ipv6", SettingCategories.Network, "IPv6", "getIPV6Enable", "setIPV6Enable"));
    }

    private static void AddSound(List<SettingSpec> specs)
    {
        specs.Add(new SettingSpec(
            Def("sound.maxVolume", SettingCategories.Sound, "Maximum volume", SettingKind.Number, min: 0, max: 100),
            "getStatusEx",
            SettingParsers.NumberKey("max_volume"),
            Execute: Simple(v => $"setMaxVolume:{Math.Clamp(SpeakerReply.ToInt(v), 0, 100)}")));
        specs.Add(new SettingSpec(
            Def("sound.fixedVolume", SettingCategories.Sound, "Fixed volume", SettingKind.Toggle),
            "getStatusEx",
            SettingParsers.Key("volume_control"),
            Execute: Simple(v => $"setVolumeControl:{ToggleValue(v)}")));
        specs.Add(new SettingSpec(
            Def("sound.balance", SettingCategories.Sound, "Balance", SettingKind.Number, min: -1, max: 1),
            "getChannelBalance",
            SettingParsers.Number,
            Execute: Simple(v => $"setChannelBalance:{double.Parse(v, NumberStyles.Float, CultureInfo.InvariantCulture).ToString("F2", CultureInfo.InvariantCulture)}")));
        specs.Add(new SettingSpec(
            Def("sound.crossfade", SettingCategories.Sound, "Crossfade", SettingKind.Toggle),
            "GetFadeFeature",
            SettingParsers.Key("FadeFeature"),
            Execute: Simple(v => $"SetFadeFeature:{ToggleValue(v)}")));
        specs.Add(new SettingSpec(
            Def("sound.channelMode", SettingCategories.Sound, "Channel mode", SettingKind.Choice, ChannelModes),
            "getChannelMode",
            SettingParsers.Number,
            Execute: Simple(v => $"setChannelMode:{SpeakerReply.ToInt(v)}")));
        specs.Add(new SettingSpec(
            Def("sound.digitalFilter", SettingCategories.Sound, "DAC digital filter", SettingKind.Choice, dynamic: true),
            "getDigitalFilterType",
            SettingParsers.Number,
            "getDigitalFilterTypeSupportList",
            Simple(v => $"setDigitalFilterType:{SpeakerReply.ToInt(v)}"),
            async execution => SettingParsers.IndexedList(await execution.SendAsync("getDigitalFilterTypeSupportList"), SettingParsers.FilterLabel)));
        AddSubwoofer(specs);
        specs.Add(new SettingSpec(
            Def("sound.syncDelay", SettingCategories.Sound, "Sync delay (ms)", SettingKind.Number),
            "GetSyncPlayExtraDelay",
            SettingParsers.NumberKey("SyncPlayExtraDelay"),
            Execute: Simple(v => $"SetSyncPlayExtraDelay:{SpeakerReply.ToInt(v)}")));
        specs.Add(new SettingSpec(
            Def("sound.autoSyncStart", SettingCategories.Sound, "Auto sync", SettingKind.Action),
            "GetSyncPlayExtraDelay",
            SettingParsers.Present,
            Execute: (execution, _) => RenderControlSoap.StartAutoSyncAsync(execution.Speaker, execution.CancellationToken)));
    }

    private static void AddSubwoofer(List<SettingSpec> specs)
    {
        specs.Add(SubwooferField("status", "Subwoofer output", SettingKind.Toggle));
        specs.Add(SubwooferField("level", "Subwoofer level", SettingKind.Number));
        specs.Add(SubwooferField("cross", "Subwoofer crossover (Hz)", SettingKind.Number));
        specs.Add(SubwooferField("phase", "Subwoofer phase", SettingKind.Number));
        specs.Add(SubwooferField("sub_delay", "Subwoofer delay (ms)", SettingKind.Number));
    }

    private static SettingSpec SubwooferField(string field, string label, SettingKind kind)
    {
        return new SettingSpec(
            Def($"sound.sub.{field}", SettingCategories.Sound, label, kind),
            "getSubLPF",
            SettingParsers.NumberKey(field),
            Execute: Simple(v => $"setSubLPF:{field}:{(kind == SettingKind.Toggle ? ToggleValue(v) : SpeakerReply.ToInt(v).ToString(CultureInfo.InvariantCulture))}"));
    }

    private static void AddInput(List<SettingSpec> specs)
    {
        specs.Add(Toggle("input.auxAutoSense", SettingCategories.Input, "Aux in auto sense", "getAuxAutoSenseEnable", "setAuxAutoSenseEnable"));
        specs.Add(Toggle("input.spdifAutoSense", SettingCategories.Input, "S/PDIF auto sense", "getSpdifAutoSenseEnable", "setSpdifAutoSenseEnable"));
        specs.Add(Toggle("input.perSourceVolume", SettingCategories.Input, "Volume per source", "getPlayModeVolumeEnable", "setPlayModeVolumeEnable"));
        specs.Add(Toggle("input.cec", SettingCategories.Input, "HDMI CEC power control", "getCecPowerCtrl", "setCecPowerCtrl"));
        specs.Add(new SettingSpec(
            Def("input.phonoType", SettingCategories.Input, "Phono type", SettingKind.Choice, PhonoTypes),
            "PHONO_MODE_SWITCH_GET",
            SettingParsers.Number,
            Execute: Simple(v => $"PHONO_MODE_SWITCH_SET:{SpeakerReply.ToInt(v)}")));
        specs.Add(Cap("input.auxInRate", SettingCategories.Input, "Aux in sample rate", SettingKind.Choice, SampleRates, "getAuxInMaxCap", "setAuxInMaxCap", 2, 0));
        specs.Add(Cap("input.auxInBits", SettingCategories.Input, "Aux in bit depth", SettingKind.Choice, LineInBitDepths, "getAuxInMaxCap", "setAuxInMaxCap", 2, 1));
    }

    private static void AddOutput(List<SettingSpec> specs)
    {
        specs.Add(new SettingSpec(
            Def("output.mode", SettingCategories.Output, "Audio output", SettingKind.Choice, dynamic: true),
            "getActiveSoundCardOutputMode",
            SettingParsers.Key("index"),
            "getSoundCardModeSupportList",
            async (execution, value) =>
            {
                var list = SpeakerReply.TryParse(await execution.SendAsync("getSoundCardModeSupportList")) as JsonArray;
                var entry = list?.OfType<JsonObject>().FirstOrDefault(e => SpeakerReply.Scalar(e["index"]) == value)
                    ?? throw new InvalidOperationException($"{execution.Speaker.Name} offers no output mode {value}.");
                await execution.SendAsync(SoundCardCommand(entry));
            },
            async execution => SettingParsers.SoundCardModes(await execution.SendAsync("getSoundCardModeSupportList"))));
        specs.Add(new SettingSpec(
            Def("output.spdifSwitchDelay", SettingCategories.Output, "S/PDIF switch delay (ms)", SettingKind.Number),
            "getSpdifOutSwitchDelayMs",
            SettingParsers.Number,
            Execute: Simple(v => $"setSpdifOutSwitchDelayMs:{SpeakerReply.ToInt(v)}")));
        specs.Add(new SettingSpec(
            Def("output.auxVoltage", SettingCategories.Output, "Aux out voltage", SettingKind.Choice, dynamic: true),
            "getOutputVoltage",
            SettingParsers.Number,
            "getAuxVoltageSupportList",
            Simple(v => $"setOutputVoltage:{SpeakerReply.ToInt(v)}"),
            async execution => SettingParsers.IndexedList(await execution.SendAsync("getAuxVoltageSupportList"), SettingParsers.VoltageLabel)));
        specs.Add(Cap("output.spdifRate", SettingCategories.Output, "S/PDIF max sample rate", SettingKind.Choice, SampleRates, "getSpdifOutMaxCap", "setSpdifOutMaxCap", 3, 0));
        specs.Add(Cap("output.spdifBits", SettingCategories.Output, "S/PDIF max bit depth", SettingKind.Choice, BitDepths, "getSpdifOutMaxCap", "setSpdifOutMaxCap", 3, 1));
        specs.Add(Cap("output.spdifFixed", SettingCategories.Output, "S/PDIF fixed resolution", SettingKind.Toggle, null, "getSpdifOutMaxCap", "setSpdifOutMaxCap", 3, 2));
        specs.Add(Cap("output.coaxRate", SettingCategories.Output, "Coax max sample rate", SettingKind.Choice, SampleRates, "getCoaxOutMaxCap", "setCoaxOutMaxCap", 3, 0));
        specs.Add(Cap("output.coaxBits", SettingCategories.Output, "Coax max bit depth", SettingKind.Choice, BitDepths, "getCoaxOutMaxCap", "setCoaxOutMaxCap", 3, 1));
        specs.Add(Cap("output.coaxFixed", SettingCategories.Output, "Coax fixed resolution", SettingKind.Toggle, null, "getCoaxOutMaxCap", "setCoaxOutMaxCap", 3, 2));
    }

    private static void AddHardware(List<SettingSpec> specs)
    {
        specs.Add(Toggle("hardware.led", SettingCategories.Hardware, "Status LED", "LED_SWITCH_GET", "LED_SWITCH_SET"));
        specs.Add(Toggle("hardware.volumeLed", SettingCategories.Hardware, "Volume LED", "VOL_LED_SWITCH_GET", "VOL_LED_SWITCH_SET"));
        specs.Add(Toggle("hardware.buttons", SettingCategories.Hardware, "Buttons", "Button_Enable_GET", "Button_Enable_SET"));
    }

    private static void AddBluetooth(List<SettingSpec> specs)
    {
        SettingChoiceSource history = async execution => SettingParsers.BluetoothDevices(await execution.SendAsync("getbthistory"));
        SettingChoiceSource historyAndScan = async execution =>
        {
            var known = SettingParsers.BluetoothDevices(await execution.SendAsync("getbthistory"));
            var scanned = SettingParsers.BluetoothDevices(await execution.SendAsync("getbtdiscoveryresult"));
            return known.Concat(scanned).DistinctBy(c => c.Value, StringComparer.OrdinalIgnoreCase).ToList();
        };

        specs.Add(new SettingSpec(
            Def("bluetooth.history", SettingCategories.Bluetooth, "Paired Bluetooth devices", SettingKind.Number),
            "getbthistory",
            SettingParsers.JsonCount("num")));
        specs.Add(new SettingSpec(
            Def("bluetooth.scan", SettingCategories.Bluetooth, "Scan for Bluetooth devices", SettingKind.Action),
            GateCommand: "getbthistory",
            Execute: (execution, argument) => execution.SendAsync($"startbtdiscovery:{(argument is null ? 3 : SpeakerReply.ToInt(argument))}")));
        specs.Add(new SettingSpec(
            Def("bluetooth.connect", SettingCategories.Bluetooth, "Connect Bluetooth device", SettingKind.Action, dynamic: true),
            GateCommand: "getbthistory",
            Execute: Action(a => $"connectbta2dpsynk:{a}"),
            Choices: historyAndScan));
        specs.Add(new SettingSpec(
            Def("bluetooth.disconnect", SettingCategories.Bluetooth, "Disconnect Bluetooth device", SettingKind.Action, dynamic: true),
            GateCommand: "getbthistory",
            Execute: Action(a => $"disconnectbta2dpsynk:{a}"),
            Choices: history));
        specs.Add(new SettingSpec(
            Def("bluetooth.forget", SettingCategories.Bluetooth, "Forget Bluetooth device", SettingKind.Action, dynamic: true),
            GateCommand: "getbthistory",
            Execute: Action(a => $"delbthistory:{a}"),
            Choices: history));
    }

    private static void AddVoice(List<SettingSpec> specs)
    {
        specs.Add(new SettingSpec(
            Def("voice.alexaCountry", SettingCategories.Voice, "Alexa country", SettingKind.Text),
            "getAlexaCountry",
            SettingParsers.Raw,
            Execute: Simple(v => $"setAlexaCountry:{v.Trim()}")));
        specs.Add(new SettingSpec(
            Def("voice.alexaLanguage", SettingCategories.Voice, "Alexa language", SettingKind.Choice, AlexaLanguages),
            "alexaGetLanguage",
            SettingParsers.Raw,
            Execute: Simple(v => $"alexaSetLanguage:{v.Trim()}")));
        specs.Add(new SettingSpec(
            Def("voice.musicHd", SettingCategories.Voice, "Alexa music HD", SettingKind.Toggle),
            "getAvsMusicHDEnable",
            SettingParsers.Prefixed("AvsMusicHDEnable:"),
            Execute: Simple(v => $"setAvsMusicHDEnable:{ToggleValue(v)}")));
    }

    private static void AddAudioCast(List<SettingSpec> specs)
    {
        SettingChoiceSource speakers = async execution => SettingParsers.CastSpeakers(await execution.SendAsync("audio_cast:get_speaker_list"));

        specs.Add(new SettingSpec(
            Def("audiocast.speakers", SettingCategories.AudioCast, "Audio cast speakers", SettingKind.Choice, dynamic: true),
            "audio_cast:get_speaker_list",
            reply => SettingParsers.CastSpeakers(reply).Count.ToString(CultureInfo.InvariantCulture),
            Choices: speakers));
        specs.Add(new SettingSpec(
            Def("audiocast.enable", SettingCategories.AudioCast, "Enable cast speaker", SettingKind.Action, dynamic: true),
            GateCommand: "audio_cast:get_speaker_list",
            Execute: Action(a => $"audio_cast:speaker_enable:{a}"),
            Choices: speakers));
        specs.Add(new SettingSpec(
            Def("audiocast.disable", SettingCategories.AudioCast, "Disable cast speaker", SettingKind.Action, dynamic: true),
            GateCommand: "audio_cast:get_speaker_list",
            Execute: Action(a => $"audio_cast:speaker_disable:{a}"),
            Choices: speakers));
        specs.Add(new SettingSpec(
            Def("audiocast.password", SettingCategories.AudioCast, "Cast speaker password", SettingKind.Action, dynamic: true),
            GateCommand: "audio_cast:get_speaker_list",
            Execute: Action(a =>
            {
                var parts = a.Split(CastPasswordSeparator, 2);
                if (parts.Length != 2)
                {
                    throw new ArgumentException("The argument must be the speaker id, a tab and the password.");
                }

                return $"audio_cast:speaker_set_password:{parts[0]}:{parts[1]}";
            }),
            Choices: speakers));
    }

    private static SettingSpec Toggle(string key, string category, string label, string getter, string setter)
    {
        return new SettingSpec(
            Def(key, category, label, SettingKind.Toggle),
            getter,
            SettingParsers.Number,
            Execute: Simple(v => $"{setter}:{ToggleValue(v)}"));
    }

    private static SettingSpec Cap(string key, string category, string label, SettingKind kind, SettingChoice[]? choices, string getter, string setter, int fieldCount, int fieldIndex)
    {
        return new SettingSpec(
            Def(key, category, label, kind, choices),
            getter,
            SettingParsers.Field(fieldIndex),
            Execute: async (execution, value) =>
            {
                var current = await execution.SendAsync(getter);
                var next = kind == SettingKind.Toggle ? ToggleValue(value) : value ?? throw new ArgumentNullException(nameof(value));
                await execution.SendAsync(CapCommand(setter, current, fieldCount, fieldIndex, next));
            });
    }

    private static SettingExecutor Simple(Func<string, string> command)
    {
        return (execution, value) => execution.SendAsync(command(value ?? throw new ArgumentNullException(nameof(value))));
    }

    private static SettingExecutor Action(Func<string, string> command)
    {
        return (execution, argument) => execution.SendAsync(command(argument ?? string.Empty));
    }

    private static DeviceSettingDefinition Def(
        string key,
        string category,
        string label,
        SettingKind kind,
        IReadOnlyList<SettingChoice>? choices = null,
        int? min = null,
        int? max = null,
        string? confirmText = null,
        bool dynamic = false)
    {
        return new DeviceSettingDefinition(key, category, label, kind, choices, min, max, confirmText, dynamic);
    }
}
