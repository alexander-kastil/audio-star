using System.Globalization;
using System.Text.Json;

namespace AudioStar.Speakers.Discovery;

internal sealed record SpeakerStatus(
    string Uuid,
    string DeviceName,
    string Project,
    string Firmware,
    long PlmSupport,
    bool IsFollower,
    string MasterUuid,
    bool HasUsbDisk)
{
    public static SpeakerStatus? Parse(string? json)
    {
        if (string.IsNullOrWhiteSpace(json))
        {
            return null;
        }
        try
        {
            using var document = JsonDocument.Parse(json);
            if (document.RootElement.ValueKind != JsonValueKind.Object)
            {
                return null;
            }
            var root = document.RootElement;
            var uuid = SpeakerIdentity.Normalize(Text(root, "uuid"));
            if (uuid.Length == 0)
            {
                return null;
            }
            var name = Text(root, "DeviceName");
            if (name.Length == 0)
            {
                name = Text(root, "GroupName");
            }
            return new SpeakerStatus(
                uuid,
                name,
                Text(root, "project"),
                Text(root, "firmware"),
                ParseHex(Text(root, "plm_support")),
                Text(root, "group") == "1",
                SpeakerIdentity.Normalize(Text(root, "master_uuid")),
                Text(root, "udisk") == "1");
        }
        catch (JsonException)
        {
            return null;
        }
    }

    public static string Text(JsonElement element, string name)
    {
        if (!element.TryGetProperty(name, out var value))
        {
            return "";
        }
        return value.ValueKind switch
        {
            JsonValueKind.String => value.GetString() ?? "",
            JsonValueKind.Number => value.GetRawText(),
            JsonValueKind.True => "1",
            JsonValueKind.False => "0",
            _ => ""
        };
    }

    private static long ParseHex(string value)
    {
        var text = value.StartsWith("0x", StringComparison.OrdinalIgnoreCase) ? value[2..] : value;
        return long.TryParse(text, NumberStyles.HexNumber, CultureInfo.InvariantCulture, out var parsed) ? parsed : 0;
    }
}
