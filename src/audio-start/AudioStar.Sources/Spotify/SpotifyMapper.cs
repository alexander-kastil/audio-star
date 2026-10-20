using System.Text.Json;
using System.Text.RegularExpressions;
using AudioStar.Core;

namespace AudioStar.Sources.Spotify;

internal sealed record SpotifyDevice(string Id, string Name, bool IsActive);

internal static partial class SpotifyMapper
{
    public const string LikedId = "liked";

    public static SourcePlaylist LikedSongs(int? total) =>
        new(SourceIds.Spotify, LikedId, "Liked Songs", null, total, null, new Uri("https://open.spotify.com/collection/tracks"));

    public static SourcePlaylist? MapPlaylist(JsonElement playlist)
    {
        var id = playlist.Str("id");
        var name = playlist.Str("name");
        if (string.IsNullOrEmpty(id) || string.IsNullOrEmpty(name))
        {
            return null;
        }
        var total = playlist.Get("items")?.Int("total") ?? playlist.Get("tracks")?.Int("total");
        var artwork = playlist.Items("images").Select(i => i.Str("url").AsHttpUri()).FirstOrDefault(u => u is not null);
        var web = playlist.Get("external_urls")?.Str("spotify").AsHttpUri() ?? new Uri($"https://open.spotify.com/playlist/{id}");
        return new SourcePlaylist(SourceIds.Spotify, id, name, playlist.Get("owner")?.Str("display_name"), total, artwork, web);
    }

    public static IReadOnlyList<SourcePlaylist> MapPlaylists(IEnumerable<JsonElement> items) =>
        items.Select(MapPlaylist).Where(p => p is not null).Select(p => p!).ToList();

    public static SourceTrack? MapTrack(JsonElement entry)
    {
        JsonElement? track = entry.Get("item") ?? entry.Get("track");
        if (track is null && entry.Str("uri") is not null)
        {
            track = entry;
        }
        if (track is not { } t || t.Str("type") is { } type && type != "track" || t.Get("is_local") is { ValueKind: JsonValueKind.True })
        {
            return null;
        }
        var id = t.Str("id");
        var title = t.Str("name");
        if (string.IsNullOrEmpty(id) || string.IsNullOrEmpty(title))
        {
            return null;
        }
        var artists = string.Join(", ", t.Items("artists").Select(a => a.Str("name")).Where(n => !string.IsNullOrEmpty(n)));
        var album = t.Get("album");
        TimeSpan? duration = t.Num("duration_ms") is { } ms ? TimeSpan.FromMilliseconds(ms) : null;
        var artwork = album?.Items("images").Select(i => i.Str("url").AsHttpUri()).FirstOrDefault(u => u is not null);
        return new SourceTrack(SourceIds.Spotify, id, title, artists.Length == 0 ? null : artists, album?.Str("name"), duration, artwork);
    }

    public static IReadOnlyList<SourceTrack> MapTracks(IEnumerable<JsonElement> items) =>
        items.Select(MapTrack).Where(t => t is not null).Select(t => t!).ToList();

    public static string? ParsePlaylistId(string? input)
    {
        var match = PlaylistPattern().Match(input?.Trim() ?? "");
        return match.Success ? match.Groups[1].Value : null;
    }

    public static SpotifyDevice? FindDevice(JsonElement devices, string speakerName) =>
        devices.Items("devices")
            .Select(d => new SpotifyDevice(d.Str("id") ?? "", d.Str("name") ?? "", d.Get("is_active") is { ValueKind: JsonValueKind.True }))
            .FirstOrDefault(d => d.Id.Length > 0 && string.Equals(d.Name.Trim(), speakerName.Trim(), StringComparison.OrdinalIgnoreCase));

    public static string BuildPlayBody(string playlistId, IReadOnlyList<SourceTrack> likedTracks, int startIndex)
    {
        if (playlistId == LikedId)
        {
            var uris = likedTracks.Skip(startIndex).Take(100).Select(t => $"spotify:track:{t.Id}").ToList();
            return JsonSerializer.Serialize(new { uris });
        }
        return JsonSerializer.Serialize(new { context_uri = $"spotify:playlist:{playlistId}", offset = new { position = startIndex } });
    }

    [GeneratedRegex(@"(?:open\.spotify\.com/(?:intl-[a-z]+/)?playlist/|spotify:playlist:)([A-Za-z0-9]{10,40})")]
    private static partial Regex PlaylistPattern();
}
