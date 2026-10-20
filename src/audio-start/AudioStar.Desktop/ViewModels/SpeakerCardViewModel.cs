using System.Collections.ObjectModel;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AudioStar.Desktop.ViewModels;

public sealed partial class SpeakerCardViewModel : ObservableObject, IDisposable
{
    private readonly IGroupService _groups;
    private readonly ICurrentSpeaker _current;
    private readonly IUiDispatcher _dispatcher;
    private readonly IToastService _toast;
    private readonly IDialogService _dialogs;
    private readonly Action _changed;
    private readonly Debouncer _debouncer = new(TimeSpan.FromMilliseconds(180));
    private bool _applying;

    public SpeakerCardViewModel(
        ISpeakerSession session,
        SpeakerGroup? group,
        IGroupService groups,
        ICurrentSpeaker current,
        IUiDispatcher dispatcher,
        IToastService toast,
        IDialogService dialogs,
        Action changed)
    {
        Session = session;
        _groups = groups;
        _current = current;
        _dispatcher = dispatcher;
        _toast = toast;
        _dialogs = dialogs;
        _changed = changed;
        IsGroup = group is not null;
        Name = group is not null && !string.IsNullOrWhiteSpace(group.Name) ? group.Name : session.Info.Name;
        Subtitle = group is not null ? $"{group.Members.Count} speakers" : session.Info.Model;
        if (group is not null)
        {
            foreach (var member in group.Members)
            {
                Members.Add(new MemberVolumeViewModel(session.Info.Id, member, groups, toast));
            }
        }
        session.StateChanged += OnStateChanged;
        Apply(session.State);
    }

    public ISpeakerSession Session { get; }

    public bool IsGroup { get; }

    public string Name { get; }

    public string Subtitle { get; }

    public ObservableCollection<MemberVolumeViewModel> Members { get; } = [];

    [ObservableProperty]
    private string _track = "Nothing playing";

    [ObservableProperty]
    private string? _artist;

    [ObservableProperty]
    private Uri? _coverUri;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(PlayGlyph))]
    [NotifyPropertyChangedFor(nameof(PlayToolTip))]
    private bool _isPlaying;

    [ObservableProperty]
    private double _volume;

    public string PlayGlyph => IsPlaying ? "" : "";

    public string PlayToolTip => IsPlaying ? "Pause" : "Play";

    partial void OnVolumeChanged(double value)
    {
        if (_applying)
        {
            return;
        }
        var level = (int)Math.Round(value);
        _ = Guard(() => _debouncer.RunAsync(token => IsGroup
            ? _groups.SetGroupVolumeAsync(Session.Info.Id, level, token)
            : Session.Controller.SetVolumeAsync(level, token)));
    }

    private void OnStateChanged(object? sender, PlaybackState state) => _dispatcher.Post(() => Apply(state));

    private void Apply(PlaybackState state)
    {
        _applying = true;
        try
        {
            Track = string.IsNullOrWhiteSpace(state.Track?.Title) ? "Nothing playing" : state.Track!.Title!;
            Artist = state.Track?.Artist;
            CoverUri = state.Track?.ArtworkUri;
            IsPlaying = state.State is TransportState.Playing or TransportState.Transitioning;
            Volume = state.Volume;
        }
        finally
        {
            _applying = false;
        }
    }

    public Task PlayAsync() => Session.Controller.PlayAsync();

    public Task PauseAsync() => Session.Controller.PauseAsync();

    [RelayCommand]
    private Task PlayPauseAsync() => IsPlaying ? Session.Controller.PauseAsync() : Session.Controller.PlayAsync();

    [RelayCommand]
    private void Select() => _current.Select(Session);

    [RelayCommand]
    private async Task EditGroupAsync()
    {
        await _dialogs.ShowGroupEditorAsync(Session.Info.Id);
        _changed();
    }

    [RelayCommand]
    private async Task UngroupAsync()
    {
        await _groups.UngroupAsync(Session.Info.Id);
        _changed();
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

    public void Dispose() => Session.StateChanged -= OnStateChanged;
}
