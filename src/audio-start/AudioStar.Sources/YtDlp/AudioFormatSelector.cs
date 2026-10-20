using System.Text.Json;
using System.Text.RegularExpressions;
using AudioStar.Core;

namespace AudioStar.Sources.YtDlp;

public sealed record SelectedAudio(ResolvedStream Stream, DateTimeOffset? ExpiresAt);

public static partial class AudioFormatSelector
{
    public static SelectedAudio? Select(JsonElement video)
    {
        var candidates = video.Items("formats")
            .Select(Describe)
            .Where(c => c is not null)
            .Select(c => c!)
            .ToList();

        var audioOnly = candidates.Where(c => c.AudioOnly).OrderByDescending(c => c.Score).ThenByDescending(c => c.Bitrate).FirstOrDefault();
        var chosen = audioOnly ?? candidates.Where(c => c.HasAudio).OrderByDescending(c => c.Bitrate).FirstOrDefault();
        if (chosen is null)
        {
            return video.Str("url").AsHttpUri() is { } direct
                ? new SelectedAudio(new ResolvedStream(direct, "audio/mpeg", Headers(video), true, null, DurationOf(video)), ExpiryOf(direct))
                : null;
        }

        var headers = chosen.Headers ?? Headers(video);
        var stream = new ResolvedStream(chosen.Url, chosen.ContentType, headers, chosen.RequiresTranscode, chosen.Length, DurationOf(video));
        return new SelectedAudio(stream, ExpiryOf(chosen.Url));
    }

    internal static TimeSpan? DurationOf(JsonElement video)
    {
        if (video.Get("is_live") is { ValueKind: JsonValueKind.True })
        {
            return null;
        }
        return video.Num("duration") is > 0 and var seconds ? TimeSpan.FromSeconds(seconds) : null;
    }

    public static DateTimeOffset? ExpiryOf(Uri url)
    {
        var match = ExpiryPattern().Match(url.OriginalString);
        return match.Success && long.TryParse(match.Groups[1].Value, out var seconds) ? DateTimeOffset.FromUnixTimeSeconds(seconds) : null;
    }

    private static IReadOnlyDictionary<string, string>? Headers(JsonElement element)
    {
        if (element.Get("http_headers") is not { ValueKind: JsonValueKind.Object } headers)
        {
            return null;
        }
        var result = headers.EnumerateObject()
            .Where(p => p.Value.ValueKind == JsonValueKind.String)
            .ToDictionary(p => p.Name, p => p.Value.GetString()!);
        return result.Count == 0 ? null : result;
    }

    private static Candidate? Describe(JsonElement format)
    {
        var url = format.Str("url").AsHttpUri();
        if (url is null)
        {
            return null;
        }
        var protocol = format.Str("protocol") ?? "";
        var ext = (format.Str("ext") ?? "").ToLowerInvariant();
        var acodec = (format.Str("acodec") ?? "").ToLowerInvariant();
        var vcodec = (format.Str("vcodec") ?? "").ToLowerInvariant();
        var isHls = protocol.StartsWith("m3u8", StringComparison.OrdinalIgnoreCase) || ext == "m3u8";
        var isProgressive = protocol is "http" or "https";
        if (!isHls && !isProgressive)
        {
            return null;
        }
        var noVideo = vcodec is "" or "none";
        var hasAudio = acodec != "none" && (acodec != "" || noVideo);
        if (!hasAudio)
        {
            return null;
        }

        var isAac = ext is "m4a" or "aac" || acodec.StartsWith("mp4a");
        var isMp3 = ext == "mp3" || acodec == "mp3";
        var bitrate = format.Num("abr") ?? format.Num("tbr") ?? 0;
        var score = (isHls, isAac, isMp3) switch
        {
            (false, true, _) => 50,
            (false, _, true) => 40,
            (false, _, _) => 20,
            (true, true, _) => 10,
            _ => 5
        };
        var contentType = isHls ? "application/vnd.apple.mpegurl"
            : ext == "aac" ? "audio/aac"
            : isAac ? noVideo ? "audio/mp4" : "video/mp4"
            : isMp3 ? "audio/mpeg"
            : ext == "ogg" ? "audio/ogg"
            : "audio/webm";
        var length = format.Num("filesize") ?? format.Num("filesize_approx");
        var playsNatively = !isHls && (isAac || isMp3) && noVideo;
        return new Candidate(url, contentType, Headers(format), !playsNatively, length is { } l ? (long)l : null, noVideo, true, score, bitrate);
    }

    private sealed record Candidate(
        Uri Url,
        string ContentType,
        IReadOnlyDictionary<string, string>? Headers,
        bool RequiresTranscode,
        long? Length,
        bool AudioOnly,
        bool HasAudio,
        int Score,
        double Bitrate);

    [GeneratedRegex(@"[?&/]expires?[=/](\d{9,11})", RegexOptions.IgnoreCase)]
    private static partial Regex ExpiryPattern();
}
