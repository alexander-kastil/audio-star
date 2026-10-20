using System.Collections.ObjectModel;
using System.Windows;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AudioStar.Desktop.ViewModels;

public sealed class AlbumRow(LibraryAlbum album, Uri? cover)
{
    public LibraryAlbum Album { get; } = album;

    public string Name => string.IsNullOrWhiteSpace(Album.Album) ? "Unknown album" : Album.Album;

    public string Artist => string.IsNullOrWhiteSpace(Album.AlbumArtist) ? "Unknown artist" : Album.AlbumArtist;

    public string Details => Album.Year is { } year ? $"{Album.TrackCount} tracks, {year}" : $"{Album.TrackCount} tracks";

    public Uri? CoverUri { get; } = cover;
}

public sealed class TrackRow(LibraryTrack track, int number)
{
    public LibraryTrack Track { get; } = track;

    public int Number { get; } = number;

    public string Title => Track.Title;

    public string Artist => Track.Artist ?? Track.AlbumArtist ?? "";

    public string Album => Track.Album ?? "";

    public string Duration => PlaybackFormat.Time(Track.Duration);
}

public sealed partial class MyMusicViewModel : SpeakerPageViewModel
{
    private const int TrackLimit = 500;

    private readonly IMusicLibrary _library;
    private readonly IMediaServer _media;
    private readonly IUiDispatcher _dispatcher;
    private readonly IDialogService _dialogs;
    private readonly IRecentlyPlayed _recent;
    private readonly Debouncer _searchDebouncer = new(TimeSpan.FromMilliseconds(300));
    private CancellationTokenSource? _scanCts;
    private bool _opened;

    public MyMusicViewModel(
        IToastService toast,
        ICurrentSpeaker speakers,
        IMusicLibrary library,
        IMediaServer media,
        IUiDispatcher dispatcher,
        IDialogService dialogs,
        IRecentlyPlayed recent) : base(toast, speakers)
    {
        _recent = recent;
        _library = library;
        _media = media;
        _dispatcher = dispatcher;
        _dialogs = dialogs;
        _library.LibraryChanged += OnLibraryChanged;
    }

    public override string Title => "My Music";

    public ObservableCollection<string> Folders { get; } = [];

    public ObservableCollection<AlbumRow> Albums { get; } = [];

    public ObservableCollection<LibraryArtist> Artists { get; } = [];

    public ObservableCollection<LibraryGenre> Genres { get; } = [];

    public ObservableCollection<TrackRow> Tracks { get; } = [];

    public ObservableCollection<TrackRow> DetailTracks { get; } = [];

    public ObservableCollection<AlbumRow> DetailAlbums { get; } = [];

    [ObservableProperty]
    private int _selectedTab;

    [ObservableProperty]
    private string _search = "";

    [ObservableProperty]
    private bool _isScanning;

