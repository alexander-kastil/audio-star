using System.Globalization;

namespace AudioStar.Speakers.Events;

internal sealed record LastChangeDelta(
    TransportState? State,
    TrackInfo? Track,
    string? TrackUri,
    TimeSpan? Duration,
    TimeSpan? Position,
    int? Volume,
    bool? Muted,
    LoopMode? LoopMode,
    string? TrackSource,
    string? PlayMedium,
    bool GroupSignal)
{
    public PlaybackState ApplyTo(PlaybackState state)
    {
        var next = state;
        if (State is { } transport)
        {
            next = next with { State = transport };
            if (transport == TransportState.NoMedia)
            {
                next = next with { Track = null, Position = TimeSpan.Zero };
            }
        }
        if (Track is not null)
        {
            next = next with { Track = Track };
        }
        if (next.Track is not null)
        {
            var track = next.Track;
            if (!string.IsNullOrWhiteSpace(TrackUri))
            {
                track = track with { TrackUri = TrackUri };
            }
            if (Duration is { } duration && duration > TimeSpan.Zero && (Track is null || track.Duration == TimeSpan.Zero))
            {
                track = track with { Duration = duration };
            }
            next = next with { Track = track };
        }
        if (Position is { } position)
        {
            next = next with { Position = position };
        }
        if (Volume is { } volume)
        {
            next = next with { Volume = volume };
        }
        if (Muted is { } muted)
        {
            next = next with { Muted = muted };
        }
        if (LoopMode is { } loop)
        {
            next = next with { LoopMode = loop };
        }
        if (TrackSource is not null)
        {
            next = next with { TrackSource = TrackSource.Length == 0 ? null : TrackSource };
        }
        if (PlayMedium is not null)
        {
            next = next with { PlayMedium = PlayMedium.Length == 0 ? null : PlayMedium };
        }
        return next;
    }
}

internal static class PlaybackMapper
{
    public static TransportState ParseTransportState(string? text)
    {
        return text?.Trim().ToUpperInvariant() switch
        {
            "PLAYING" => TransportState.Playing,
            "PAUSED_PLAYBACK" or "PAUSED_RECORDING" or "PAUSED" => TransportState.Paused,
            "STOPPED" => TransportState.Stopped,
            "TRANSITIONING" or "BUFFERING" or "LOADING" => TransportState.Transitioning,
            "NO_MEDIA_PRESENT" => TransportState.NoMedia,
            _ => TransportState.Unknown
        };
    }

    public static LoopMode ParseLoopMode(string? text)
    {
        return int.TryParse(text, NumberStyles.Integer, CultureInfo.InvariantCulture, out var value) && Enum.IsDefined(typeof(LoopMode), value)
            ? (LoopMode)value
            : LoopMode.Default;
    }

    public static PlaybackState FromGetInfoEx(IReadOnlyDictionary<string, string> reply, string deviceIp)
    {
        string Get(string key) => reply.TryGetValue(key, out var value) ? value : "";
        var trackUri = Get("TrackURI");
        var track = DidlParser.ParseTrack(Get("TrackMetaData"), trackUri, deviceIp);
        var duration = ClockText.Parse(Get("TrackDuration"));
        if (track is null && !string.IsNullOrWhiteSpace(trackUri))
        {
            track = new TrackInfo(null, null, null, null, duration, null, null, null, trackUri);
        }
        if (track is not null && track.Duration == TimeSpan.Zero && duration > TimeSpan.Zero)
        {
            track = track with { Duration = duration };
        }
        var volume = ParseVolume(Get("CurrentVolume")) ?? 0;
        return new PlaybackState(
            ParseTransportState(Get("CurrentTransportState")),
            track,
            ClockText.Parse(Get("RelTime")),
            volume,
            Get("CurrentMute") == "1",
            ParseLoopMode(Get("LoopMode")),
            NullIfEmpty(Get("TrackSource")),
            NullIfEmpty(Get("PlayMedium")));
    }

    public static LastChangeDelta? ParseLastChange(string? lastChangeXml, string deviceIp)
    {
        if (string.IsNullOrWhiteSpace(lastChangeXml))
        {
            return null;
        }
        XDocument document;
        try
        {
            document = XDocument.Parse(lastChangeXml);
        }
        catch (System.Xml.XmlException)
        {
            return null;
        }

        string? Val(string name)
        {
            var element = document.Descendants().FirstOrDefault(e => e.Name.LocalName == name);
            return element is null ? null : element.Attribute("val")?.Value ?? "";
        }

        var state = Val("TransportState");
        var metadata = Val("CurrentTrackMetaData");
        var trackUri = Val("CurrentTrackURI");
        var duration = Val("CurrentTrackDuration");
        var seek = Val("A_ARG_TYPE_SeekTarget");
        var volume = Val("Volume");
        var mute = Val("Mute");
        var loop = Val("LoopMode") ?? Val("LoopMpde");
        var group = document.Descendants().Any(e => e.Name.LocalName is "Slave" or "lpmrm")
            || document.Descendants().Any(e => e.Name.LocalName == "commonevent" && e.ToString().Contains("lpmrm", StringComparison.Ordinal));

        return new LastChangeDelta(
            state is null ? null : ParseTransportState(state),
            string.IsNullOrWhiteSpace(metadata) ? null : DidlParser.ParseTrack(metadata, trackUri, deviceIp),
            NullIfEmpty(trackUri),
            string.IsNullOrWhiteSpace(duration) ? null : ClockText.Parse(duration),
            string.IsNullOrWhiteSpace(seek) ? null : ClockText.Parse(seek),
            string.IsNullOrWhiteSpace(volume) ? null : ParseVolume(volume),
            string.IsNullOrWhiteSpace(mute) ? null : mute == "1",
            string.IsNullOrWhiteSpace(loop) ? null : ParseLoopMode(loop),
            Val("TrackSource"),
            Val("PlaybackStorageMedium"),
            group);
    }

    private static int? ParseVolume(string text)
    {
        return double.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out var value)
            ? Math.Clamp((int)Math.Round(value), 0, 100)
            : null;
    }

    private static string? NullIfEmpty(string? value) => string.IsNullOrWhiteSpace(value) ? null : value;
}
