using System.Collections.Concurrent;
using System.Text.Json;
using AudioStar.Core;
using Microsoft.Extensions.Logging;

namespace AudioStar.Sources.YtDlp;

public abstract class YtDlpPlaylistSource(
    IYtDlp ytDlp,
    ISettingsStore settings,
    IMediaServer mediaServer,
    IRecentlyPlayed recentlyPlayed,
    IPlaylistCache playlistCache,
    ILogger logger) : IMusicSource, IEditablePlaylistSource
{
    protected static readonly TimeSpan ListTimeout = TimeSpan.FromMinutes(3);
    protected static readonly TimeSpan PeekTimeout = TimeSpan.FromSeconds(60);

    private readonly ConcurrentDictionary<string, byte> _added = new();
    private readonly ConcurrentDictionary<string, byte> _refreshing = new();
    private readonly ConcurrentDictionary<string, IReadOnlyList<SourceTrack>> _shown = new();
    private SourceStatus _status = new(SourceConnectionState.Disconnected, null, null);

    protected IYtDlp YtDlp { get; } = ytDlp;
    protected ISettingsStore Settings { get; } = settings;
    protected ILogger Logger { get; } = logger;
    protected ConcurrentDictionary<string, SourcePlaylist> Pasted { get; } = new();

    public abstract string Id { get; }
    public abstract string DisplayName { get; }

    protected virtual string QueueSourceName => DisplayName;

    public SourceStatus Status => _status;

    public event EventHandler<SourceStatus>? StatusChanged;

    public abstract Task<SourceStatus> ConnectAsync(CancellationToken cancellationToken = default);

    public virtual Task<SourceStatus> ConnectSilentlyAsync(CancellationToken cancellationToken = default) => ConnectAsync(cancellationToken);

    public abstract Task<IReadOnlyList<SourcePlaylist>> GetPlaylistsAsync(CancellationToken cancellationToken = default);

    public abstract Task<SourcePlaylist?> AddPlaylistByUrlAsync(string url, CancellationToken cancellationToken = default);

    protected abstract List<string> PastedUrls { get; }

    protected abstract string? NormalizeUrl(string url);

    protected abstract Task<SourcePlaylist> PeekAddedAsync(string url, CancellationToken cancellationToken);

    protected virtual bool IsLibraryPlaylist(string playlistId) => false;

    protected abstract IReadOnlyList<SourceTrack> MapTracks(JsonElement root);

    protected abstract SourcePlaylist MapPlaylistHeader(JsonElement root, string url);

    protected virtual IReadOnlyList<string> TrackArguments() => [];

    protected virtual Task<IReadOnlyList<SourceTrack>?> GetOwnTracksAsync(SourcePlaylist playlist, CancellationToken cancellationToken) =>
        Task.FromResult<IReadOnlyList<SourceTrack>?>(null);

    protected virtual Task<IReadOnlyList<SourceTrack>> EnrichTracksAsync(IReadOnlyList<SourceTrack> tracks, CancellationToken cancellationToken) =>
        Task.FromResult(tracks);

    public virtual Task DisconnectAsync(CancellationToken cancellationToken = default)
    {
        SetStatus(SourceConnectionState.Disconnected, null, null);
        return Task.CompletedTask;
    }

    public bool IsAdded(SourcePlaylist playlist) =>
        !IsLibraryPlaylist(playlist.Id) && PastedUrls.Any(u => (NormalizeUrl(u) ?? u) == playlist.Id);

    public async Task RemovePlaylistAsync(SourcePlaylist playlist, CancellationToken cancellationToken = default)
    {
        PastedUrls.RemoveAll(u => (NormalizeUrl(u) ?? u) == playlist.Id);
        await Settings.SaveAsync(cancellationToken);
        await ForgetAsync(playlist.Id, cancellationToken);
    }

    public async Task<SourcePlaylist?> ChangePlaylistUrlAsync(SourcePlaylist playlist, string url, CancellationToken cancellationToken = default)
    {
        var normalized = NormalizeUrl(url);
        if (normalized is null)
        {
            return null;
        }
        if (normalized == playlist.Id)
        {
            return playlist;
        }
        var replacement = await PeekAddedAsync(normalized, cancellationToken);
        var urls = PastedUrls;
        var index = urls.FindIndex(u => (NormalizeUrl(u) ?? u) == playlist.Id);
        if (index < 0)
        {
            urls.Add(normalized);
            index = urls.Count - 1;
        }
        else
        {
            urls[index] = normalized;
        }
        var kept = urls.Where((u, i) => i == index || (NormalizeUrl(u) ?? u) != normalized).ToList();
        urls.Clear();
        urls.AddRange(kept);
        await Settings.SaveAsync(cancellationToken);
        await ForgetAsync(playlist.Id, cancellationToken);
        Pasted[normalized] = replacement;
        await StoreHeaderAsync(replacement, cancellationToken);
        return replacement;
    }

    public async Task<IReadOnlyList<SourceTrack>> GetTracksAsync(SourcePlaylist playlist, CancellationToken cancellationToken = default)
    {
        var tracks = await GetOwnTracksAsync(playlist, cancellationToken)
            ?? (_added.ContainsKey(playlist.Id)
                ? await GetAddedTracksAsync(playlist, cancellationToken)
                : (await FetchAsync(playlist, false, cancellationToken)).Tracks);
        _shown[playlist.Id] = tracks;
        return tracks;
    }

    public async Task PlayAsync(ISpeakerSession speaker, SourcePlaylist playlist, int startIndex = 0, CancellationToken cancellationToken = default)
    {
        var tracks = _shown.TryGetValue(playlist.Id, out var shown) && shown.Count > 0 ? shown : await GetTracksAsync(playlist, cancellationToken);
        if (tracks.Count == 0)
        {
            throw new InvalidOperationException($"'{playlist.Title}' has no playable tracks.");
        }
        var items = tracks
            .Select(t => new PlayItem(t.Id, t.Title, t.Artist, t.Album, mediaServer.GetStreamUri(Id, t.Id), t.ArtworkUri, t.Duration))
            .ToList();
        var start = Math.Clamp(startIndex, 0, items.Count - 1);
        var artwork = playlist.ArtworkUri ?? items[0].ArtworkUri;
        var request = new PlayRequest(playlist.Title, QueueSourceName, items, start, artwork);
        await speaker.Controller.PlayAsync(request, cancellationToken);
        await recentlyPlayed.AddAsync(RecentKinds.Request, Id, playlist.Title, $"{DisplayName}, {items.Count} tracks", artwork, JsonSerializer.Serialize(request), cancellationToken);
        Logger.LogInformation("Playing {Playlist} ({Count} tracks) on {Speaker}", playlist.Title, items.Count, speaker.Info.Name);
    }

    protected void SetStatus(SourceConnectionState state, string? account, string? message)
    {
        _status = new SourceStatus(state, account, message);
        StatusChanged?.Invoke(this, _status);
    }

    protected async Task<SourcePlaylist> PeekPlaylistAsync(string url, Func<JsonElement, string, SourcePlaylist> map, IReadOnlyList<string> extraArguments, CancellationToken cancellationToken)
    {
        var arguments = new List<string> { "-J", "--flat-playlist", "--playlist-items", "1" };
        arguments.AddRange(extraArguments);
        arguments.Add(url);
        using var result = await YtDlp.GetJsonAsync(arguments, PeekTimeout, cancellationToken);
        return map(result.Root, url);
    }

    protected async Task<SourcePlaylist> CachedOrPeekAsync(string url, Func<Task<SourcePlaylist>> peek, CancellationToken cancellationToken)
    {
        _added[url] = 0;
        if (await playlistCache.GetAsync(Id, url, cancellationToken) is { } hit)
        {
            return hit.Playlist;
        }
        var playlist = await peek();
        await StoreHeaderAsync(playlist, cancellationToken);
        return playlist;
    }

    protected async Task StoreHeaderAsync(SourcePlaylist playlist, CancellationToken cancellationToken)
    {
        _added[playlist.Id] = 0;
        var existing = await playlistCache.GetAsync(Id, playlist.Id, cancellationToken);
        await playlistCache.SaveAsync(new CachedPlaylist(playlist, existing?.Tracks, existing?.FetchedAt ?? DateTimeOffset.UtcNow), cancellationToken);
    }

    private async Task ForgetAsync(string playlistId, CancellationToken cancellationToken)
    {
        await playlistCache.RemoveAsync(Id, playlistId, cancellationToken);
        _added.TryRemove(playlistId, out _);
        _shown.TryRemove(playlistId, out _);
        Pasted.TryRemove(playlistId, out _);
    }

    private async Task<IReadOnlyList<SourceTrack>> GetAddedTracksAsync(SourcePlaylist playlist, CancellationToken cancellationToken)
    {
        if (await playlistCache.GetAsync(Id, playlist.Id, cancellationToken) is { Tracks: { Count: > 0 } cached })
        {
            if (_refreshing.TryAdd(playlist.Id, 0))
            {
                _ = Task.Run(() => RefreshAsync(playlist), CancellationToken.None);
            }
            return cached;
        }
        var fetch = await FetchAsync(playlist, true, cancellationToken);
        await SaveFetchAsync(playlist, fetch, cancellationToken);
        return fetch.Tracks;
    }

    private async Task RefreshAsync(SourcePlaylist playlist)
    {
        try
        {
            var fetch = await FetchAsync(playlist, true, CancellationToken.None);
            if (fetch.Tracks.Count > 0)
            {
                await SaveFetchAsync(playlist, fetch, CancellationToken.None);
            }
        }
        catch (Exception exception)
        {
            Logger.LogWarning("Playlist {Playlist} could not be refreshed: {Message}", playlist.Title, exception.Message);
        }
        finally
        {
            _refreshing.TryRemove(playlist.Id, out _);
        }
    }

    private Task SaveFetchAsync(SourcePlaylist playlist, PlaylistFetch fetch, CancellationToken cancellationToken) =>
        playlistCache.SaveAsync(new CachedPlaylist(fetch.Header ?? playlist, fetch.Tracks, DateTimeOffset.UtcNow), cancellationToken);

    private async Task<PlaylistFetch> FetchAsync(SourcePlaylist playlist, bool withHeader, CancellationToken cancellationToken)
    {
        var arguments = new List<string> { "-J", "--flat-playlist", "--ignore-errors" };
        arguments.AddRange(TrackArguments());
        arguments.Add(playlist.Id);
        using var result = await YtDlp.GetJsonAsync(arguments, ListTimeout, cancellationToken);
        var tracks = MapTracks(result.Root);
        if (tracks.Count == 0 && YtDlpErrors.IsOutdated(result.StdErr))
        {
            throw new YtDlpException(YtDlpErrors.OutdatedHint, result.StdErr);
        }
        tracks = await EnrichTracksAsync(tracks, cancellationToken);
        return new PlaylistFetch(tracks, withHeader ? MapPlaylistHeader(result.Root, playlist.Id) : null);
    }

    private sealed record PlaylistFetch(IReadOnlyList<SourceTrack> Tracks, SourcePlaylist? Header);
}
