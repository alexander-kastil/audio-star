using System.Text.Json;
using AudioStar.Core;

namespace AudioStar.Sources.Radio;

internal static class RadioMapper
{
    public static RadioStation? MapStation(JsonElement station)
    {
        var id = station.Str("stationuuid");
        var name = station.Str("name")?.Trim();
        var stream = (station.Str("url_resolved") is { Length: > 0 } resolved ? resolved : station.Str("url")).AsHttpUri();
        if (string.IsNullOrEmpty(id) || string.IsNullOrEmpty(name) || stream is null)
        {
            return null;
        }
        var tags = (station.Str("tags") ?? "")
            .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .ToList();
        int? bitrate = station.Int("bitrate") is > 0 and var kbps ? kbps : null;
        var codec = station.Str("codec") is { Length: > 0 } c ? c : null;
        var country = station.Str("country") is { Length: > 0 } countryName ? countryName : null;
        var countryCode = station.Str("countrycode") is { Length: > 0 } code ? code : null;
        return new RadioStation(id, name, stream, station.Str("favicon").AsHttpUri(), country, countryCode, tags, bitrate, codec);
    }

    public static IReadOnlyList<RadioStation> MapStations(JsonElement array) =>
        array.ValueKind != JsonValueKind.Array
            ? []
            : array.EnumerateArray().Select(MapStation).Where(s => s is not null).Select(s => s!).ToList();

    public static IReadOnlyList<string> MapServerNames(JsonElement array) =>
        array.ValueKind != JsonValueKind.Array
            ? []
            : array.EnumerateArray().Select(e => e.Str("name")).Where(n => !string.IsNullOrEmpty(n)).Select(n => n!).Distinct().ToList();
}
