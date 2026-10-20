namespace AudioStar.Core;

public static class SourceIds
{
    public const string YouTube = "youtube";
    public const string SoundCloud = "soundcloud";
    public const string Spotify = "spotify";
    public const string Radio = "radio";
    public const string Library = "library";
    public const string HomeShare = "homeshare";
}

public enum SourceConnectionState { NotConfigured, Disconnected, Connecting, Connected, Error }

public sealed record SourceStatus(SourceConnectionState State, string? AccountName, string? Message);

public sealed record SourcePlaylist(string SourceId, string Id, string Title, string? Owner, int? TrackCount, Uri? ArtworkUri, Uri? WebUri);

public sealed record SourceTrack(string SourceId, string Id, string Title, string? Artist, string? Album, TimeSpan? Duration, Uri? ArtworkUri);

public interface IMusicSource
{
    string Id { get; }
    string DisplayName { get; }
    SourceStatus Status { get; }
    event EventHandler<SourceStatus>? StatusChanged;
    Task<SourceStatus> ConnectAsync(CancellationToken cancellationToken = default);
    Task<SourceStatus> ConnectSilentlyAsync(CancellationToken cancellationToken = default) => ConnectAsync(cancellationToken);
    Task DisconnectAsync(CancellationToken cancellationToken = default);
    Task<IReadOnlyList<SourcePlaylist>> GetPlaylistsAsync(CancellationToken cancellationToken = default);
    Task<SourcePlaylist?> AddPlaylistByUrlAsync(string url, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<SourceTrack>> GetTracksAsync(SourcePlaylist playlist, CancellationToken cancellationToken = default);
    Task PlayAsync(ISpeakerSession speaker, SourcePlaylist playlist, int startIndex = 0, CancellationToken cancellationToken = default);
}

public interface IEditablePlaylistSource
{
    bool IsAdded(SourcePlaylist playlist);
    Task RemovePlaylistAsync(SourcePlaylist playlist, CancellationToken cancellationToken = default);
    Task<SourcePlaylist?> ChangePlaylistUrlAsync(SourcePlaylist playlist, string url, CancellationToken cancellationToken = default);
}

public sealed record RadioStation(
    string Id,
    string Name,
    Uri StreamUri,
    Uri? LogoUri,
    string? Country,
    string? CountryCode,
    IReadOnlyList<string> Tags,
    int? Bitrate,
    string? Codec);

public sealed record RadioSection(string Key, string Title, IReadOnlyList<RadioStation> Stations);

public interface IRadioDirectory
{
    IReadOnlyList<RadioStation> Favorites { get; }
    event EventHandler? FavoritesChanged;
    Task<IReadOnlyList<RadioSection>> GetHomeAsync(CancellationToken cancellationToken = default);
    Task<IReadOnlyList<RadioStation>> SearchAsync(string query, int offset = 0, int limit = 50, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<RadioStation>> GetByTagAsync(string tag, int offset = 0, int limit = 50, CancellationToken cancellationToken = default);
    Task SetFavoriteAsync(RadioStation station, bool favorite, CancellationToken cancellationToken = default);
    Task PlayAsync(ISpeakerSession speaker, RadioStation station, CancellationToken cancellationToken = default);
}