    [ObservableProperty]
    private string _scanText = "";

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(ShowTabs))]
    private bool _hasDetail;

    [ObservableProperty]
    private string _detailTitle = "";

    [ObservableProperty]
    private string? _detailSubtitle;

    [ObservableProperty]
    private Uri? _detailCover;

    [ObservableProperty]
    private string? _tracksNote;

    private static bool s_showNumber;
    private static bool s_showArtist = true;
    private static bool s_showAlbum = true;
    private static GridLength s_titleWidth = new(3, GridUnitType.Star);
    private static GridLength s_artistWidth = new(2, GridUnitType.Star);
    private static GridLength s_albumWidth = new(2, GridUnitType.Star);

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
            OnPropertyChanged(nameof(ShowAlbumDivider));
        }
    }

    public bool ShowAlbum
    {
        get => s_showAlbum;
        set
        {
            if (s_showAlbum == value)
            {
                return;
            }
            s_showAlbum = value;
            OnPropertyChanged();
            OnPropertyChanged(nameof(AlbumColumnWidth));
            OnPropertyChanged(nameof(ShowAlbumDivider));
        }
    }

    public bool ShowAlbumDivider => ShowArtist && ShowAlbum;

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

    public GridLength AlbumColumnWidth
    {
        get => ShowAlbum ? s_albumWidth : new GridLength(0);
        set
        {
            if (!ShowAlbum)
            {
                return;
            }
            s_albumWidth = value;
            OnPropertyChanged();
        }
    }

    public bool ShowTabs => !HasDetail;

    public bool NoFolders => Folders.Count == 0;

    public bool HasDetailAlbums => DetailAlbums.Count > 0;

    protected override void OnSpeakerSwitched()
    {
    }

    public override async Task LoadAsync()
    {
        SyncFolders();
        _opened = true;
        await LoadTabAsync();
    }

    private void SyncFolders()
    {
        Folders.Clear();
        foreach (var folder in _library.Folders)
        {
            Folders.Add(folder);
        }
        OnPropertyChanged(nameof(NoFolders));
    }

    partial void OnSelectedTabChanged(int value)
    {
        if (_opened)
        {
            _ = GuardAsync(LoadTabAsync);
        }
    }

    partial void OnSearchChanged(string value)
    {
        if (_opened)
        {
            _ = GuardAsync(() => _searchDebouncer.RunAsync(_ => LoadTabAsync()));
        }
    }

    private void OnLibraryChanged(object? sender, EventArgs e) => _dispatcher.Post(() =>
    {
        SyncFolders();
        _ = GuardAsync(LoadTabAsync);
    });

    private async Task LoadTabAsync()
    {
        var search = string.IsNullOrWhiteSpace(Search) ? null : Search.Trim();
        switch (SelectedTab)
        {
            case 0:
                var albums = await _library.GetAlbumsAsync(search);
                Replace(Albums, albums.Select(ToRow));
                break;
            case 1:
                var artists = await _library.GetArtistsAsync(search);
                Replace(Artists, artists);
                break;
            case 2:
                var genres = await _library.GetGenresAsync();
                Replace(Genres, search is null ? genres : genres.Where(g => g.Name.Contains(search, StringComparison.OrdinalIgnoreCase)));
                break;
            default:
                var tracks = await _library.GetTracksAsync(new LibraryQuery(Search: search, Limit: TrackLimit));
                Replace(Tracks, tracks.Select((t, i) => new TrackRow(t, i + 1)));
                TracksNote = tracks.Count >= TrackLimit ? $"Showing the first {TrackLimit} tracks. Search to narrow the list." : null;
                break;
        }
    }

    private AlbumRow ToRow(LibraryAlbum album) =>
        new(album, album.CoverTrackPath is { } path ? _media.GetCoverUri(path) : null);

    private static void Replace<T>(ObservableCollection<T> target, IEnumerable<T> items)
    {
        target.Clear();
        foreach (var item in items)
        {
            target.Add(item);
        }
    }

    [RelayCommand]
    private Task AddFolderAsync() => GuardAsync(async () =>
    {
        var folder = _dialogs.PickFolder();
        if (folder is null)
        {
            return;
        }
        await _library.AddFolderAsync(folder);
        SyncFolders();
    });

    [RelayCommand]
    private Task RemoveFolderAsync(string? folder) => folder is null
        ? Task.CompletedTask
        : GuardAsync(async () =>
        {
            await _library.RemoveFolderAsync(folder);
            SyncFolders();
        });

    [RelayCommand]
    private async Task ScanAsync()
    {
        if (IsScanning)
        {
            return;
        }
        IsScanning = true;
        ScanText = "Scanning...";
        _scanCts = new CancellationTokenSource();
        try
        {
            var progress = new Progress<LibraryScanProgress>(p =>
                ScanText = p.Completed ? $"Scan finished: {p.FilesSeen} files checked, {p.FilesImported} new or changed." : $"Scanning: {p.FilesSeen} files seen, {p.FilesImported} imported");
            await _library.ScanAsync(progress, _scanCts.Token);
            await LoadTabAsync();
        }
        catch (OperationCanceledException)
        {
            ScanText = "Scan cancelled.";
        }
        catch (Exception ex)
        {
            ScanText = "Scan failed.";
            Toast.ShowError(ex);
        }
        finally
        {
            IsScanning = false;
            _scanCts?.Dispose();
            _scanCts = null;
        }
    }

    [RelayCommand]
    private void CancelScan() => _scanCts?.Cancel();

    [RelayCommand]
    private Task OpenAlbumAsync(AlbumRow? row) => row is null
        ? Task.CompletedTask
        : GuardAsync(async () =>
        {
            var tracks = await _library.GetTracksAsync(new LibraryQuery(Album: row.Album.Album, Limit: 2000));
            var filtered = tracks
                .Where(t => string.IsNullOrWhiteSpace(row.Album.AlbumArtist)
                    || string.IsNullOrWhiteSpace(t.AlbumArtist)
                    || string.Equals(t.AlbumArtist, row.Album.AlbumArtist, StringComparison.OrdinalIgnoreCase))
                .OrderBy(t => t.DiscNumber ?? 1)
                .ThenBy(t => t.TrackNumber ?? int.MaxValue)
                .ThenBy(t => t.Title)
                .ToList();
            ShowDetail(row.Name, row.Artist, row.CoverUri, filtered, []);
        });

    [RelayCommand]
    private Task OpenArtistAsync(LibraryArtist? artist) => artist is null
        ? Task.CompletedTask
        : GuardAsync(async () =>
        {
            var tracks = await _library.GetTracksAsync(new LibraryQuery(Artist: artist.Name, Limit: 2000));
            var albums = (await _library.GetAlbumsAsync(artist.Name))
                .Where(a => string.Equals(a.AlbumArtist, artist.Name, StringComparison.OrdinalIgnoreCase))
                .Select(ToRow)
                .ToList();
            ShowDetail(artist.Name, $"{artist.AlbumCount} albums, {artist.TrackCount} tracks", albums.FirstOrDefault()?.CoverUri, tracks.OrderBy(t => t.Album).ThenBy(t => t.TrackNumber ?? int.MaxValue).ToList(), albums);
        });

    [RelayCommand]
    private Task OpenGenreAsync(LibraryGenre? genre) => genre is null
        ? Task.CompletedTask
        : GuardAsync(async () =>
        {
            var tracks = await _library.GetTracksAsync(new LibraryQuery(Genre: genre.Name, Limit: 2000));
            ShowDetail(genre.Name, $"{genre.TrackCount} tracks", null, tracks, []);
        });

    private void ShowDetail(string title, string? subtitle, Uri? cover, IReadOnlyList<LibraryTrack> tracks, IReadOnlyList<AlbumRow> albums)
    {
        DetailTitle = title;
        DetailSubtitle = subtitle;
        DetailCover = cover;
        Replace(DetailTracks, tracks.Select((t, i) => new TrackRow(t, i + 1)));
        Replace(DetailAlbums, albums);
        OnPropertyChanged(nameof(HasDetailAlbums));
        HasDetail = true;
    }

    [RelayCommand]
    private void Back()
    {
        HasDetail = false;
        DetailTracks.Clear();
        DetailAlbums.Clear();
    }

    [RelayCommand]
    private Task PlayAllAsync() => PlayListAsync(DetailTracks, 0, DetailTitle, DetailCover);

    [RelayCommand]
    private Task PlayFromAsync(TrackRow? row)
    {
        if (row is null)
        {
            return Task.CompletedTask;
        }
        var list = HasDetail ? DetailTracks : Tracks;
        return PlayListAsync(list, list.IndexOf(row), HasDetail ? DetailTitle : "My Music", HasDetail ? DetailCover : null);
    }

    private Task PlayListAsync(IReadOnlyList<TrackRow> rows, int start, string name, Uri? cover) => GuardAsync(async () =>
    {
        if (rows.Count == 0)
        {
            return;
        }
        var session = Speakers.Require();
        var items = rows.Select(r => _library.ToPlayItem(r.Track)).ToList();
        var request = new PlayRequest(name, "My Music", items, Math.Max(0, start), cover);
        await session.Controller.PlayAsync(request);
        await _recent.AddAsync(RecentKinds.Request, SourceIds.Library, name, $"My Music, {items.Count} tracks", cover, System.Text.Json.JsonSerializer.Serialize(request));
    });

    public override void Dispose()
    {
        _library.LibraryChanged -= OnLibraryChanged;
        _searchDebouncer.Cancel();
        _scanCts?.Cancel();
        base.Dispose();
    }
}
