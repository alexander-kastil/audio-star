using System.Globalization;
using System.Text.Json.Nodes;
using AudioStar.Core;

namespace AudioStar.Devices.Settings;

internal static class SettingParsers
{
    public static Func<string, string?> Raw { get; } = reply => reply.Trim();

    public static Func<string, string?> Number { get; } = reply => SpeakerReply.NormalizeNumber(reply.Trim());

    public static Func<string, string?> Key(string key)
    {
        return reply => SpeakerReply.Scalar((SpeakerReply.TryParse(reply) as JsonObject)?[key]);
    }

    public static Func<string, string?> NumberKey(string key)
    {
        return reply =>
        {
            var value = SpeakerReply.Scalar((SpeakerReply.TryParse(reply) as JsonObject)?[key]);
            return value is null ? null : SpeakerReply.NormalizeNumber(value);
        };
    }

    public static Func<string, string?> Field(int index)
    {
        return reply =>
        {
            var parts = reply.Trim().Split(':');
            return index < parts.Length ? parts[index] : null;
        };
    }

    public static Func<string, string?> Prefixed(string prefix)
    {
        return reply =>
        {
            var text = reply.Trim();
            return text.StartsWith(prefix, StringComparison.OrdinalIgnoreCase) ? text[prefix.Length..] : null;
        };
    }

    public static Func<string, string?> Present { get; } = _ => string.Empty;

    public static Func<string, string?> JsonCount(string key)
    {
        return reply =>
        {
            var root = SpeakerReply.TryParse(reply) as JsonObject;
            return root is null ? null : SpeakerReply.Scalar(root[key]) ?? "0";
        };
    }

    public static bool GateAccepts(string? reply)
    {
        if (SpeakerReply.IsFailure(reply))
        {
            return false;
        }

        return SpeakerReply.TryParse(reply) is not JsonArray { Count: 0 };
    }

    public static IReadOnlyList<SettingChoice> BluetoothDevices(string? reply)
    {
        var root = SpeakerReply.TryParse(reply) as JsonObject;
        var choices = new List<SettingChoice>();
        if (root?["list"] is not JsonArray list)
        {
            return choices;
        }

        foreach (var entry in list.OfType<JsonObject>())
        {
            var address = SpeakerReply.Scalar(entry["ad"]);
            if (string.IsNullOrEmpty(address))
            {
                continue;
            }

            var name = SpeakerReply.Scalar(entry["name"]);
            choices.Add(new SettingChoice(address, string.IsNullOrEmpty(name) ? address : name));
        }

        return choices;
    }

    public static IReadOnlyList<SettingChoice> CastSpeakers(string? reply)
    {
        var root = SpeakerReply.TryParse(reply);
        var array = root as JsonArray ?? (root as JsonObject)?["outputs"] as JsonArray;
        var choices = new List<SettingChoice>();
        if (array is null)
        {
            return choices;
        }

        foreach (var entry in array.OfType<JsonObject>())
        {
            var id = SpeakerReply.Scalar(entry["id"]);
            if (string.IsNullOrEmpty(id))
            {
                continue;
            }

            var name = SpeakerReply.Scalar(entry["name"]);
            choices.Add(new SettingChoice(id, string.IsNullOrEmpty(name) ? id : name));
        }

        return choices;
    }

    public static IReadOnlyList<SettingChoice> SoundCardModes(string? reply)
    {
        var choices = new List<SettingChoice>();
        if (SpeakerReply.TryParse(reply) is not JsonArray array)
        {
            return choices;
        }

        foreach (var entry in array.OfType<JsonObject>())
        {
            var index = SpeakerReply.Scalar(entry["index"]);
            if (index is null)
            {
                continue;
            }

            var name = SpeakerReply.Scalar((entry["soundCard"] as JsonObject)?["devName"]) ?? SpeakerReply.Scalar(entry["mode"]) ?? index;
            choices.Add(new SettingChoice(index, name));
        }

        return choices;
    }

    public static IReadOnlyList<SettingChoice> IndexedList(string? reply, Func<JsonObject, string?> label)
    {
        var choices = new List<SettingChoice>();
        if (SpeakerReply.TryParse(reply) is not JsonArray array)
        {
            return choices;
        }

        for (var position = 0; position < array.Count; position++)
        {
            switch (array[position])
            {
                case JsonObject entry:
                    var value = SpeakerReply.Scalar(entry["index"]) ?? SpeakerReply.Scalar(entry["type"]) ?? SpeakerReply.Scalar(entry["id"]) ?? SpeakerReply.Scalar(entry["value"]) ?? position.ToString(CultureInfo.InvariantCulture);
                    choices.Add(new SettingChoice(value, label(entry) ?? value));
                    break;
                case JsonValue scalar:
                    var text = SpeakerReply.Scalar(scalar) ?? string.Empty;
                    choices.Add(new SettingChoice(position.ToString(CultureInfo.InvariantCulture), text));
                    break;
            }
        }

        return choices;
    }

    public static string? FilterLabel(JsonObject entry)
    {
        return SpeakerReply.Scalar(entry["name"]) ?? SpeakerReply.Scalar(entry["title"]) ?? SpeakerReply.Scalar(entry["desc"]) ?? SpeakerReply.Scalar(entry["description"]);
    }

    public static string? VoltageLabel(JsonObject entry)
    {
        var raw = SpeakerReply.Scalar(entry["value"]);
        if (raw is null)
        {
            return null;
        }

        var digits = new string(raw.Where(char.IsDigit).ToArray());
        if (!int.TryParse(digits, out var millivolts))
        {
            return raw;
        }

        return millivolts >= 1000 ? $"{millivolts / 1000} Vrms" : $"{millivolts} mVrms";
    }
}
