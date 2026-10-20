using System.Globalization;
using System.Text.Json;
using AudioStar.Core;

namespace AudioStar.Sources.SoundCloud;

internal static class SoundCloudMapper
{
    public static string? NormalizeUrl(string? input)
    {
        if (!Uri.TryCreate(input?.Trim(), UriKind.Absolute, out var uri) || uri.Scheme is not ("http" or "https"))
        {
            return null;
        }
        var host = uri.Host;
        if (host != "soundcloud.com" && !host.EndsWith(".soundcloud.com", StringComparison.OrdinalIgnoreCase))
        {
            return null;
        }
        return $"https://soundcloud.com{uri.AbsolutePath.TrimEnd('/')}";
    }

    public static string? NormalizeProfile(string? input)
    {
        var url = NormalizeUrl(input);
        if (url is null)
        {
            return null;
        }
        var segments = new Uri(url).AbsolutePath.Split('/', StringSplitOptions.RemoveEmptyEntries);
        return segments.Length == 0 ? null : $"https://soundcloud.com/{segments[0]}";
    }

    public static IReadOnlyList<SourceTrack> MapTracks(JsonElement root)
    {
        var tracks = new List<SourceTrack>();
        foreach (var entry in root.Items("entries"))
        {
            var url = entry.Str("url") ?? "";
            var id = entry.Str("id");
            if (string.IsNullOrEmpty(id) || url.Contains("/sets/", StringComparison.OrdinalIgnoreCase))
            {
                continue;
            }
            var title = entry.Str("title") is { Length: > 0 } named ? named : TitleFromUrl(url, id);
            TimeSpan? duration = entry.Num("duration") is { } seconds ? TimeSpan.FromSeconds(seconds) : null;
            var artwork = entry.Items("thumbnails").Select(t => t.Str("url").AsHttpUri()).FirstOrDefault(u => u is not null);
            tracks.Add(new SourceTrack(SourceIds.SoundCloud, id, title, entry.Str("uploader"), root.Str("title"), duration, artwork));
        }
        return tracks;
    }

    public static IReadOnlyList<SourcePlaylist> MapSets(JsonElement root, string? owner)
    {
        var sets = new List<SourcePlaylist>();
        foreach (var entry in root.Items("entries"))
        {
            var url = NormalizeUrl(entry.Str("url"));
            var title = entry.Str("title");
            if (url is null || string.IsNullOrWhiteSpace(title) || !url.Contains("/sets/", StringComparison.OrdinalIgnoreCase))
            {
                continue;
            }
            sets.Add(new SourcePlaylist(SourceIds.SoundCloud, url, title, owner, null, null, new Uri(url)));
        }
        return sets;
    }

    public static SourcePlaylist MapPlaylistHeader(JsonElement root, string url)
    {
        var artwork = root.Items("thumbnails").Select(t => t.Str("url").AsHttpUri()).FirstOrDefault(u => u is not null);
        return new SourcePlaylist(SourceIds.SoundCloud, url, root.Str("title") ?? url, root.Str("uploader"), root.Int("playlist_count"), artwork, new Uri(url));
    }

    public static string TitleFromUrl(string url, string id)
    {
        if (!Uri.TryCreate(url, UriKind.Absolute, out var uri) || uri.Host.StartsWith("api", StringComparison.OrdinalIgnoreCase))
        {
            return $"SoundCloud track {id}";
        }
        var slug = uri.AbsolutePath.Split('/', StringSplitOptions.RemoveEmptyEntries).LastOrDefault();
        if (string.IsNullOrEmpty(slug))
        {
            return $"SoundCloud track {id}";
        }
        var text = Uri.UnescapeDataString(slug).Replace('-', ' ');
        return CultureInfo.InvariantCulture.TextInfo.ToUpper(text[0]) + text[1..];
    }
}
