using AudioStar.Core;

namespace AudioStar.Sources.YtDlp;

public sealed record CachedPlaylist(SourcePlaylist Playlist, IReadOnlyList<SourceTrack>? Tracks, DateTimeOffset FetchedAt);

public interface IPlaylistCache
{
    Task<CachedPlaylist?> GetAsync(string sourceId, string playlistId, CancellationToken cancellationToken = default);
    Task SaveAsync(CachedPlaylist entry, CancellationToken cancellationToken = default);
    Task RemoveAsync(string sourceId, string playlistId, CancellationToken cancellationToken = default);
}
