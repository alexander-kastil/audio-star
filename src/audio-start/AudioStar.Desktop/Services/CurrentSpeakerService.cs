using System.Collections.ObjectModel;
using AudioStar.Core;

namespace AudioStar.Desktop.Services;

public interface ICurrentSpeaker
{
    ObservableCollection<ISpeakerSession> Speakers { get; }
    ISpeakerSession? Current { get; }
    event EventHandler? CurrentChanged;
    void Select(ISpeakerSession? speaker);
    ISpeakerSession Require();
}

public sealed class CurrentSpeakerService : ICurrentSpeaker, IDisposable
{
    private readonly ISpeakerHub _hub;
    private readonly ISettingsStore _settings;
    private readonly IUiDispatcher _dispatcher;
    private readonly IToastService _toast;
    private ISpeakerSession? _current;

    public CurrentSpeakerService(ISpeakerHub hub, ISettingsStore settings, IUiDispatcher dispatcher, IToastService toast)
    {
        _hub = hub;
        _settings = settings;
        _dispatcher = dispatcher;
        _toast = toast;
        _hub.SpeakerAdded += OnSpeakerAdded;
        _hub.SpeakerRemoved += OnSpeakerRemoved;
        foreach (var speaker in _hub.Speakers)
        {
            Speakers.Add(speaker);
        }
        Restore();
    }

    public ObservableCollection<ISpeakerSession> Speakers { get; } = [];

    public ISpeakerSession? Current => _current;

    public event EventHandler? CurrentChanged;

    public void Select(ISpeakerSession? speaker)
    {
        if (ReferenceEquals(_current, speaker))
        {
            return;
        }
        _current = speaker;
        if (speaker is not null && _settings.Current.LastSpeakerId != speaker.Info.Id)
        {
            _settings.Current.LastSpeakerId = speaker.Info.Id;
            _ = SaveAsync();
        }
        CurrentChanged?.Invoke(this, EventArgs.Empty);
    }

    public ISpeakerSession Require() =>
        _current ?? throw new InvalidOperationException("Select a speaker first.");

    private async Task SaveAsync()
    {
        try
        {
            await _settings.SaveAsync();
        }
        catch (Exception ex)
        {
            _toast.ShowError(ex);
        }
    }

    private void OnSpeakerAdded(object? sender, ISpeakerSession speaker) => _dispatcher.Post(() =>
    {
        if (Speakers.Any(s => s.Info.Id == speaker.Info.Id))
        {
            return;
        }
        Speakers.Add(speaker);
        Restore();
    });

    private void OnSpeakerRemoved(object? sender, ISpeakerSession speaker) => _dispatcher.Post(() =>
    {
        var existing = Speakers.FirstOrDefault(s => s.Info.Id == speaker.Info.Id);
        if (existing is not null)
        {
            Speakers.Remove(existing);
        }
        if (_current is not null && _current.Info.Id == speaker.Info.Id)
        {
            _current = null;
            Restore();
            CurrentChanged?.Invoke(this, EventArgs.Empty);
        }
    });

    private void Restore()
    {
        if (_current is not null || Speakers.Count == 0)
        {
            return;
        }
        var last = _settings.Current.LastSpeakerId;
        var pick = Speakers.FirstOrDefault(s => s.Info.Id == last);
        if (pick is null && !string.IsNullOrEmpty(last))
        {
            return;
        }
        Select(pick ?? Speakers[0]);
    }

    public void Dispose()
    {
        _hub.SpeakerAdded -= OnSpeakerAdded;
        _hub.SpeakerRemoved -= OnSpeakerRemoved;
    }
}
