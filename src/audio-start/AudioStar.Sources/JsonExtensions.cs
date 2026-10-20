using System.Text.Json;

namespace AudioStar.Sources;

internal static class JsonExtensions
{
    public static JsonElement? Get(this JsonElement element, string name) =>
        element.ValueKind == JsonValueKind.Object && element.TryGetProperty(name, out var value) && value.ValueKind != JsonValueKind.Null
            ? value
            : null;

    public static string? Str(this JsonElement element, string name) =>
        element.Get(name) switch
        {
            { ValueKind: JsonValueKind.String } value => value.GetString(),
            { ValueKind: JsonValueKind.Number } value => value.GetRawText(),
            _ => null
        };

    public static double? Num(this JsonElement element, string name) =>
        element.Get(name) is { ValueKind: JsonValueKind.Number } value && value.TryGetDouble(out var number) ? number : null;

    public static int? Int(this JsonElement element, string name) =>
        element.Num(name) is { } number ? (int)number : null;

    public static IEnumerable<JsonElement> Items(this JsonElement element, string name) =>
        element.Get(name) is { ValueKind: JsonValueKind.Array } array ? array.EnumerateArray() : [];

    public static Uri? AsHttpUri(this string? value) =>
        Uri.TryCreate(value, UriKind.Absolute, out var uri) && (uri.Scheme == Uri.UriSchemeHttp || uri.Scheme == Uri.UriSchemeHttps) ? uri : null;
}
