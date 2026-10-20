using System.Globalization;
using AudioStar.Core;

namespace AudioStar.Desktop.Services;

public enum RepeatMode { Off, List, Single }

public static class PlaybackFormat
{
    public static string Time(TimeSpan value)
    {
        if (value < TimeSpan.Zero)
        {
            value = TimeSpan.Zero;
        }
        return value.TotalHours >= 1
            ? $"{(int)value.TotalHours}:{value.Minutes:00}:{value.Seconds:00}"
            : $"{value.Minutes}:{value.Seconds:00}";
    }

    public static string? Quality(TrackInfo? track)
    {
        if (track is null)
        {
            return null;
        }
        var parts = new List<string>();
        if (track.BitrateKbps is > 0)
        {
            parts.Add(string.Create(CultureInfo.InvariantCulture, $"{track.BitrateKbps.Value:0} kbps"));
        }
        if (track.BitDepth is > 0 && track.SampleRateHz is > 0)
        {
            parts.Add(string.Create(CultureInfo.InvariantCulture, $"{track.BitDepth.Value}-bit · {track.SampleRateHz.Value / 1000:0.0} kHz"));
        }
        else if (track.SampleRateHz is > 0)
        {
            parts.Add(string.Create(CultureInfo.InvariantCulture, $"{track.SampleRateHz.Value / 1000:0.0} kHz"));
        }
        return parts.Count == 0 ? null : string.Join(" · ", parts);
    }

    public static RepeatMode Repeat(LoopMode mode) => mode switch
    {
        LoopMode.ListRepeat or LoopMode.RepeatShuffle => RepeatMode.List,
        LoopMode.SingleRepeat or LoopMode.SingleRepeatShuffle => RepeatMode.Single,
        _ => RepeatMode.Off
    };

    public static bool IsShuffle(LoopMode mode) =>
        mode is LoopMode.Shuffle or LoopMode.RepeatShuffle or LoopMode.SingleRepeatShuffle;

    public static LoopMode NextLoop(LoopMode mode) => mode switch
    {
        LoopMode.SingleRepeat => LoopMode.Default,
        LoopMode.ListRepeat => LoopMode.SingleRepeat,
        LoopMode.Shuffle => LoopMode.RepeatShuffle,
        LoopMode.RepeatShuffle => LoopMode.SingleRepeatShuffle,
        LoopMode.Default => LoopMode.ListRepeat,
        LoopMode.SingleRepeatShuffle => LoopMode.Shuffle,
        _ => LoopMode.Shuffle
    };

    public static LoopMode NextShuffle(LoopMode mode) => mode switch
    {
        LoopMode.SingleRepeat => LoopMode.SingleRepeatShuffle,
        LoopMode.ListRepeat => LoopMode.RepeatShuffle,
        LoopMode.Shuffle => LoopMode.Default,
        LoopMode.RepeatShuffle => LoopMode.ListRepeat,
        LoopMode.Default => LoopMode.Shuffle,
        LoopMode.SingleRepeatShuffle => LoopMode.SingleRepeat,
        _ => LoopMode.Shuffle
    };
}
