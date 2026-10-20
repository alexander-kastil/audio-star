using System.Globalization;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace AudioStar.Devices;

internal static class SpeakerReply
{
    public static bool IsFailure(string? reply)
    {
        var text = reply?.Trim();
        return string.IsNullOrEmpty(text)
            || text.Equals("Failed", StringComparison.OrdinalIgnoreCase)
            || text.Equals("unknown command", StringComparison.OrdinalIgnoreCase)
            || text.Equals("no parameters", StringComparison.OrdinalIgnoreCase);
    }

    public static JsonNode? TryParse(string? reply)
    {
        if (string.IsNullOrWhiteSpace(reply))
        {
            return null;
        }

        try
        {
            return JsonNode.Parse(reply);
        }
        catch (JsonException)
        {
            return null;
        }
    }

    public static string? Scalar(JsonNode? node)
    {
        if (node is not JsonValue value)
        {
            return null;
        }

        if (value.TryGetValue<string>(out var text))
        {
            return text;
        }

        if (value.TryGetValue<bool>(out var flag))
        {
            return flag ? "1" : "0";
        }

        return value.TryGetValue<double>(out var number) ? FormatNumber(number) : null;
    }

    public static string FormatNumber(double number)
    {
        return number.ToString("0.##########", CultureInfo.InvariantCulture);
    }

    public static string NormalizeNumber(string text)
    {
        return double.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out var number)
            ? FormatNumber(number)
            : text;
    }

    public static int ToInt(string text)
    {
        return (int)Math.Round(double.Parse(text, NumberStyles.Float, CultureInfo.InvariantCulture), MidpointRounding.AwayFromZero);
    }

    public static string Hex(string text)
    {
        return Convert.ToHexString(System.Text.Encoding.UTF8.GetBytes(text));
    }
}
