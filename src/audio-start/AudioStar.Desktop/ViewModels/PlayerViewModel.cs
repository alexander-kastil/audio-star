using System.Windows.Threading;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.Logging;

namespace AudioStar.Desktop.ViewModels;

public sealed partial class PlayerViewModel : ObservableObject, IDisposable
{
    private static readonly TimeSpan TickInterval = TimeSpan.FromMilliseconds(500);
    private static readonly TimeSpan ResyncInterval = TimeSpan.FromSeconds(10);

    private readonly ICurrentSpeaker _speakers;
    private readonly IUiDispatcher _dispatcher;
    private readonly IToastService _toast;
    private readonly INavigationService _navigation;
    private readonly ILogger<PlayerViewModel> _logger;
    private readonly DispatcherTimer _timer;
    private readonly Debouncer _volumeDebouncer = new(TimeSpan.FromMilliseconds(180));
    private ISpeakerSession? _session;
    private LoopMode _loopMode = LoopMode.Default;
    private bool _applying;
    private DateTime _lastResync = DateTime.UtcNow;

    public PlayerViewModel(ICurrentSpeaker speakers, IUiDispatcher dispatcher, IToastService toast, INavigationService navigation, ILogger<PlayerViewModel> logger)
    {
        _speakers = speakers;
        _dispatcher = dispatcher;
        _toast = toast;
        _navigation = navigation;
        _logger = logger;
        _timer = new DispatcherTimer(DispatcherPriority.Background) { Interval = TickInterval };
        _timer.Tick += OnTick;
        _speakers.CurrentChanged += OnCurrentChanged;
        Attach(_speakers.Current);
        _timer.Start();
    }

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(NoSpeaker))]
    private bool _hasSpeaker;

    [ObservableProperty]
    private string _speakerName = "No speaker selected";

    [ObservableProperty]
    private string _title = "Nothing playing";

    [ObservableProperty]
    private string? _artist;

    [ObservableProperty]
    private string? _album;

    [ObservableProperty]
    private Uri? _coverUri;

    [ObservableProperty]
    private string? _quality;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(PlayGlyph))]
    [NotifyPropertyChangedFor(nameof(PlayToolTip))]
    private bool _isPlaying;

    [ObservableProperty]
    private double _durationSeconds;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(PositionText))]
    private double _positionSeconds;

    [ObservableProperty]
    private bool _isSeeking;

    [ObservableProperty]
    private double _volume;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(MuteGlyph))]
    private bool _muted;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(RepeatGlyph))]
    [NotifyPropertyChangedFor(nameof(RepeatActive))]
    [NotifyPropertyChangedFor(nameof(RepeatToolTip))]
    private RepeatMode _repeat;

    [ObservableProperty]
    private bool _shuffle;

    public bool NoSpeaker => !HasSpeaker;

    public string PlayGlyph => IsPlaying ? "" : "";

    public string PlayToolTip => IsPlaying ? "Pause" : "Play";

    public string MuteGlyph => Muted ? "" : "";

    public string RepeatGlyph => Repeat == RepeatMode.Single ? "" : "";

    public string RepeatToolTip => Repeat switch
    {
        RepeatMode.List => "Repeat all (click for repeat one)",
        RepeatMode.Single => "Repeat one (click to turn off)",
        _ => "Repeat off (click to repeat all)"
    };

    public bool RepeatActive => Repeat != RepeatMode.Off;

    public string PositionText => PlaybackFormat.Time(TimeSpan.FromSeconds(PositionSeconds));

    public string DurationText => HasDuration ? PlaybackFormat.Time(TimeSpan.FromSeconds(DurationSeconds)) : "Live";

    public bool HasDuration => DurationSeconds > 0;

    public string TrackLine => string.IsNullOrWhiteSpace(Artist) ? Title : $"{Title} - {Artist}";

    partial void OnDurationSecondsChanged(double value)
    {
        OnPropertyChanged(nameof(DurationText));
        OnPropertyChanged(nameof(HasDuration));
    }

    partial void OnTitleChanged(string value) => OnPropertyChanged(nameof(TrackLine));

    partial void OnArtistChanged(string? value) => OnPropertyChanged(nameof(TrackLine));

    partial void OnVolumeChanged(double value)
    {
        if (_applying || _session is null)
        {
            return;
        }
        var session = _session;
        var level = (int)Math.Round(value);
        _ = Guard(() => _volumeDebouncer.RunAsync(token => session.Controller.SetVolumeAsync(level, token)));
    }

    private void OnCurrentChanged(object? sender, EventArgs e) => Attach(_speakers.Current);

    private void Attach(ISpeakerSession? session)
    {
        if (_session is not null)
        {
            _session.StateChanged -= OnStateChanged;
        }
        _session = session;
        HasSpeaker = session is not null;
        if (session is null)
        {
            SpeakerName = "No speaker selected";
            Apply(PlaybackState.Empty);
            return;
        }
        SpeakerName = session.Info.Name;
        session.StateChanged += OnStateChanged;
        Apply(session.State);
        _ = Guard(async () =>
        {
            var state = await session.Controller.GetPlaybackStateAsync();
            _dispatcher.Post(() =>
            {
                if (ReferenceEquals(_session, session))
                {
                    Apply(state);
                }
            });
        });
    }

    private void OnStateChanged(object? sender, PlaybackState state)
    {
        var session = sender as ISpeakerSession;
        _dispatcher.Post(() =>
        {
            if (session is null || ReferenceEquals(_session, session))
            {
                Apply(state);
            }
        });
    }

    private void Apply(PlaybackState state)
    {
        _applying = true;
        try
        {
            var track = state.Track;
            Title = string.IsNullOrWhiteSpace(track?.Title) ? "Nothing playing" : track!.Title!;
            Artist = track?.Artist;
            Album = track?.Album;
            CoverUri = track?.ArtworkUri;
            Quality = PlaybackFormat.Quality(track);
            IsPlaying = state.State is TransportState.Playing or TransportState.Transitioning;
            DurationSeconds = track?.Duration.TotalSeconds ?? 0;
            if (!IsSeeking)
            {
                PositionSeconds = Math.Min(state.Position.TotalSeconds, DurationSeconds > 0 ? DurationSeconds : state.Position.TotalSeconds);
            }
            Volume = state.Volume;
            Muted = state.Muted;
            _loopMode = state.LoopMode;
            Repeat = PlaybackFormat.Repeat(state.LoopMode);
            Shuffle = PlaybackFormat.IsShuffle(state.LoopMode);
            _lastResync = DateTime.UtcNow;
        }
        finally
        {
            _applying = false;
        }
    }

    private void OnTick(object? sender, EventArgs e)
    {
        if (IsPlaying && !IsSeeking && DurationSeconds > 0)
        {
            PositionSeconds = Math.Min(PositionSeconds + TickInterval.TotalSeconds, DurationSeconds);
        }
        if (_session is not null && DateTime.UtcNow - _lastResync > ResyncInterval)
        {
            _lastResync = DateTime.UtcNow;
            var session = _session;
            _ = Task.Run(async () =>
            {
                try
                {
                    var state = await session.Controller.GetPlaybackStateAsync();
                    _dispatcher.Post(() =>
                    {
                        if (ReferenceEquals(_session, session))
                        {
                            Apply(state);
                        }
                    });
                }
                catch (Exception ex)
                {
                    _logger.LogDebug(ex, "Playback resync failed for {Speaker}", session.Info.Name);
                }
            });
        }
    }

    public void BeginSeek() => IsSeeking = true;

    public async Task CommitSeekAsync(double seconds)
    {
        IsSeeking = false;
        PositionSeconds = seconds;
        var session = _session;
        if (session is null)
        {
            return;
        }
        await Guard(() => session.Controller.SeekAsync(TimeSpan.FromSeconds(seconds)));
    }

    private async Task Guard(Func<Task> work)
    {
        try
        {
            await work();
        }
        catch (OperationCanceledException)
        {
        }
        catch (Exception ex)
        {
            _toast.ShowError(ex);
        }
    }

    [RelayCommand(CanExecute = nameof(HasSpeaker))]
    private Task PlayPauseAsync()
    {
        var controller = _session!.Controller;
        return IsPlaying ? controller.PauseAsync() : controller.PlayAsync();
    }

    [RelayCommand(CanExecute = nameof(HasSpeaker))]
    private Task NextAsync() => _session!.Controller.NextAsync();

    [RelayCommand(CanExecute = nameof(HasSpeaker))]
    private Task PreviousAsync() => _session!.Controller.PreviousAsync();

    [RelayCommand(CanExecute = nameof(HasSpeaker))]
    private Task ToggleMuteAsync() => _session!.Controller.SetMuteAsync(!Muted);

    [RelayCommand(CanExecute = nameof(HasSpeaker))]
    private Task CycleRepeatAsync() => SetLoopAsync(PlaybackFormat.NextLoop(_loopMode));

    [RelayCommand(CanExecute = nameof(HasSpeaker))]
    private Task ToggleShuffleAsync() => SetLoopAsync(PlaybackFormat.NextShuffle(_loopMode));

    private async Task SetLoopAsync(LoopMode mode)
    {
        await _session!.Controller.SetLoopModeAsync(mode);
        _loopMode = mode;
        Repeat = PlaybackFormat.Repeat(mode);
        Shuffle = PlaybackFormat.IsShuffle(mode);
    }

    [RelayCommand]
    private void ShowQueue() => _navigation.Navigate(PageKey.Queue);

    [RelayCommand]
    private void ShowNowPlaying() => _navigation.Navigate(PageKey.NowPlaying);

    partial void OnHasSpeakerChanged(bool value)
    {
        PlayPauseCommand.NotifyCanExecuteChanged();
        NextCommand.NotifyCanExecuteChanged();
        PreviousCommand.NotifyCanExecuteChanged();
        ToggleMuteCommand.NotifyCanExecuteChanged();
        CycleRepeatCommand.NotifyCanExecuteChanged();
        ToggleShuffleCommand.NotifyCanExecuteChanged();
    }

    public void Dispose()
    {
        _timer.Stop();
        _speakers.CurrentChanged -= OnCurrentChanged;
        if (_session is not null)
        {
            _session.StateChanged -= OnStateChanged;
        }
    }
}
