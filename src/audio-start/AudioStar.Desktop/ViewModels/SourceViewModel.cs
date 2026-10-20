using System.Collections.ObjectModel;
using System.Windows;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AudioStar.Desktop.ViewModels;

public sealed partial class PlaylistRow(SourcePlaylist playlist, bool isAdded = false) : ObservableObject
{
    [ObservableProperty]
    private bool _isPlaying;

    public SourcePlaylist Playlist { get; } = playlist;

    public bool IsAdded { get; } = isAdded;

    public string Title => Playlist.Title;

    public string Details => string.Join(" - ", new[]
    {
        Playlist.Owner,
        Playlist.TrackCount is { } count ? $"{count} tracks" : null
    }.Where(s => !string.IsNullOrWhiteSpace(s)));

    public Uri? ArtworkUri => Playlist.ArtworkUri;
}

public sealed partial class SourceTrackRow(SourceTrack track, int number) : ObservableObject
{
    [ObservableProperty]
    private bool _isPlaying;

    public SourceTrack Track { get; } = track;

    public int Number { get; } = number;

    public string Title => Track.Title;

    public string Artist => Track.Artist ?? "";

    public string Duration => Track.Duration is { } d ? PlaybackFormat.Time(d) : "";

    public Uri? ArtworkUri => Track.ArtworkUri;

    public string Details => string.Join(Environment.NewLine, new[] { Title, Artist, Track.Album ?? "", Duration }.Where(line => !string.IsNullOrWhiteSpace(line)));
}

public sealed partial class SourceViewModel : SpeakerPageViewModel
{
    private const string NotAPlaylistMessage = "That link is not a playlist this source can open.";

    private readonly IMusicSource _source;
    private readonly IUiDispatcher _dispatcher;
    private readonly IDialogService _dialogs;
    private ISpeakerSession? _observed;
    private string? _playingId;

    public SourceViewModel(string sourceId, IEnumerable<IMusicSource> sources, IToastService toast, ICurrentSpeaker speakers, IUiDispatcher dispatcher, IDialogService dialogs)
        : base(toast, speakers)
    {
        _source = sources.FirstOrDefault(s => s.Id == sourceId)
            ?? throw new InvalidOperationException($"The {sourceId} source is not available.");
        _dispatcher = dispatcher;
        _dialogs = dialogs;
        SupportsUrl = sourceId is SourceIds.YouTube or SourceIds.SoundCloud;
        ApplyStatus(_source.Status);
        _source.StatusChanged += OnStatusChanged;
        Observe(Speaker);
    }

    public override string Title => _source.DisplayName;

    public bool SupportsUrl { get; }

    public double CoverRatio => _source.Id == SourceIds.YouTube ? 9.0 / 16 : 1;

    private static StartedList? s_startedList;
    private static bool s_showNumber;
    private static bool s_showArtist = true;
    private static bool s_cardView;
    private static GridLength s_titleWidth = new(3, GridUnitType.Star);
    private static GridLength s_artistWidth = new(2, GridUnitType.Star);

    public bool CardView
    {
        get => s_cardView;
        set
        {
            if (s_cardView == value)
            {
                return;
            }
            s_cardView = value;
            OnPropertyChanged();
            OnPropertyChanged(nameof(ListMode));
        }
    }

    public bool ListMode => !s_cardView;

    [RelayCommand]
    private void ToggleView() => CardView = !CardView;

    public bool ShowNumber
    {
        get => s_showNumber;
        set
        {
            if (s_showNumber == value)
            {
                return;
            }
            s_showNumber = value;
            OnPropertyChanged();
            OnPropertyChanged(nameof(NumberColumnWidth));
        }
    }

    public bool ShowArtist
    {
        get => s_showArtist;
        set
        {
            if (s_showArtist == value)
            {
                return;
            }
            s_showArtist = value;
            OnPropertyChanged();
            OnPropertyChanged(nameof(ArtistColumnWidth));
        }
    }

    public GridLength NumberColumnWidth => ShowNumber ? new GridLength(36) : new GridLength(0);

    public GridLength TitleColumnWidth
    {
        get => s_titleWidth;
        set
        {
            s_titleWidth = value;
            OnPropertyChanged();
        }
    }

    public GridLength ArtistColumnWidth
    {
        get => ShowArtist ? s_artistWidth : new GridLength(0);
        set
        {
            if (!ShowArtist)
            {
                return;
            }
            s_artistWidth = value;
            OnPropertyChanged();
        }
    }

    public ObservableCollection<PlaylistRow> Playlists { get; } = [];

