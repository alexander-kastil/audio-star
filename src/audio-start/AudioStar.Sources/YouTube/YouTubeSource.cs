using System.Text.Json;
using AudioStar.Core;
using AudioStar.Sources.YtDlp;
using Microsoft.Extensions.Logging;

namespace AudioStar.Sources.YouTube;

public sealed class YouTubeSource(
    IYtDlp ytDlp,
    ISettingsStore settings,
    IMediaServer mediaServer,
    IRecentlyPlayed recentlyPlayed,
    IPlaylistCache playlistCache,
    ILogger<YouTubeSource> logger) : YtDlpPlaylistSource(ytDlp, settings, mediaServer, recentlyPlayed, playlistCache, logger)
{

    private const string HistoryUrl = "https://www.youtube.com/feed/history";
    private const string LibraryUrl = "https://www.youtube.com/feed/playlists";
    private static readonly TimeSpan LibraryLifetime = TimeSpan.FromMinutes(5);

    private IReadOnlyList<SourcePlaylist> _library = [];
    private DateTimeOffset _libraryLoadedAt = DateTimeOffset.MinValue;
    private Uri? _historyArtwork;

    public override string Id => SourceIds.YouTube;
    public override string DisplayName => "YouTube";

    public override async Task<SourceStatus> ConnectAsync(CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(Settings.Current.YouTubeCookieSource))
        {
            SetStatus(SourceConnectionState.Connected, null, null);
            return Status;
        }
        SetStatus(SourceConnectionState.Connecting, null, null);
        try
        {
            var (playlists, account) = await LoadLibraryAsync(cancellationToken);
            if (playlists.Count == 0)
            {
                SetStatus(SourceConnectionState.Error, null, "No playlists were found. The cookies are probably not signed in to YouTube.");
                return Status;
            }
            SetStatus(SourceConnectionState.Connected, account, $"{playlists.Count} playlists in your library.");
        }
        catch (YtDlpException exception)
        {
            Logger.LogWarning("YouTube connect failed: {Message}", exception.Message);
            SetStatus(SourceConnectionState.Error, null, exception.Message);
        }
        return Status;
    }

    public override Task DisconnectAsync(CancellationToken cancellationToken = default)
    {
        _library = [];
        _libraryLoadedAt = DateTimeOffset.MinValue;
        _historyArtwork = null;
        return base.DisconnectAsync(cancellationToken);
    }

    public override async Task<IReadOnlyList<SourcePlaylist>> GetPlaylistsAsync(CancellationToken cancellationToken = default)
    {
        var result = new List<SourcePlaylist>();
        if (!string.IsNullOrWhiteSpace(Settings.Current.YouTubeCookieSource))
        {
            var historyTask = HistoryCardAsync(cancellationToken);
            if (DateTimeOffset.UtcNow - _libraryLoadedAt > LibraryLifetime)
            {
                try
                {
                    await LoadLibraryAsync(cancellationToken);
                }
                catch (YtDlpException exception)
                {
                    Logger.LogWarning("YouTube library could not be loaded: {Message}", exception.Message);
                    SetStatus(SourceConnectionState.Error, null, exception.Message);
                }
            }
            result.Add(await historyTask);
            result.AddRange(_library);
        }

        var known = result.Select(p => p.Id).ToHashSet();
        var urls = Settings.Current.YouTubePlaylistUrls.Select(u => YouTubeMapper.NormalizePlaylistUrl(u) ?? u).Distinct().Where(u => !known.Contains(u)).ToList();
        var loaded = await Task.WhenAll(urls.Select(url => PastedPlaylistAsync(url, cancellationToken)));
        result.AddRange(loaded.Where(p => p is not null)!);
        return result;
    }

    public override async Task<SourcePlaylist?> AddPlaylistByUrlAsync(string url, CancellationToken cancellationToken = default)
    {
        var normalized = YouTubeMapper.NormalizePlaylistUrl(url);
        if (normalized is null)
        {
            return null;
        }
        var playlist = await PeekPlaylistAsync(normalized, YouTubeMapper.MapPlaylistHeader, YtDlpCookies.Arguments(Settings.Current.YouTubeCookieSource), cancellationToken);
        Pasted[normalized] = playlist;
        await StoreHeaderAsync(playlist, cancellationToken);
        var saved = Settings.Current.YouTubePlaylistUrls;
        if (!saved.Select(u => YouTubeMapper.NormalizePlaylistUrl(u) ?? u).Contains(normalized))
        {
            saved.Add(normalized);
            await Settings.SaveAsync(cancellationToken);
        }
        return playlist;
    }

    protected override List<string> PastedUrls => Settings.Current.YouTubePlaylistUrls;

    protected override string? NormalizeUrl(string url) => YouTubeMapper.NormalizePlaylistUrl(url);

    protected override Task<SourcePlaylist> PeekAddedAsync(string url, CancellationToken cancellationToken) =>
        PeekPlaylistAsync(url, YouTubeMapper.MapPlaylistHeader, YtDlpCookies.Arguments(Settings.Current.YouTubeCookieSource), cancellationToken);

    protected override bool IsLibraryPlaylist(string playlistId) => playlistId == HistoryUrl || _library.Any(p => p.Id == playlistId);

    protected override IReadOnlyList<SourceTrack> MapTracks(JsonElement root) => YouTubeMapper.MapTracks(root);

    protected override SourcePlaylist MapPlaylistHeader(JsonElement root, string url) => YouTubeMapper.MapPlaylistHeader(root, url);

    protected override IReadOnlyList<string> TrackArguments() => YtDlpCookies.Arguments(Settings.Current.YouTubeCookieSource);

    private async Task<SourcePlaylist> HistoryCardAsync(CancellationToken cancellationToken)
    {
        if (_historyArtwork is null)
        {
            try
            {
                var header = await PeekPlaylistAsync(HistoryUrl, YouTubeMapper.MapPlaylistHeader, TrackArguments(), cancellationToken);
                _historyArtwork = header.ArtworkUri;
            }
            catch (YtDlpException exception)
            {
                Logger.LogWarning("YouTube history cover could not be loaded: {Message}", exception.Message);
            }
        }
        return new SourcePlaylist(Id, HistoryUrl, "History", null, null, _historyArtwork, new Uri(HistoryUrl));
    }

    private async Task<(IReadOnlyList<SourcePlaylist> Playlists, string? Account)> LoadLibraryAsync(CancellationToken cancellationToken)
    {
        var arguments = new List<string> { "-J", "--flat-playlist", "--ignore-errors" };
        arguments.AddRange(YtDlpCookies.Arguments(Settings.Current.YouTubeCookieSource));
        arguments.Add(LibraryUrl);
        using var result = await YtDlp.GetJsonAsync(arguments, ListTimeout, cancellationToken);
        var playlists = YouTubeMapper.MapLibrary(result.Root);
        if (playlists.Count == 0 && YtDlpErrors.IsOutdated(result.StdErr))
        {
            throw new YtDlpException(YtDlpErrors.OutdatedHint, result.StdErr);
        }
        _library = playlists;
        _libraryLoadedAt = DateTimeOffset.UtcNow;
        return (playlists, result.Root.Str("uploader") ?? result.Root.Str("channel"));
    }

    private async Task<SourcePlaylist?> PastedPlaylistAsync(string url, CancellationToken cancellationToken)
    {
        if (Pasted.TryGetValue(url, out var cached))
        {
            return cached;
        }
        try
        {
            var playlist = await CachedOrPeekAsync(url, () => PeekPlaylistAsync(url, YouTubeMapper.MapPlaylistHeader, YtDlpCookies.Arguments(Settings.Current.YouTubeCookieSource), cancellationToken), cancellationToken);
            Pasted[url] = playlist;
            return playlist;
        }
        catch (YtDlpException exception)
        {
            Logger.LogWarning("Playlist {Url} could not be read: {Message}", url, exception.Message);
            return new SourcePlaylist(SourceIds.YouTube, url, url, null, null, null, Uri.TryCreate(url, UriKind.Absolute, out var uri) ? uri : null);
        }
    }
}
