using System.Text.Json;

namespace AudioStar.Speakers.Playback;

internal static class InputCatalog
{
    private const int Linein = 1;
    private const int Bluetooth = 2;
    private const int Usb = 3;
    private const int Optical = 4;
    private const int Rca = 5;
    private const int Coaxial = 6;
    private const int Radio = 7;
    private const int Linein2 = 8;
    private const int Xlr = 9;
    private const int Hdmi = 10;
    private const int Tf = 13;
    private const int ExternBt = 14;
    private const int PcUsb = 15;
    private const int Phono = 16;
    private const int Arc = 22;
    private const int Wifi = 10001;

    private static readonly int[] KeyOrder =
        [Wifi, Bluetooth, Linein, Usb, ExternBt, PcUsb, Tf, Xlr, Rca, Radio, Linein2, Optical, Hdmi, Coaxial, Phono];

    private static readonly HashSet<string> AmpProjects = new(StringComparer.Ordinal)
    {
        "WiiM_AMP", "WiiM_Amp_Pro", "WiiM_Amp_4layer", "WiiM_Amp_Ultra", "WiiM_AMP_No_MFI", "WiiM_CI_MOD_A80"
    };

    private static readonly HashSet<string> ProProjects = new(StringComparer.Ordinal)
    {
        "WiiM_Pro_with_gc4a", "WiiM_Pro_AVS", "WiiM_Pro_Plus"
    };

    public static IReadOnlyList<AudioInput> Build(string project, long plmSupport, bool hasUsbDisk, string? modeRenameJson)
    {
        var template = TemplateFor(project);
        var renames = ParseRenames(modeRenameJson);
        var inputs = new List<AudioInput>();
        foreach (var key in KeyOrder)
        {
            if (!template.TryGetValue(key, out var entry))
            {
                continue;
            }
            if (!IsSupported(key, plmSupport, hasUsbDisk))
            {
                continue;
            }
            inputs.Add(new AudioInput(entry.Mode, RenamedTitle(entry, renames)));
        }
        return inputs;
    }

    public static bool IsSupported(int key, long plmSupport, bool hasUsbDisk)
    {
        if (key == Wifi)
        {
            return true;
        }
        if (key == Tf)
        {
            return false;
        }
        if (key == Usb && !hasUsbDisk)
        {
            return false;
        }
        if (key >= 32)
        {
            return false;
        }
        if (key == Linein)
        {
            return true;
        }
        var flag = 1L << key;
        return (plmSupport & flag) == flag;
    }

    private static string RenamedTitle((string Mode, string Title) entry, IReadOnlyDictionary<string, string> renames)
    {
        var renameKey = entry.Mode switch
        {
            "line-in" => "Line-In",
            "optical" => "SPDIF-In",
            _ => null
        };
        return renameKey is not null && renames.TryGetValue(renameKey, out var renamed) && renamed.Length > 0 ? renamed : entry.Title;
    }

    private static Dictionary<string, string> ParseRenames(string? json)
    {
        var result = new Dictionary<string, string>(StringComparer.Ordinal);
        if (string.IsNullOrWhiteSpace(json))
        {
            return result;
        }
        try
        {
            using var document = JsonDocument.Parse(json);
            if (document.RootElement.ValueKind != JsonValueKind.Object)
            {
                return result;
            }
            foreach (var property in document.RootElement.EnumerateObject())
            {
                if (property.Value.ValueKind == JsonValueKind.String)
                {
                    result[property.Name] = property.Value.GetString()?.Trim() ?? "";
                }
            }
        }
        catch (JsonException)
        {
        }
        return result;
    }

    private static Dictionary<int, (string Mode, string Title)> TemplateFor(string project)
    {
        if (AmpProjects.Contains(project))
        {
            return new()
            {
                [Hdmi] = ("HDMI", "TV"),
                [Linein] = ("line-in", "Line In"),
                [Optical] = ("optical", "Optical In"),
                [Bluetooth] = ("bluetooth", "Bluetooth"),
                [Wifi] = ("wifi", "Wi-Fi")
            };
        }
        if (project == "WiiM_Ultra")
        {
            return new()
            {
                [Phono] = ("phono", "PHONO"),
                [Hdmi] = ("HDMI", "TV"),
                [Linein] = ("line-in", "Line In"),
                [Optical] = ("optical", "Optical In"),
                [Bluetooth] = ("bluetooth", "Bluetooth"),
                [Wifi] = ("wifi", "Wi-Fi")
            };
        }
        if (ProProjects.Contains(project))
        {
            return new()
            {
                [Linein] = ("line-in", "Line In"),
                [Optical] = ("optical", "Optical In"),
                [Bluetooth] = ("bluetooth", "Bluetooth"),
                [Wifi] = ("wifi", "Wi-Fi")
            };
        }
        return new()
        {
            [Arc] = ("arc", "ARC"),
            [Phono] = ("phono", "PHONO"),
            [PcUsb] = ("PCUSB", "USBDAC"),
            [ExternBt] = ("extern_bluetooth", "Bluetooth"),
            [Wifi] = ("wifi", "Wi-Fi"),
            [Coaxial] = ("co-axial", "CO-AXIAL"),
            [Hdmi] = ("HDMI", "TV"),
            [Optical] = ("optical", "Optical"),
            [Rca] = ("RCA", "Stereo out"),
            [Radio] = ("FM", "Radio"),
            [Linein2] = ("line-in", "Aux"),
            [Linein] = ("line-in", "Aux In"),
            [Xlr] = ("XLR", "XLR"),
            [Tf] = ("TFCard", "TF Card"),
            [Usb] = ("udisk", "USB Devices"),
            [Bluetooth] = ("bluetooth", "Bluetooth")
        };
    }
}