    public ObservableCollection<SourceTrackRow> Tracks { get; } = [];

    [ObservableProperty]
    private string _statusLabel = "";

    [ObservableProperty]
    private string? _statusMessage;

    [ObservableProperty]
    private SourceConnectionState _state;

    [ObservableProperty]
    private bool _connecting;

    [ObservableProperty]
    private PlaylistRow? _selectedPlaylist;

    [ObservableProperty]
    private string _playlistUrl = "";

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(NoPlaylists))]
    private bool _loaded;

    public bool NoPlaylists => Loaded && Playlists.Count == 0;

    public bool HasTracks => Tracks.Count > 0;

    protected override void OnSpeakerSwitched() => _dispatcher.Post(() => Observe(Speaker));

    private void Observe(ISpeakerSession? speaker)
    {
        if (_observed is not null)
        {
            _observed.StateChanged -= OnPlaybackChanged;
        }
        _observed = speaker;
        if (_observed is not null)
        {
            _observed.StateChanged += OnPlaybackChanged;
        }
        ApplyPlaying(speaker?.State);
    }

    private void OnPlaybackChanged(object? sender, PlaybackState state) => _dispatcher.Post(() => ApplyPlaying(state));

    private void ApplyPlaying(PlaybackState? state)
    {
        _playingId = PlayingTrackId(state?.Track?.TrackUri);
        foreach (var row in Tracks)
        {
            row.IsPlaying = row.Track.Id == _playingId;
        }
        var started = s_startedList is { } list && list.SourceId == _source.Id && _playingId is not null && list.TrackIds.Contains(_playingId) ? list.PlaylistId : null;
        foreach (var row in Playlists)
        {
            row.IsPlaying = _playingId is not null && (started is not null
                ? row.Playlist.Id == started
                : ReferenceEquals(row, SelectedPlaylist) && Tracks.Any(t => t.IsPlaying));
        }
    }

    private string? PlayingTrackId(string? trackUri)
    {
        if (!Uri.TryCreate(trackUri, UriKind.Absolute, out var uri))
        {
            return null;
        }
        var prefix = $"/stream/{Uri.EscapeDataString(_source.Id)}/";
        var at = uri.AbsolutePath.IndexOf(prefix, StringComparison.Ordinal);
        return at < 0 ? null : Uri.UnescapeDataString(uri.AbsolutePath[(at + prefix.Length)..]);
    }

    private void OnStatusChanged(object? sender, SourceStatus status) => _dispatcher.Post(() =>
    {
        var wasConnected = State == SourceConnectionState.Connected;
        ApplyStatus(status);
        if (!wasConnected && !Connecting && status.State == SourceConnectionState.Connected)
        {
            _ = InitializeAsync();
        }
        else if (wasConnected && status.State is SourceConnectionState.Disconnected or SourceConnectionState.NotConfigured)
        {
            Playlists.Clear();
            Tracks.Clear();
            SelectedPlaylist = null;
        }
    });

    private void ApplyStatus(SourceStatus status)
    {
        State = status.State;
        var label = status.State switch
        {
            SourceConnectionState.Connected => string.IsNullOrWhiteSpace(status.AccountName) ? "Connected" : $"Connected as {status.AccountName}",
            SourceConnectionState.Connecting => "Connecting...",
            SourceConnectionState.NotConfigured => "Not set up",
            SourceConnectionState.Error => "Connection problem",
            _ => "Not connected"
        };
        StatusLabel = label;
        StatusMessage = string.IsNullOrWhiteSpace(status.Message) ? null : status.Message;
    }

    public override async Task LoadAsync()
    {
        Playlists.Clear();
        Tracks.Clear();
        OnPropertyChanged(nameof(HasTracks));
        try
        {
            if (SupportsUrl && _source.Status.State == SourceConnectionState.Disconnected)
            {
                Connecting = true;
                try
                {
                    ApplyStatus(await _source.ConnectSilentlyAsync());
                }
                finally
                {
                    Connecting = false;
                }
            }
            var playlists = await _source.GetPlaylistsAsync();
            foreach (var playlist in playlists)
            {
                Playlists.Add(CreateRow(playlist));
            }
            ApplyPlaying(Speaker?.State);
        }
        finally
        {
            Loaded = true;
            OnPropertyChanged(nameof(NoPlaylists));
        }
    }

    partial void OnSelectedPlaylistChanged(PlaylistRow? value)
    {
        Tracks.Clear();
        OnPropertyChanged(nameof(HasTracks));
        if (value is not null)
        {
            _ = LoadGuardedAsync(() => LoadTracksAsync(value));
        }
    }

    private async Task LoadTracksAsync(PlaylistRow row)
    {
        var tracks = await _source.GetTracksAsync(row.Playlist);
        if (!ReferenceEquals(SelectedPlaylist, row))
        {
            return;
        }
        Tracks.Clear();
        var number = 1;
        foreach (var track in tracks)
        {
            Tracks.Add(new SourceTrackRow(track, number++) { IsPlaying = track.Id == _playingId });
        }
        OnPropertyChanged(nameof(HasTracks));
        ApplyPlaying(Speaker?.State);
    }

    [RelayCommand]
    private Task AddPlaylistAsync() => GuardAsync(async () =>
    {
        var url = PlaylistUrl.Trim();
        if (url.Length == 0)
        {
            return;
        }
        IsBusy = true;
        try
        {
            var playlist = await _source.AddPlaylistByUrlAsync(url);
            if (playlist is null)
            {
                Toast.ShowError(NotAPlaylistMessage);
                return;
            }
            PlaylistUrl = "";
            var row = Playlists.FirstOrDefault(p => p.Playlist.Id == playlist.Id);
            if (row is null)
            {
                row = CreateRow(playlist);
                Playlists.Add(row);
                OnPropertyChanged(nameof(NoPlaylists));
            }
            SelectedPlaylist = row;
        }
        finally
        {
            IsBusy = false;
        }
    });

    [RelayCommand]
    private Task RemovePlaylistAsync(PlaylistRow? row) => GuardAsync(async () =>
    {
        if (row is null || _source is not IEditablePlaylistSource editable)
        {
            return;
        }
        await editable.RemovePlaylistAsync(row.Playlist);
        var wasSelected = ReferenceEquals(SelectedPlaylist, row);
        Playlists.Remove(row);
        if (wasSelected)
        {
            SelectedPlaylist = null;
            Tracks.Clear();
            OnPropertyChanged(nameof(HasTracks));
        }
        OnPropertyChanged(nameof(NoPlaylists));
    });

    [RelayCommand]
    private Task EditPlaylistAsync(PlaylistRow? row) => GuardAsync(async () =>
    {
        if (row is null || _source is not IEditablePlaylistSource editable)
        {
            return;
        }
        var url = _dialogs.ShowPlaylistSettings(row.Title, row.Playlist.Id)?.Trim();
        if (string.IsNullOrEmpty(url))
        {
            return;
        }
        IsBusy = true;
        try
        {
            var playlist = await editable.ChangePlaylistUrlAsync(row.Playlist, url);
            if (playlist is null)
            {
                Toast.ShowError(NotAPlaylistMessage);
                return;
            }
            var replacement = CreateRow(playlist);
            var index = Playlists.IndexOf(row);
            if (index < 0)
            {
                Playlists.Add(replacement);
            }
            else
            {
                Playlists[index] = replacement;
            }
            foreach (var duplicate in Playlists.Where(p => p != replacement && p.Playlist.Id == playlist.Id).ToList())
            {
                Playlists.Remove(duplicate);
            }
            SelectedPlaylist = replacement;
        }
        finally
        {
            IsBusy = false;
        }
    });

    [RelayCommand]
    private Task PlayAllAsync() => PlayAsync(0);

    [RelayCommand]
    private Task PlayFromAsync(SourceTrackRow? row) => row is null ? Task.CompletedTask : PlayAsync(row.Number - 1);

    [RelayCommand]
    private Task OpenPlaylistAsync(PlaylistRow? row)
    {
        SelectedPlaylist = row;
        return Task.CompletedTask;
    }

    private PlaylistRow CreateRow(SourcePlaylist playlist) =>
        new(playlist, _source is IEditablePlaylistSource editable && editable.IsAdded(playlist));

    private Task PlayAsync(int start) => GuardAsync(async () =>
    {
        var playlist = SelectedPlaylist ?? throw new InvalidOperationException("Pick a playlist first.");
        var trackIds = Tracks.Select(t => t.Track.Id).ToHashSet();
        await _source.PlayAsync(Speakers.Require(), playlist.Playlist, start);
        s_startedList = new StartedList(_source.Id, playlist.Playlist.Id, trackIds);
        ApplyPlaying(Speaker?.State);
    });

    private sealed record StartedList(string SourceId, string PlaylistId, HashSet<string> TrackIds);

    public override void Dispose()
    {
        _source.StatusChanged -= OnStatusChanged;
        if (_observed is not null)
        {
            _observed.StateChanged -= OnPlaybackChanged;
        }
        base.Dispose();
    }
}
