using System.Text.Json;
using AudioStar.Core;
using Microsoft.Extensions.Logging;

namespace AudioStar.Sources.Spotify;

public sealed class SpotifySource : IMusicSource
{
    private const int MaxLikedTracks = 5000;

    private readonly SpotifyAuth _auth;
    private readonly SpotifyApi _api;
    private readonly IWebSignIn _webSignIn;
    private readonly ISettingsStore _settings;
    private readonly IRecentlyPlayed _recentlyPlayed;
    private readonly ILogger<SpotifySource> _logger;
    private SourceStatus _status;

    public SpotifySource(SpotifyAuth auth, SpotifyApi api, IWebSignIn webSignIn, ISettingsStore settings, IRecentlyPlayed recentlyPlayed, ILogger<SpotifySource> logger)
    {
        _auth = auth;
        _api = api;
        _webSignIn = webSignIn;
        _settings = settings;
        _recentlyPlayed = recentlyPlayed;
        _logger = logger;
        _status = Idle();
        settings.Changed += (_, _) =>
        {
            if (_status.State is SourceConnectionState.NotConfigured or SourceConnectionState.Disconnected)
            {
                SetStatus(Idle());
            }
        };
    }

    public string Id => SourceIds.Spotify;
    public string DisplayName => "Spotify";
    public SourceStatus Status => _status;

    public event EventHandler<SourceStatus>? StatusChanged;

    public Task<SourceStatus> ConnectAsync(CancellationToken cancellationToken = default) => ConnectAsync(true, cancellationToken);

    public Task<SourceStatus> ConnectSilentlyAsync(CancellationToken cancellationToken = default) =>
        _auth.HasStoredToken ? ConnectAsync(false, cancellationToken) : Task.FromResult(_status);

    private async Task<SourceStatus> ConnectAsync(bool interactive, CancellationToken cancellationToken)
    {
        if (_auth.ClientId is null && !interactive)
        {
            SetStatus(Idle());
            return _status;
        }
        SetStatus(new SourceStatus(SourceConnectionState.Connecting, null, null));
        try
        {
            if (_auth.ClientId is null)
            {
                await _auth.SetUpClientIdAsync(cancellationToken);
            }
            if (_auth.HasStoredToken)
            {
                try
                {
                    await _auth.GetAccessTokenAsync(cancellationToken);
                }
                catch (SpotifyAuthException) when (interactive)
                {
                    await _auth.SignInAsync(cancellationToken);
                }
            }
            else
            {
                await _auth.SignInAsync(cancellationToken);
            }
            using var me = await _api.GetAsync("me", cancellationToken);
            var account = me.RootElement.Str("display_name") ?? me.RootElement.Str("id");
            SetStatus(new SourceStatus(SourceConnectionState.Connected, account, null));
        }
        catch (Exception exception) when (exception is SpotifyAuthException or SpotifyApiException or HttpRequestException or TaskCanceledException && !cancellationToken.IsCancellationRequested)
        {
            _logger.LogWarning("Spotify connect failed: {Message}", exception.Message);
            SetStatus(new SourceStatus(SourceConnectionState.Error, null, exception.Message));
        }
        return _status;
    }

    public async Task DisconnectAsync(CancellationToken cancellationToken = default)
    {
        _auth.SignOut();
        await _webSignIn.SignOutAsync(new Uri("https://accounts.spotify.com"), cancellationToken);
        SetStatus(Idle());
    }

    public async Task<IReadOnlyList<SourcePlaylist>> GetPlaylistsAsync(CancellationToken cancellationToken = default)
    {
        EnsureConnected();
        var items = await _api.GetAllAsync("me/playlists?limit=50", 1000, cancellationToken);
        var playlists = new List<SourcePlaylist>();
        using (var liked = await _api.GetAsync("me/tracks?limit=1", cancellationToken))
        {
            playlists.Add(SpotifyMapper.LikedSongs(liked.RootElement.Int("total")));
        }
        playlists.AddRange(SpotifyMapper.MapPlaylists(items));
        return playlists;
    }

    public async Task<SourcePlaylist?> AddPlaylistByUrlAsync(string url, CancellationToken cancellationToken = default)
    {
        EnsureConnected();
        var id = SpotifyMapper.ParsePlaylistId(url);
        if (id is null)
        {
            return null;
        }
        using var playlist = await _api.GetAsync($"playlists/{id}", cancellationToken);
        return SpotifyMapper.MapPlaylist(playlist.RootElement);
    }

    public async Task<IReadOnlyList<SourceTrack>> GetTracksAsync(SourcePlaylist playlist, CancellationToken cancellationToken = default)
    {
        EnsureConnected();
        var path = playlist.Id == SpotifyMapper.LikedId ? "me/tracks?limit=50" : $"playlists/{playlist.Id}/items?limit=50";
        var items = await _api.GetAllAsync(path, MaxLikedTracks, cancellationToken);
        return SpotifyMapper.MapTracks(items);
    }

    public async Task PlayAsync(ISpeakerSession speaker, SourcePlaylist playlist, int startIndex = 0, CancellationToken cancellationToken = default)
    {
        EnsureConnected();
        var name = speaker.Info.Name;
        SpotifyDevice? device;
        using (var devices = await _api.GetAsync("me/player/devices", cancellationToken))
        {
            device = SpotifyMapper.FindDevice(devices.RootElement, name);
        }
        if (device is null)
        {
            throw new InvalidOperationException($"'{name}' is not listed as a Spotify Connect device. Open the Spotify app once, pick '{name}' as the playback device, then try again.");
        }

        var tracks = playlist.Id == SpotifyMapper.LikedId ? await GetTracksAsync(playlist, cancellationToken) : [];
        var body = SpotifyMapper.BuildPlayBody(playlist.Id, tracks, Math.Max(0, startIndex));
        await _api.SendAsync(HttpMethod.Put, $"me/player/play?device_id={Uri.EscapeDataString(device.Id)}", body, cancellationToken);
        await _recentlyPlayed.AddAsync(RecentKinds.SourcePlaylist, Id, playlist.Title, playlist.Owner is null ? DisplayName : $"{DisplayName}, {playlist.Owner}", playlist.ArtworkUri, JsonSerializer.Serialize(playlist), cancellationToken);
        _logger.LogInformation("Started Spotify playlist {Playlist} on {Speaker}", playlist.Title, name);
    }

    private void EnsureConnected()
    {
        if (_status.State != SourceConnectionState.Connected)
        {
            throw new InvalidOperationException(_status.Message ?? "Spotify is not connected.");
        }
    }

    private SourceStatus Idle() =>
        _auth.ClientId is null
            ? new SourceStatus(SourceConnectionState.NotConfigured, null, "Press Connect to set up Spotify.")
            : new SourceStatus(SourceConnectionState.Disconnected, null, null);

    private void SetStatus(SourceStatus status)
    {
        _status = status;
        StatusChanged?.Invoke(this, status);
    }
}
