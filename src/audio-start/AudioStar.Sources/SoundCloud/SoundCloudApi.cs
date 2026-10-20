using System.Text.Json;
using AudioStar.Core;

namespace AudioStar.Sources.SoundCloud;

internal sealed record SoundCloudTrackInfo(string Id, string? Title, string? Artist, TimeSpan? Duration, Uri? Artwork);

internal static class SoundCloudApi
{
    public const int TrackBatchSize = 50;
    public const int HistoryPageSize = 200;
    public const int HistoryMaxPages = 5;
    public const string HistoryUrl = "https://soundcloud.com/you/history";

    public static IReadOnlyList<SoundCloudTrackInfo> ParseTracks(JsonElement array)
    {
        var infos = new List<SoundCloudTrackInfo>();
        if (array.ValueKind != JsonValueKind.Array)
        {
            return infos;
        }
        foreach (var track in array.EnumerateArray())
        {
            if (ParseTrack(track) is { } info)
            {
                infos.Add(info);
            }
        }
        return infos;
    }

    public static (IReadOnlyList<SoundCloudTrackInfo> Tracks, string? NextHref) ParseHistory(JsonElement root)
    {
        var tracks = new List<SoundCloudTrackInfo>();
        foreach (var item in root.Items("collection"))
        {
            if (item.Get("track") is { } track && ParseTrack(track) is { } info)
            {
                tracks.Add(info);
            }
        }
        var next = root.Str("next_href");
        return (tracks, string.IsNullOrEmpty(next) ? null : next);
    }

    public static IReadOnlyList<SourceTrack> ToSourceTracks(IEnumerable<SoundCloudTrackInfo> infos, string album) =>
        infos
            .DistinctBy(i => i.Id)
            .Select(i => new SourceTrack(SourceIds.SoundCloud, i.Id, string.IsNullOrWhiteSpace(i.Title) ? $"SoundCloud track {i.Id}" : i.Title, i.Artist, album, i.Duration, i.Artwork))
            .ToList();

    public static SoundCloudTrackInfo? ParseTrack(JsonElement track)
    {
        var id = track.Str("id");
        if (string.IsNullOrEmpty(id))
        {
            return null;
        }
        TimeSpan? duration = track.Num("duration") is > 0 and var ms ? TimeSpan.FromMilliseconds(ms) : null;
        var user = track.Get("user") ?? default;
        return new SoundCloudTrackInfo(id, track.Str("title"), user.Str("username"), duration, TrackArtwork(track));
    }

    public static Uri? TrackArtwork(JsonElement track)
    {
        var user = track.Get("user") ?? default;
        return LargeArtwork(track.Str("artwork_url")) ?? LargeArtwork(user.Str("avatar_url"));
    }

    public static Uri? LargeArtwork(string? url)
    {
        if (string.IsNullOrEmpty(url))
        {
            return null;
        }
        return url.Replace("-large.", "-t500x500.", StringComparison.Ordinal).AsHttpUri();
    }

    public static Uri? PlaylistArtwork(JsonElement playlist)
    {
        if (LargeArtwork(playlist.Str("artwork_url")) is { } own)
        {
            return own;
        }
        foreach (var track in playlist.Items("tracks"))
        {
            if (LargeArtwork(track.Str("artwork_url")) is { } cover)
            {
                return cover;
            }
        }
        return null;
    }

    public static Uri? FirstLikeArtwork(JsonElement likes)
    {
        foreach (var like in likes.Items("collection"))
        {
            if (like.Get("track") is { } track && LargeArtwork(track.Str("artwork_url")) is { } cover)
            {
                return cover;
            }
        }
        return null;
    }

    public static IReadOnlyList<SourceTrack> Enrich(IReadOnlyList<SourceTrack> tracks, IReadOnlyList<SoundCloudTrackInfo> infos)
    {
        var byId = infos.GroupBy(i => i.Id).ToDictionary(g => g.Key, g => g.First());
        return tracks
            .Select(t => byId.TryGetValue(t.Id, out var info)
                ? t with
                {
                    Title = string.IsNullOrWhiteSpace(t.Title) || t.Title == $"SoundCloud track {t.Id}" ? info.Title ?? t.Title : t.Title,
                    Artist = info.Artist ?? t.Artist,
                    Duration = info.Duration ?? t.Duration,
                    ArtworkUri = info.Artwork ?? t.ArtworkUri
                }
                : t)
            .ToList();
    }

    public static bool IsTrackId(string id) => id.Length is > 0 and <= 15 && id.All(char.IsAsciiDigit);
}
