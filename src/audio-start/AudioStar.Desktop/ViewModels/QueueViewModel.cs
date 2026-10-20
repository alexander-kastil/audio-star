using System.Collections.ObjectModel;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AudioStar.Desktop.ViewModels;

public sealed class QueueRow(QueueTrack track, bool isCurrent)
{
    public QueueTrack Track { get; } = track;

    public int Number { get; } = track.Index;

    public string Title => Track.Title;

    public string? Artist => Track.Artist;

    public string? Album => Track.Album;

    public string Subtitle => string.Join(" - ", new[] { Track.Artist, Track.Album }.Where(v => !string.IsNullOrWhiteSpace(v)));

    public Uri? ArtworkUri => Track.ArtworkUri;

    public bool IsCurrent { get; } = isCurrent;

    public string Duration => Track.Duration is { } d ? PlaybackFormat.Time(d) : "";
}

public sealed partial class QueueViewModel : SpeakerPageViewModel
{
    private readonly IUiDispatcher _dispatcher;
    private readonly Debouncer _reload = new(TimeSpan.FromMilliseconds(600));
    private ISpeakerSession? _watched;
    private string? _lastTrackUri;

    public QueueViewModel(IToastService toast, ICurrentSpeaker speakers, IUiDispatcher dispatcher) : base(toast, speakers)
    {
        _dispatcher = dispatcher;
    }

    public override string Title => "Queue";

    public ObservableCollection<QueueRow> Rows { get; } = [];

    [ObservableProperty]
    private string _queueName = "";

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(IsEmpty))]
    private bool _loaded;

    public bool IsEmpty => Loaded && Rows.Count == 0;

    public string EmptyText => Speaker is null ? "Select a speaker to see its queue." : "The queue is empty.";

    public override async Task LoadAsync()
    {
        Watch(Speaker);
        Rows.Clear();
        QueueName = "";
        OnPropertyChanged(nameof(EmptyText));
        if (Speaker is null)
        {
            Loaded = true;
            OnPropertyChanged(nameof(IsEmpty));
            return;
        }
        var queue = await Speaker.Controller.GetQueueAsync();
        if (queue is not null)
        {
            QueueName = string.IsNullOrWhiteSpace(queue.SourceName) ? queue.Name : $"{queue.Name} ({queue.SourceName})";
            foreach (var track in queue.Tracks)
            {
                Rows.Add(new QueueRow(track, track.Index == queue.CurrentIndex));
            }
        }
        Loaded = true;
        OnPropertyChanged(nameof(IsEmpty));
    }

    private void Watch(ISpeakerSession? session)
    {
        if (_watched is not null)
        {
            _watched.StateChanged -= OnStateChanged;
        }
        _watched = session;
        _lastTrackUri = session?.State.Track?.TrackUri;
        if (session is not null)
        {
            session.StateChanged += OnStateChanged;
        }
    }

    private void OnStateChanged(object? sender, PlaybackState state)
    {
        var uri = state.Track?.TrackUri;
        if (uri == _lastTrackUri)
        {
            return;
        }
        _lastTrackUri = uri;
        _dispatcher.Post(() => _ = GuardAsync(() => _reload.RunAsync(_ => LoadAsync())));
    }

    [RelayCommand]
    private Task JumpAsync(QueueRow? row) => row is null || Speaker is null
        ? Task.CompletedTask
        : GuardAsync(async () =>
        {
            await Speaker.Controller.PlayQueueIndexAsync(row.Track.Index);
            await LoadAsync();
        });

    [RelayCommand]
    private Task RemoveAsync(QueueRow? row) => row is null || Speaker is null
        ? Task.CompletedTask
        : GuardAsync(async () =>
        {
            await Speaker.Controller.RemoveQueueIndexAsync(row.Track.Index);
            await LoadAsync();
        });

    [RelayCommand]
    private Task RefreshAsync() => InitializeAsync();

    public override void Dispose()
    {
        _reload.Cancel();
        Watch(null);
        base.Dispose();
    }
}
