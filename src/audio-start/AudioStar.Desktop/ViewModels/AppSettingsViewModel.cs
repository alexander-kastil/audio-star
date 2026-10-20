using System.Collections.ObjectModel;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AudioStar.Desktop.ViewModels;

public sealed partial class AppSettingsViewModel : PageViewModel
{
    private readonly ISettingsStore _store;
    private readonly IMusicLibrary _library;
    private readonly IDlnaServer _dlna;
    private readonly IDialogService _dialogs;

    public AppSettingsViewModel(IToastService toast, ISettingsStore store, IMusicLibrary library, IDlnaServer dlna, IDialogService dialogs) : base(toast)
    {
        _store = store;
        _library = library;
        _dlna = dlna;
        _dialogs = dialogs;
        var current = store.Current;
        _dlnaServerEnabled = current.DlnaServerEnabled;
        _dlnaServerName = current.DlnaServerName;
        _preventSleep = current.PreventSleep;
        _minimizeToTray = current.MinimizeToTray;
        _startWithWindows = Autostart.IsEnabled;
        _youTubeCookieSource = current.YouTubeCookieSource;
        _soundCloudProfileUrl = current.SoundCloudProfileUrl ?? "";
        _spotifyClientId = current.SpotifyClientId ?? "";
        _radioCountryCode = current.RadioCountryCode;
        _manualSpeakerIps = string.Join(Environment.NewLine, current.ManualSpeakerIps);
        _mediaServerPort = current.MediaServerPort.ToString();
        _eventListenerPort = current.EventListenerPort.ToString();
        SpotifyRedirectUri = $"http://127.0.0.1:{current.SpotifyRedirectPort}/callback";
        SyncFolders();
    }

    public override string Title => "App settings";

    public string SpotifyRedirectUri { get; }

    public ObservableCollection<string> Folders { get; } = [];

    [ObservableProperty]
    private bool _dlnaServerEnabled;

    [ObservableProperty]
    private string _dlnaServerName;

    [ObservableProperty]
    private bool _preventSleep;

    [ObservableProperty]
    private bool _minimizeToTray;

    [ObservableProperty]
    private bool _startWithWindows;

    [ObservableProperty]
    private string _youTubeCookieSource;

    [ObservableProperty]
    private string _soundCloudProfileUrl;

    [ObservableProperty]
    private string _spotifyClientId;

    [ObservableProperty]
    private string _radioCountryCode;

    [ObservableProperty]
    private string _manualSpeakerIps;

    [ObservableProperty]
    private string _mediaServerPort;

    [ObservableProperty]
    private string _eventListenerPort;

    private void SyncFolders()
    {
        Folders.Clear();
        foreach (var folder in _library.Folders)
        {
            Folders.Add(folder);
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
    private Task SaveAsync() => GuardAsync(async () =>
    {
        var mediaPort = ParsePort(MediaServerPort, "Media server port");
        var eventPort = ParsePort(EventListenerPort, "Event listener port");
        if (mediaPort == eventPort)
        {
            throw new InvalidOperationException("The media server port and the event port must differ.");
        }
        var country = RadioCountryCode.Trim().ToUpperInvariant();
        if (country.Length is not (0 or 2))
        {
            throw new InvalidOperationException("The radio country is a two letter code such as AT or DE.");
        }
        var ips = ManualSpeakerIps
            .Split(['\r', '\n', ',', ';', ' '], StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .Distinct()
            .ToList();
        foreach (var ip in ips.Where(ip => !System.Net.IPAddress.TryParse(ip, out _)))
        {
            throw new InvalidOperationException($"{ip} is not a valid IP address.");
        }
        var settings = _store.Current;
        settings.DlnaServerEnabled = DlnaServerEnabled;
        settings.DlnaServerName = string.IsNullOrWhiteSpace(DlnaServerName) ? "Audio Star" : DlnaServerName.Trim();
        settings.PreventSleep = PreventSleep;
        settings.MinimizeToTray = MinimizeToTray;
        settings.YouTubeCookieSource = YouTubeCookieSource.Trim();
        settings.SoundCloudProfileUrl = string.IsNullOrWhiteSpace(SoundCloudProfileUrl) ? null : SoundCloudProfileUrl.Trim();
        settings.SpotifyClientId = string.IsNullOrWhiteSpace(SpotifyClientId) ? null : SpotifyClientId.Trim();
        settings.RadioCountryCode = country;
        settings.ManualSpeakerIps = ips;
        var portsChanged = settings.MediaServerPort != mediaPort || settings.EventListenerPort != eventPort;
        settings.MediaServerPort = mediaPort;
        settings.EventListenerPort = eventPort;
        await _store.SaveAsync();
        Autostart.SetEnabled(StartWithWindows);
        await ApplyDlnaAsync(settings);
        Toast.Show(portsChanged ? "Settings saved. Restart Audio Star to apply the new ports." : "Settings saved.");
    });

    private async Task ApplyDlnaAsync(AudioStarSettings settings)
    {
        if (settings.DlnaServerEnabled && !_dlna.IsRunning)
        {
            await _dlna.StartAsync(CancellationToken.None);
        }
        else if (!settings.DlnaServerEnabled && _dlna.IsRunning)
        {
            await _dlna.StopAsync(CancellationToken.None);
        }
    }

    private static int ParsePort(string text, string name) =>
        int.TryParse(text.Trim(), out var port) && port is >= 1024 and <= 65535
            ? port
            : throw new InvalidOperationException($"{name} must be a number between 1024 and 65535.");
}
