namespace AudioStar.Core;

public sealed record LibraryTrack(
    long Id,
    string Path,
    string Title,
    string? Artist,
    string? AlbumArtist,
    string? Album,
    string? Genre,
    int? TrackNumber,
    int? DiscNumber,
    int? Year,
    TimeSpan Duration,
    bool HasCover);

public sealed record LibraryAlbum(string Album, string AlbumArtist, int TrackCount, int? Year, string? CoverTrackPath);

public sealed record LibraryArtist(string Name, int AlbumCount, int TrackCount);

public sealed record LibraryGenre(string Name, int TrackCount);

public sealed record LibraryQuery(string? Search = null, string? Artist = null, string? Album = null, string? Genre = null, int Offset = 0, int Limit = 500);

public sealed record LibraryScanProgress(int FilesSeen, int FilesImported, string? CurrentPath, bool Completed);

public interface IMusicLibrary
{
    IReadOnlyList<string> Folders { get; }
    event EventHandler? LibraryChanged;
    Task AddFolderAsync(string path, CancellationToken cancellationToken = default);
    Task RemoveFolderAsync(string path, CancellationToken cancellationToken = default);
    Task ScanAsync(IProgress<LibraryScanProgress>? progress, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<LibraryAlbum>> GetAlbumsAsync(string? search = null, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<LibraryArtist>> GetArtistsAsync(string? search = null, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<LibraryGenre>> GetGenresAsync(CancellationToken cancellationToken = default);
    Task<IReadOnlyList<LibraryTrack>> GetTracksAsync(LibraryQuery query, CancellationToken cancellationToken = default);
    PlayItem ToPlayItem(LibraryTrack track);
}

public interface IMediaServer
{
    Uri BaseUri { get; }
    Task StartAsync(CancellationToken cancellationToken);
    Task StopAsync(CancellationToken cancellationToken);
    Uri GetFileUri(string absolutePath);
    Uri GetCoverUri(string absolutePath);
    Uri GetStreamUri(string sourceId, string itemId);
}

public sealed record ResolvedStream(
    Uri Url,
    string ContentType,
    IReadOnlyDictionary<string, string>? Headers = null,
    bool RequiresTranscode = false,
    long? Length = null,
    TimeSpan? Duration = null);

public interface IStreamResolver
{
    string SourceId { get; }
    Task<ResolvedStream> ResolveAsync(string itemId, CancellationToken cancellationToken = default);
}

public interface IDlnaServer
{
    bool IsRunning { get; }
    Task StartAsync(CancellationToken cancellationToken);
    Task StopAsync(CancellationToken cancellationToken);
}

public sealed record DlnaServerInfo(string Id, string Name, Uri DescriptionUri);

public sealed record DlnaItem(
    string Id,
    string ParentId,
    string Title,
    bool IsContainer,
    string? Artist,
    string? Album,
    Uri? ResourceUri,
    Uri? ArtworkUri,
    TimeSpan? Duration);

public interface IHomeShareBrowser
{
    IReadOnlyList<DlnaServerInfo> Servers { get; }
    event EventHandler? ServersChanged;
    Task StartAsync(CancellationToken cancellationToken);
    Task<IReadOnlyList<DlnaItem>> BrowseAsync(DlnaServerInfo server, string objectId, CancellationToken cancellationToken = default);
}

public static class RecentKinds
{
    public const string Request = "request";
    public const string SourcePlaylist = "source-playlist";
}

public sealed record RecentItem(
    long Id,
    string Kind,
    string SourceId,
    string Title,
    string? Subtitle,
    Uri? ArtworkUri,
    DateTimeOffset PlayedAt,
    string PayloadJson);

public interface IRecentlyPlayed
{
    event EventHandler? Changed;
    Task AddAsync(string kind, string sourceId, string title, string? subtitle, Uri? artworkUri, string payloadJson, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<RecentItem>> GetAsync(int limit = 100, CancellationToken cancellationToken = default);
    Task RemoveAsync(long id, CancellationToken cancellationToken = default);
    Task ReplayAsync(ISpeakerSession speaker, RecentItem item, CancellationToken cancellationToken = default);
}
