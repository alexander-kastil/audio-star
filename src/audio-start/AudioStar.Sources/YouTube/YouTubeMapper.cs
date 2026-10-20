using System.Text.Json;
using System.Web;
using AudioStar.Core;

namespace AudioStar.Sources.YouTube;

internal static class YouTubeMapper
{
    private static readonly string[] HiddenTitles = ["[Private video]", "[Deleted video]", "[Unavailable video]"];

    public static Uri ThumbnailUri(string videoId) => new($"https://i.ytimg.com/vi/{videoId}/hqdefault.jpg");

    public static string PlaylistUrl(string playlistId) => $"https://www.youtube.com/playlist?list={Uri.EscapeDataString(playlistId)}";

    public static string? NormalizePlaylistUrl(string? input)
    {
        if (!Uri.TryCreate(input?.Trim(), UriKind.Absolute, out var uri) || uri.Scheme is not ("http" or "https"))
        {
            return null;
        }
        var host = uri.Host;
        if (host != "youtu.be" && host != "youtube.com" && !host.EndsWith(".youtube.com", StringComparison.OrdinalIgnoreCase))
        {
            return null;
        }
        var list = HttpUtility.ParseQueryString(uri.Query)["list"];
        return string.IsNullOrWhiteSpace(list) ? null : PlaylistUrl(list);
    }

    public static IReadOnlyList<SourceTrack> MapTracks(JsonElement root)
    {
        var tracks = new List<SourceTrack>();
        foreach (var entry in root.Items("entries"))
        {
            var id = entry.Str("id");
            var title = entry.Str("title");
            if (string.IsNullOrEmpty(id) || string.IsNullOrWhiteSpace(title))
            {
                continue;
            }
            if (HiddenTitles.Contains(title, StringComparer.OrdinalIgnoreCase) || entry.Str("availability") == "private")
            {
                continue;
            }
            TimeSpan? duration = entry.Num("duration") is { } seconds ? TimeSpan.FromSeconds(seconds) : null;
            tracks.Add(new SourceTrack(SourceIds.YouTube, id, title, entry.Str("channel") ?? entry.Str("uploader"), null, duration, ThumbnailUri(id)));
        }
        return tracks;
    }

    public static IReadOnlyList<SourcePlaylist> MapLibrary(JsonElement root)
    {
        var playlists = new List<SourcePlaylist>();
        foreach (var entry in root.Items("entries"))
        {
            var title = entry.Str("title");
            var id = ListIdOf(entry);
            if (string.IsNullOrEmpty(id) || string.IsNullOrWhiteSpace(title))
            {
                continue;
            }
            var url = PlaylistUrl(id);
            var count = entry.Int("playlist_count") ?? entry.Int("n_entries") ?? entry.Int("video_count");
            playlists.Add(new SourcePlaylist(SourceIds.YouTube, url, title, entry.Str("channel") ?? entry.Str("uploader"), count, FirstThumbnail(entry), new Uri(url)));
        }
        return playlists;
    }

    public static SourcePlaylist MapPlaylistHeader(JsonElement root, string url)
    {
        var firstVideo = root.Items("entries").Select(e => e.Str("id")).FirstOrDefault(id => !string.IsNullOrEmpty(id));
        var title = root.Str("title") ?? url;
        var artwork = FirstThumbnail(root) ?? (firstVideo is null ? null : ThumbnailUri(firstVideo));
        return new SourcePlaylist(SourceIds.YouTube, url, title, root.Str("channel") ?? root.Str("uploader"), root.Int("playlist_count"), artwork, new Uri(url));
    }

    private static string? ListIdOf(JsonElement entry)
    {
        var url = entry.Str("url") ?? entry.Str("webpage_url");
        if (Uri.TryCreate(url, UriKind.Absolute, out var uri) && HttpUtility.ParseQueryString(uri.Query)["list"] is { Length: > 0 } fromUrl)
        {
            return fromUrl;
        }
        var id = entry.Str("id");
        return entry.Str("ie_key") == "YoutubeTab" || (id is not null && id.Length > 10) ? id : null;
    }

    private static Uri? FirstThumbnail(JsonElement element) =>
        element.Items("thumbnails").Select(t => t.Str("url").AsHttpUri()).FirstOrDefault(u => u is not null);
}
