using System.Text.RegularExpressions;
using AudioStar.Core;
using AudioStar.Sources.YtDlp;
using Microsoft.Extensions.Logging;

namespace AudioStar.Sources.SoundCloud;

public sealed partial class SoundCloudStreamResolver(IYtDlp ytDlp, SoundCloudSession session, ILogger<SoundCloudStreamResolver> logger)
    : YtDlpStreamResolver(ytDlp, logger)
{
    public override string SourceId => SourceIds.SoundCloud;

    protected override IReadOnlyList<string> ExtraArguments() => session.AuthArguments();

    protected override string BuildUrl(string itemId)
    {
        if (TrackIdPattern().IsMatch(itemId))
        {
            return $"https://api.soundcloud.com/tracks/{itemId}";
        }
        return SoundCloudMapper.NormalizeUrl(itemId) ?? throw new ArgumentException("Not a SoundCloud track id.", nameof(itemId));
    }

    [GeneratedRegex(@"^\d{1,15}$")]
    private static partial Regex TrackIdPattern();
}
