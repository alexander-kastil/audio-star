using AudioStar.Core;
using AudioStar.Library.Data;
using Microsoft.Extensions.Logging;

namespace AudioStar.Library.Music;

internal sealed class MusicLibrary(TrackStore store, ISettingsStore settings, IMediaServer mediaServer, ILogger<MusicLibrary> logger) : IMusicLibrary, IAsyncDisposable
{
    private static readonly TimeSpan WatchDebounce = TimeSpan.FromSeconds(3);

    private readonly SemaphoreSlim _scanGate = new(1, 1);
    private readonly object _watchLock = new();
    private readonly List<FileSystemWatcher> _watchers = [];
    private Timer? _debounce;
    private string _foldersSignature = "";
    private CancellationTokenSource? _lifetime;

    public IReadOnlyList<string> Folders => settings.Current.MusicFolders.ToArray();

    public event EventHandler? LibraryChanged;

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        _lifetime = new CancellationTokenSource();
        await EnsureDefaultFolderAsync(cancellationToken);
        _foldersSignature = Signature();
        settings.Changed += OnSettingsChanged;
        RefreshWatchers();
        _ = Task.Run(() => ScanSafelyAsync(_lifetime.Token));
    }

    public async Task StopAsync()
    {
        settings.Changed -= OnSettingsChanged;
        _lifetime?.Cancel();
        DisposeWatchers();
        _debounce?.Dispose();
        _debounce = null;
        await Task.CompletedTask;
    }

    public async ValueTask DisposeAsync()
    {
        await StopAsync();
        _lifetime?.Dispose();
    }

    public async Task AddFolderAsync(string path, CancellationToken cancellationToken = default)
    {
        var full = Path.GetFullPath(path);
        if (settings.Current.MusicFolders.Any(f => string.Equals(Path.GetFullPath(f), full, StringComparison.OrdinalIgnoreCase)))
        {
            return;
        }
        settings.Current.MusicFolders.Add(full);
        _foldersSignature = Signature();
        await settings.SaveAsync(cancellationToken);
        RefreshWatchers();
        await ScanAsync(null, cancellationToken);
    }

    public async Task RemoveFolderAsync(string path, CancellationToken cancellationToken = default)
    {
        var full = Path.GetFullPath(path);
        var removed = settings.Current.MusicFolders.RemoveAll(f => string.Equals(Path.GetFullPath(f), full, StringComparison.OrdinalIgnoreCase));
        if (removed == 0)
        {
            return;
        }
        _foldersSignature = Signature();
        await settings.SaveAsync(cancellationToken);
        RefreshWatchers();
        await ScanAsync(null, cancellationToken);
    }

    public async Task ScanAsync(IProgress<LibraryScanProgress>? progress, CancellationToken cancellationToken = default)
    {
        await _scanGate.WaitAsync(cancellationToken);
        try
        {
            var index = await store.GetIndexAsync(cancellationToken);
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var batch = new List<TrackWrite>();
            var filesSeen = 0;
            var imported = 0;
            var options = new EnumerationOptions { RecurseSubdirectories = true, IgnoreInaccessible = true };
            foreach (var folder in Folders.Where(Directory.Exists))
            {
                foreach (var file in Directory.EnumerateFiles(folder, "*", options).Where(AudioFormats.IsSupported))
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    filesSeen++;
                    seen.Add(file);
                    var info = new FileInfo(file);
                    var ticks = info.LastWriteTimeUtc.Ticks;
                    if (index.TryGetValue(file, out var known) && known.Size == info.Length && known.ModifiedTicks == ticks)
                    {
                        continue;
                    }
                    var track = await Task.Run(() => TagReader.Read(file), cancellationToken);
                    batch.Add(new TrackWrite(track, info.Length, ticks));
                    imported++;
                    if (batch.Count >= 200)
                    {
                        await store.UpsertAsync(batch, cancellationToken);
                        batch.Clear();
                        progress?.Report(new LibraryScanProgress(filesSeen, imported, file, false));
                    }
                }
            }
            await store.UpsertAsync(batch, cancellationToken);
            var vanished = index.Keys.Where(k => !seen.Contains(k)).ToList();
            await store.DeleteAsync(vanished, cancellationToken);
            progress?.Report(new LibraryScanProgress(filesSeen, imported, null, true));
            if (imported > 0 || vanished.Count > 0)
            {
                LibraryChanged?.Invoke(this, EventArgs.Empty);
            }
        }
        finally
        {
            _scanGate.Release();
        }
    }

    public Task<IReadOnlyList<LibraryAlbum>> GetAlbumsAsync(string? search = null, CancellationToken cancellationToken = default) => store.GetAlbumsAsync(search, cancellationToken);

    public Task<IReadOnlyList<LibraryArtist>> GetArtistsAsync(string? search = null, CancellationToken cancellationToken = default) => store.GetArtistsAsync(search, cancellationToken);

    public Task<IReadOnlyList<LibraryGenre>> GetGenresAsync(CancellationToken cancellationToken = default) => store.GetGenresAsync(cancellationToken);

    public Task<IReadOnlyList<LibraryTrack>> GetTracksAsync(LibraryQuery query, CancellationToken cancellationToken = default) => store.GetTracksAsync(query, cancellationToken);

    public PlayItem ToPlayItem(LibraryTrack track) => new(
        "library:" + track.Id,
        track.Title,
        track.Artist ?? track.AlbumArtist,
        track.Album,
        mediaServer.GetFileUri(track.Path),
        track.HasCover ? mediaServer.GetCoverUri(track.Path) : null,
        track.Duration > TimeSpan.Zero ? track.Duration : null);

    private async Task EnsureDefaultFolderAsync(CancellationToken cancellationToken)
    {
        if (settings.Current.MusicFolders.Count > 0)
        {
            return;
        }
        var music = Environment.GetFolderPath(Environment.SpecialFolder.MyMusic);
        if (string.IsNullOrEmpty(music))
        {
            return;
        }
        settings.Current.MusicFolders.Add(music);
        await settings.SaveAsync(cancellationToken);
    }

    private string Signature() => string.Join('|', settings.Current.MusicFolders.Select(f => f.ToLowerInvariant()));

    private async Task ScanSafelyAsync(CancellationToken cancellationToken)
    {
        try
        {
            await ScanAsync(null, cancellationToken);
        }
        catch (OperationCanceledException)
        {
        }
        catch (Exception ex)
        {
            logger.LogWarning(ex, "Library scan failed");
        }
    }

    private void OnSettingsChanged(object? sender, EventArgs e)
    {
        var signature = Signature();
        if (signature == _foldersSignature)
        {
            return;
        }
        _foldersSignature = signature;
        RefreshWatchers();
        ScheduleScan();
    }

    private void RefreshWatchers()
    {
        lock (_watchLock)
        {
            DisposeWatchers();
            foreach (var folder in Folders.Where(Directory.Exists))
            {
                try
                {
                    var watcher = new FileSystemWatcher(folder)
                    {
                        IncludeSubdirectories = true,
                        NotifyFilter = NotifyFilters.FileName | NotifyFilters.DirectoryName | NotifyFilters.LastWrite | NotifyFilters.Size,
                        InternalBufferSize = 64 * 1024
                    };
                    watcher.Created += OnFileEvent;
                    watcher.Changed += OnFileEvent;
                    watcher.Deleted += OnFileEvent;
                    watcher.Renamed += OnFileEvent;
                    watcher.Error += (_, e) => logger.LogWarning(e.GetException(), "Folder watcher error in {Folder}", folder);
                    watcher.EnableRaisingEvents = true;
                    _watchers.Add(watcher);
                }
                catch (Exception ex) when (ex is ArgumentException or IOException or PlatformNotSupportedException)
                {
                    logger.LogWarning(ex, "Cannot watch {Folder}", folder);
                }
            }
        }
    }

    private void DisposeWatchers()
    {
        lock (_watchLock)
        {
            foreach (var watcher in _watchers)
            {
                watcher.Dispose();
            }
            _watchers.Clear();
        }
    }

    private void OnFileEvent(object sender, FileSystemEventArgs e)
    {
        if (Directory.Exists(e.FullPath) || AudioFormats.IsSupported(e.FullPath) || e.ChangeType == WatcherChangeTypes.Deleted)
        {
            ScheduleScan();
        }
    }

    private void ScheduleScan()
    {
        lock (_watchLock)
        {
            _debounce ??= new Timer(_ => _ = Task.Run(() => ScanSafelyAsync(_lifetime?.Token ?? CancellationToken.None)));
            _debounce.Change(WatchDebounce, Timeout.InfiniteTimeSpan);
        }
    }
}
