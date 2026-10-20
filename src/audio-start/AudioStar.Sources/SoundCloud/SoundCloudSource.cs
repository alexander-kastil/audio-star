using System.Collections.Concurrent;
using System.Text.Json;
using AudioStar.Core;
using AudioStar.Sources.YtDlp;
using Microsoft.Extensions.Logging;

namespace AudioStar.Sources.SoundCloud;

public sealed class SoundCloudSource(
    IYtDlp ytDlp,
    ISettingsStore settings,
    IMediaServer mediaServer,
    IRecentlyPlayed recentlyPlayed,
    IPlaylistCache playlistCache,
    SoundCloudSession session,
    IWebSignIn webSignIn,
    ILogger<SoundCloudSource> logger) : YtDlpPlaylistSource(ytDlp, settings, mediaServer, recentlyPlayed, playlistCache, logger)
{
    private static readonly Uri SiteUri = new("https://soundcloud.com");

    private IReadOnlySet<string> _libraryIds = new HashSet<string>();
    private readonly ConcurrentDictionary<string, Task<Uri?>> _artwork = new();
    private string? _accountProfile;

    public override string Id => SourceIds.SoundCloud;
    public override string DisplayName => "SoundCloud";

    protected override string QueueSourceName => "SoundCloud via Audio Star";

    public override Task<SourceStatus> ConnectAsync(CancellationToken cancellationToken = default) => ConnectAsync(true, cancellationToken);

    public override Task<SourceStatus> ConnectSilentlyAsync(CancellationToken cancellationToken = default) => ConnectAsync(false, cancellationToken);

    public override async Task DisconnectAsync(CancellationToken cancellationToken = default)
    {
        session.Clear();
        _accountProfile = null;
        await webSignIn.SignOutAsync(SiteUri, cancellationToken);
        await base.DisconnectAsync(cancellationToken);
    }

    protected override IReadOnlyList<string> TrackArguments() => session.AuthArguments();

    internal IReadOnlyList<TimeSpan> RetryDelays { get; set; } = [TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(5), TimeSpan.FromSeconds(10)];

    internal static bool ShouldRetry(Exception exception, int attempt, int maxRetries, CancellationToken cancellationToken) =>
        attempt < maxRetries
        && !cancellationToken.IsCancellationRequested
        && exception is HttpRequestException or TaskCanceledException;

    private string? Profile => SoundCloudMapper.NormalizeProfile(Settings.Current.SoundCloudProfileUrl) ?? SoundCloudMapper.NormalizeProfile(_accountProfile);

    private async Task<SourceStatus> ConnectAsync(bool interactive, CancellationToken cancellationToken)
    {
        if (!session.HasToken && interactive && !await SignInAsync(cancellationToken))
        {
            return Status;
        }
        if (!session.HasToken)
        {
            return await ConnectWithoutAccountAsync(cancellationToken);
        }
        SetStatus(SourceConnectionState.Connecting, null, null);
        for (var attempt = 0; ; attempt++)
        {
            try
            {
                var account = await session.GetAccountAsync(cancellationToken);
                _accountProfile = account.ProfileUrl;
                SetStatus(SourceConnectionState.Connected, account.Name, null);
                break;
            }
            catch (SoundCloudTokenRejectedException)
            {
                session.Clear();
                _accountProfile = null;
                SetStatus(SourceConnectionState.Error, null, "SoundCloud no longer accepts the sign-in. Connect again.");
                break;
            }
            catch (Exception exception) when (exception is HttpRequestException or JsonException or TaskCanceledException && !cancellationToken.IsCancellationRequested)
            {
                var request = exception.Data[SoundCloudSession.RequestKey] as string ?? "unknown request";
                var retry = ShouldRetry(exception, attempt, RetryDelays.Count, cancellationToken);
                Logger.LogWarning("SoundCloud account could not be read (attempt {Attempt} of {Attempts}, {Request}): {Message}", attempt + 1, RetryDelays.Count + 1, request, exception.Message);
                if (!retry)
                {
                    SetStatus(SourceConnectionState.Error, null, exception.Message);
                    break;
                }
                await Task.Delay(RetryDelays[attempt], cancellationToken);
            }
        }
        return Status;
    }

    private async Task<bool> SignInAsync(CancellationToken cancellationToken)
    {
        SetStatus(SourceConnectionState.Connecting, null, null);
        try
        {
            var request = new WebSignInRequest("Sign in to SoundCloud", new Uri("https://soundcloud.com/signin"))
            {
                CookieUri = SiteUri,
                CookieName = "oauth_token"
            };
            var result = await webSignIn.SignInAsync(request, cancellationToken);
            if (result?.CookieValue is { Length: > 0 } token)
            {
                session.Save(token);
            }
            return true;
        }
        catch (InvalidOperationException exception)
        {
            Logger.LogWarning("SoundCloud sign-in could not open: {Message}", exception.Message);
            SetStatus(SourceConnectionState.Error, null, exception.Message);
            return false;
        }
    }

    private async Task<SourceStatus> ConnectWithoutAccountAsync(CancellationToken cancellationToken)
    {
        var profile = SoundCloudMapper.NormalizeProfile(Settings.Current.SoundCloudProfileUrl);
        if (profile is null)
        {
            if (Settings.Current.SoundCloudPlaylistUrls.Count == 0)
            {
                SetStatus(SourceConnectionState.NotConfigured, null, "Set your SoundCloud profile URL or paste a playlist URL.");
            }
            else
            {
                SetStatus(SourceConnectionState.Connected, null, "Pasted playlists only. Set your profile URL to see your sets and likes.");
            }
            return Status;
        }
        SetStatus(SourceConnectionState.Connecting, null, null);
        try
        {
            var header = await PeekPlaylistAsync($"{profile}/sets", (root, _) => new SourcePlaylist(Id, profile, root.Str("title") ?? profile, root.Str("uploader"), null, null, null), [], cancellationToken);
            SetStatus(SourceConnectionState.Connected, header.Title.Replace(" (Sets)", ""), null);
        }
        catch (YtDlpException exception)
        {
            Logger.LogWarning("SoundCloud connect failed: {Message}", exception.Message);
            SetStatus(SourceConnectionState.Error, null, exception.Message);
        }
        return Status;
    }

    public override async Task<IReadOnlyList<SourcePlaylist>> GetPlaylistsAsync(CancellationToken cancellationToken = default)
    {
        var result = new List<SourcePlaylist>();
        var profile = Profile;
        if (profile is not null)
        {
            result.Add(new SourcePlaylist(Id, $"{profile}/likes", "Likes", null, null, null, new Uri($"{profile}/likes")));
        }
        if (session.HasToken)
        {
            result.Add(new SourcePlaylist(Id, SoundCloudApi.HistoryUrl, "History", null, null, null, new Uri(SoundCloudApi.HistoryUrl)));
        }
        if (profile is not null)
        {
            try
            {
                using var sets = await YtDlp.GetJsonAsync([.. TrackArguments(), "-J", "--flat-playlist", "--ignore-errors", $"{profile}/sets"], ListTimeout, cancellationToken);
                result.AddRange(SoundCloudMapper.MapSets(sets.Root, sets.Root.Str("uploader")));
            }
            catch (YtDlpException exception)
            {
                Logger.LogWarning("SoundCloud sets could not be loaded: {Message}", exception.Message);
                SetStatus(SourceConnectionState.Error, null, exception.Message);
            }
        }

        var known = result.Select(p => p.Id).ToHashSet();
        _libraryIds = known;
        var urls = Settings.Current.SoundCloudPlaylistUrls.Select(u => SoundCloudMapper.NormalizeUrl(u) ?? u).Distinct().Where(u => !known.Contains(u)).ToList();
        var loaded = await Task.WhenAll(urls.Select(url => PastedPlaylistAsync(url, cancellationToken)));
        result.AddRange(loaded);
        return await FillArtworkAsync(result, cancellationToken);
    }

    private async Task<IReadOnlyList<SourcePlaylist>> FillArtworkAsync(List<SourcePlaylist> playlists, CancellationToken cancellationToken)
    {
        var filled = await Task.WhenAll(playlists.Select(async playlist =>
        {
            if (playlist.ArtworkUri is not null)
            {
                return playlist;
            }
            var artwork = await ArtworkForAsync(playlist.Id, cancellationToken);
            if (artwork is null)
            {
                return playlist;
            }
            var withArtwork = playlist with { ArtworkUri = artwork };
            if (Pasted.ContainsKey(playlist.Id))
            {
                Pasted[playlist.Id] = withArtwork;
                try
                {
                    await StoreHeaderAsync(withArtwork, cancellationToken);
                }
                catch (Exception exception) when (exception is not OperationCanceledException)
                {
                    Logger.LogWarning("SoundCloud cover for {Url} could not be cached: {Message}", playlist.Id, exception.Message);
                }
            }
            return withArtwork;
        }));
        return filled;
    }

    private async Task<Uri?> ArtworkForAsync(string playlistId, CancellationToken cancellationToken)
    {
        if (playlistId == SoundCloudApi.HistoryUrl)
        {
            return await LoadArtworkAsync(playlistId, cancellationToken);
        }
        var task = _artwork.GetOrAdd(playlistId, id => LoadArtworkAsync(id, CancellationToken.None));
        var artwork = await task.WaitAsync(cancellationToken);
        if (artwork is null)
        {
            _artwork.TryRemove(new KeyValuePair<string, Task<Uri?>>(playlistId, task));
        }
        return artwork;
    }

    private async Task<Uri?> LoadArtworkAsync(string playlistId, CancellationToken cancellationToken)
    {
        try
        {
            if (playlistId == SoundCloudApi.HistoryUrl)
            {
                return await session.GetHistoryArtworkAsync(cancellationToken);
            }
            return playlistId.EndsWith("/likes", StringComparison.OrdinalIgnoreCase)
                ? await session.GetLikesArtworkAsync(playlistId, cancellationToken)
                : await session.GetPlaylistArtworkAsync(playlistId, cancellationToken);
        }
        catch (Exception exception) when (exception is HttpRequestException or JsonException or TaskCanceledException or InvalidOperationException && !cancellationToken.IsCancellationRequested)
        {
            Logger.LogWarning("SoundCloud cover for {Url} could not be loaded: {Message}", playlistId, exception.Message);
            return null;
        }
    }

    protected override async Task<IReadOnlyList<SourceTrack>?> GetOwnTracksAsync(SourcePlaylist playlist, CancellationToken cancellationToken)
    {
        if (playlist.Id != SoundCloudApi.HistoryUrl || !session.HasToken)
        {
            return null;
        }
        return SoundCloudApi.ToSourceTracks(await session.GetHistoryAsync(cancellationToken), playlist.Title);
    }

    protected override async Task<IReadOnlyList<SourceTrack>> EnrichTracksAsync(IReadOnlyList<SourceTrack> tracks, CancellationToken cancellationToken)
    {
        var ids = tracks.Select(t => t.Id).Where(SoundCloudApi.IsTrackId).Distinct().ToList();
        if (ids.Count == 0)
        {
            return tracks;
        }
        try
        {
            return SoundCloudApi.Enrich(tracks, await session.GetTrackInfosAsync(ids, cancellationToken));
        }
        catch (Exception exception) when (exception is HttpRequestException or JsonException or TaskCanceledException or InvalidOperationException && !cancellationToken.IsCancellationRequested)
        {
            Logger.LogWarning("SoundCloud track details could not be loaded: {Message}", exception.Message);
            return tracks;
        }
    }

    public override async Task<SourcePlaylist?> AddPlaylistByUrlAsync(string url, CancellationToken cancellationToken = default)
    {
        var normalized = SoundCloudMapper.NormalizeUrl(url);
        if (normalized is null)
        {
            return null;
        }
        var playlist = await PeekPlaylistAsync(normalized, SoundCloudMapper.MapPlaylistHeader, TrackArguments(), cancellationToken);
        Pasted[normalized] = playlist;
        await StoreHeaderAsync(playlist, cancellationToken);
        var saved = Settings.Current.SoundCloudPlaylistUrls;
        if (!saved.Select(u => SoundCloudMapper.NormalizeUrl(u) ?? u).Contains(normalized))
        {
            saved.Add(normalized);
            await Settings.SaveAsync(cancellationToken);
        }
        return playlist;
    }

    protected override List<string> PastedUrls => Settings.Current.SoundCloudPlaylistUrls;

    protected override string? NormalizeUrl(string url) => SoundCloudMapper.NormalizeUrl(url);

    protected override Task<SourcePlaylist> PeekAddedAsync(string url, CancellationToken cancellationToken) =>
        PeekPlaylistAsync(url, SoundCloudMapper.MapPlaylistHeader, TrackArguments(), cancellationToken);

    protected override bool IsLibraryPlaylist(string playlistId) => _libraryIds.Contains(playlistId);

    protected override IReadOnlyList<SourceTrack> MapTracks(JsonElement root) => SoundCloudMapper.MapTracks(root);

    protected override SourcePlaylist MapPlaylistHeader(JsonElement root, string url) => SoundCloudMapper.MapPlaylistHeader(root, url);

    private async Task<SourcePlaylist> PastedPlaylistAsync(string url, CancellationToken cancellationToken)
    {
        if (Pasted.TryGetValue(url, out var cached))
        {
            return cached;
        }
        try
        {
            var playlist = await CachedOrPeekAsync(url, () => PeekPlaylistAsync(url, SoundCloudMapper.MapPlaylistHeader, TrackArguments(), cancellationToken), cancellationToken);
            Pasted[url] = playlist;
            return playlist;
        }
        catch (YtDlpException exception)
        {
            Logger.LogWarning("Playlist {Url} could not be read: {Message}", url, exception.Message);
            return new SourcePlaylist(Id, url, url, null, null, null, Uri.TryCreate(url, UriKind.Absolute, out var uri) ? uri : null);
        }
    }
}
