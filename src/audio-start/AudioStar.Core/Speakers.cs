namespace AudioStar.Core;

public sealed record SpeakerInfo(string Id, string Name, string IpAddress, int UpnpPort, string Model, string Firmware);

public enum TransportState { Unknown, NoMedia, Stopped, Transitioning, Playing, Paused }

public enum LoopMode { ListRepeat = 0, SingleRepeat = 1, RepeatShuffle = 2, Shuffle = 3, Default = 4, SingleRepeatShuffle = 5 }

public sealed record TrackInfo(
    string? Title,
    string? Artist,
    string? Album,
    Uri? ArtworkUri,
    TimeSpan Duration,
    int? BitDepth,
    double? SampleRateHz,
    double? BitrateKbps,
    string? TrackUri);

public sealed record PlaybackState(
    TransportState State,
    TrackInfo? Track,
    TimeSpan Position,
    int Volume,
    bool Muted,
    LoopMode LoopMode,
    string? TrackSource,
    string? PlayMedium)
{
    public static PlaybackState Empty { get; } = new(TransportState.Unknown, null, TimeSpan.Zero, 0, false, LoopMode.Default, null, null);
}

public sealed record PlayItem(string Id, string Title, string? Artist, string? Album, Uri StreamUri, Uri? ArtworkUri, TimeSpan? Duration);

public sealed record PlayRequest(string ListName, string SourceName, IReadOnlyList<PlayItem> Items, int StartIndex = 0, Uri? ListArtworkUri = null);

public sealed record QueueTrack(int Index, string Title, string? Artist, string? Album, Uri? ArtworkUri, TimeSpan? Duration);

public sealed record SpeakerQueue(string Name, string? SourceName, int CurrentIndex, IReadOnlyList<QueueTrack> Tracks);

public sealed record Preset(int Number, string Name, string? Source, Uri? PictureUri, bool IsEmpty);

public sealed record AudioInput(string Mode, string Title);

public interface ISpeakerHub
{
    IReadOnlyList<ISpeakerSession> Speakers { get; }
    event EventHandler<ISpeakerSession>? SpeakerAdded;
    event EventHandler<ISpeakerSession>? SpeakerRemoved;
    Task StartAsync(CancellationToken cancellationToken);
    Task StopAsync(CancellationToken cancellationToken);
    Task RefreshAsync(CancellationToken cancellationToken = default);
    Task<ISpeakerSession?> AddByIpAsync(string ipAddress, CancellationToken cancellationToken = default);
    ISpeakerSession? Find(string speakerId);
}

public interface ISpeakerSession
{
    SpeakerInfo Info { get; }
    PlaybackState State { get; }
    string? LeaderId { get; }
    IReadOnlyList<string> FollowerIds { get; }
    ISpeakerController Controller { get; }
    event EventHandler<PlaybackState>? StateChanged;
    event EventHandler? GroupChanged;
}

public interface ISpeakerController
{
    Task PlayAsync(CancellationToken cancellationToken = default);
    Task PauseAsync(CancellationToken cancellationToken = default);
    Task NextAsync(CancellationToken cancellationToken = default);
    Task PreviousAsync(CancellationToken cancellationToken = default);
    Task SeekAsync(TimeSpan position, CancellationToken cancellationToken = default);
    Task SetVolumeAsync(int volume, CancellationToken cancellationToken = default);
    Task SetMuteAsync(bool muted, CancellationToken cancellationToken = default);
    Task SetLoopModeAsync(LoopMode mode, CancellationToken cancellationToken = default);
    Task<PlaybackState> GetPlaybackStateAsync(CancellationToken cancellationToken = default);

    Task PlayAsync(PlayRequest request, CancellationToken cancellationToken = default);
    Task PlayUrlAsync(string title, Uri streamUri, Uri? artworkUri, string sourceName, CancellationToken cancellationToken = default);

    Task<SpeakerQueue?> GetQueueAsync(CancellationToken cancellationToken = default);
    Task PlayQueueIndexAsync(int index, CancellationToken cancellationToken = default);
    Task RemoveQueueIndexAsync(int index, CancellationToken cancellationToken = default);

    Task<IReadOnlyList<Preset>> GetPresetsAsync(CancellationToken cancellationToken = default);
    Task PlayPresetAsync(int number, CancellationToken cancellationToken = default);
    Task SaveCurrentAsPresetAsync(int number, CancellationToken cancellationToken = default);
    Task DeletePresetAsync(int number, CancellationToken cancellationToken = default);

    Task<IReadOnlyList<AudioInput>> GetInputsAsync(CancellationToken cancellationToken = default);
    Task SwitchInputAsync(string mode, CancellationToken cancellationToken = default);

    Task<string> SendCommandAsync(string command, CancellationToken cancellationToken = default);
    Task<string> PostCommandAsync(string command, string jsonPayload, CancellationToken cancellationToken = default);
}
