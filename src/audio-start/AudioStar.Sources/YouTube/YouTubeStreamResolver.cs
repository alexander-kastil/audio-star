using System.Text.RegularExpressions;
using AudioStar.Core;
using AudioStar.Sources.YtDlp;
using Microsoft.Extensions.Logging;

namespace AudioStar.Sources.YouTube;

public sealed partial class YouTubeStreamResolver(IYtDlp ytDlp, ISettingsStore settings, ILogger<YouTubeStreamResolver> logger)
    : YtDlpStreamResolver(ytDlp, logger)
{
    public override string SourceId => SourceIds.YouTube;

    protected override string BuildUrl(string itemId)
    {
        if (!VideoIdPattern().IsMatch(itemId))
        {
            throw new ArgumentException("Not a YouTube video id.", nameof(itemId));
        }
        return $"https://www.youtube.com/watch?v={itemId}";
    }

    protected override IReadOnlyList<string> ExtraArguments() => YtDlpCookies.Arguments(settings.Current.YouTubeCookieSource);

    [GeneratedRegex("^[A-Za-z0-9_-]{6,20}$")]
    private static partial Regex VideoIdPattern();
}
