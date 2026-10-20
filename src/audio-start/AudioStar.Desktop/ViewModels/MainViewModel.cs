using System.Collections.ObjectModel;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.DependencyInjection;

namespace AudioStar.Desktop.ViewModels;

public sealed partial class NavItem(PageKey key, string label, string glyph, IToastService toast) : ObservableObject
{
    public PageKey Key { get; } = key;

    public string Label { get; } = label;

    public string Glyph { get; } = glyph;

    [ObservableProperty]
    private bool _isSelected;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(ConnectText))]
    [NotifyPropertyChangedFor(nameof(CanDisconnect))]
    [NotifyPropertyChangedFor(nameof(IsOn))]
    private SourceConnectionState? _sourceState;

    public IMusicSource? Source { get; set; }

    public bool HasSource => Source is not null;

    public string ConnectText => SourceState == SourceConnectionState.Connected ? "Reconnect" : "Connect";

    public bool CanDisconnect => SourceState == SourceConnectionState.Connected;

    public bool IsOn => SourceState == SourceConnectionState.Connected;

    [RelayCommand]
    private Task ConnectAsync() => ConnectAndReportAsync();

    [RelayCommand]
    private Task DisconnectAsync() => Source!.DisconnectAsync();

    [RelayCommand]
    private Task ToggleConnectionAsync() => SourceState == SourceConnectionState.Connected ? Source!.DisconnectAsync() : ConnectAndReportAsync();

    private async Task ConnectAndReportAsync()
    {
        var status = await Source!.ConnectAsync();
        if (status.State != SourceConnectionState.Connected && !string.IsNullOrWhiteSpace(status.Message))
            toast.ShowError(status.Message);
    }
}

public sealed record NavGroup(string Header, ObservableCollection<NavItem> Items);

public interface IPageFactory
{
    PageViewModel Create(PageKey key);
}

public sealed class PageFactory(IServiceProvider services) : IPageFactory
{
    public PageViewModel Create(PageKey key) => key switch
    {
        PageKey.Dashboard => services.GetRequiredService<DashboardViewModel>(),
        PageKey.NowPlaying => services.GetRequiredService<NowPlayingViewModel>(),
        PageKey.Queue => services.GetRequiredService<QueueViewModel>(),
        PageKey.MyMusic => services.GetRequiredService<MyMusicViewModel>(),
        PageKey.HomeShare => services.GetRequiredService<HomeShareViewModel>(),
        PageKey.Radio => services.GetRequiredService<RadioViewModel>(),
        PageKey.YouTube => ActivatorUtilities.CreateInstance<SourceViewModel>(services, SourceIds.YouTube),
        PageKey.Spotify => ActivatorUtilities.CreateInstance<SourceViewModel>(services, SourceIds.Spotify),
        PageKey.SoundCloud => ActivatorUtilities.CreateInstance<SourceViewModel>(services, SourceIds.SoundCloud),
        PageKey.Recent => services.GetRequiredService<RecentViewModel>(),
        PageKey.Presets => services.GetRequiredService<PresetsViewModel>(),
        PageKey.DeviceSettings => services.GetRequiredService<DeviceSettingsViewModel>(),
        PageKey.AppSettings => services.GetRequiredService<AppSettingsViewModel>(),
        _ => throw new ArgumentOutOfRangeException(nameof(key), key, null)
    };
}

public sealed partial class MainViewModel : ObservableObject
{
    private readonly IPageFactory _pages;
    private readonly ICurrentSpeaker _speakers;
    private readonly IToastService _toast;
    private readonly List<NavItem> _items;
    private readonly List<IMusicSource> _sources = [];
    private bool _syncing;

    public MainViewModel(IPageFactory pages, INavigationService navigation, ICurrentSpeaker speakers, PlayerViewModel player, IToastService toast, IEnumerable<IMusicSource> sources, IUiDispatcher dispatcher)
    {
        _pages = pages;
        _speakers = speakers;
        _toast = toast;
        Player = player;
        Groups =
        [
            new NavGroup("Browse",
            new ObservableCollection<NavItem>
            {
                new NavItem(PageKey.Dashboard, "Home", "", toast),
                new NavItem(PageKey.MyMusic, "My Music", "", toast),
                new NavItem(PageKey.HomeShare, "Home Share", "", toast),
                new NavItem(PageKey.Radio, "Radio", "", toast)
            }),
            new NavGroup("Music services",
            new ObservableCollection<NavItem>
            {
                new NavItem(PageKey.YouTube, "YouTube", "", toast),
                new NavItem(PageKey.Spotify, "Spotify", "", toast),
                new NavItem(PageKey.SoundCloud, "SoundCloud", "", toast)
            }),
            new NavGroup("Library",
            new ObservableCollection<NavItem>
            {
                new NavItem(PageKey.Recent, "Recently played", "", toast),
                new NavItem(PageKey.Presets, "Presets", "", toast)
            }),
            new NavGroup("Settings",
            new ObservableCollection<NavItem>
            {
                new NavItem(PageKey.DeviceSettings, "Device settings", "", toast),
                new NavItem(PageKey.AppSettings, "App settings", "", toast)
            })
        ];
        _items = Groups.SelectMany(g => g.Items).ToList();
        WatchSources(sources, dispatcher);
        Toasts = toast.Toasts;
        SelectedSpeaker = speakers.Current;
        speakers.CurrentChanged += OnCurrentSpeakerChanged;
        navigation.NavigationRequested += (_, key) => Navigate(key);
    }

    public IReadOnlyList<NavGroup> Groups { get; }

    private void WatchSources(IEnumerable<IMusicSource> sources, IUiDispatcher dispatcher)
    {
        var sourceIds = new Dictionary<PageKey, string>
        {
            [PageKey.YouTube] = SourceIds.YouTube,
            [PageKey.Spotify] = SourceIds.Spotify,
            [PageKey.SoundCloud] = SourceIds.SoundCloud
        };
        foreach (var item in _items)
        {
            if (!sourceIds.TryGetValue(item.Key, out var id) || sources.FirstOrDefault(s => s.Id == id) is not { } source)
            {
                continue;
            }
            _sources.Add(source);
            item.Source = source;
            item.SourceState = source.Status.State;
            source.StatusChanged += (_, status) => dispatcher.Post(() =>
            {
                item.SourceState = status.State;
                SortServices();
            });
        }
    }

    private void SortServices()
    {
        var items = Groups.First(g => g.Header == "Music services").Items;
        var sorted = items.Where(i => i.IsOn).Concat(items.Where(i => !i.IsOn)).ToList();
        for (var i = 0; i < sorted.Count; i++)
        {
            var from = items.IndexOf(sorted[i]);
            if (from != i)
            {
                items.Move(from, i);
            }
        }
    }

    public PlayerViewModel Player { get; }

    public ObservableCollection<ISpeakerSession> Speakers => _speakers.Speakers;

    public ObservableCollection<ToastItem> Toasts { get; }

    [ObservableProperty]
    private PageViewModel? _current;

    [ObservableProperty]
    private ISpeakerSession? _selectedSpeaker;

    partial void OnSelectedSpeakerChanged(ISpeakerSession? value)
    {
        if (_syncing || value is null)
        {
            return;
        }
        _speakers.Select(value);
    }

    private void OnCurrentSpeakerChanged(object? sender, EventArgs e)
    {
        _syncing = true;
        try
        {
            SelectedSpeaker = _speakers.Current;
        }
        finally
        {
            _syncing = false;
        }
    }

    public void Start()
    {
        Navigate(PageKey.Dashboard);
        foreach (var source in _sources)
        {
            _ = source.ConnectSilentlyAsync();
        }
    }

    [RelayCommand]
    private void Navigate(PageKey key)
    {
        PageViewModel page;
        try
        {
            page = _pages.Create(key);
        }
        catch (Exception ex)
        {
            _toast.ShowError(ex);
            return;
        }
        var previous = Current;
        Current = page;
        previous?.Dispose();
        foreach (var item in _items)
        {
            item.IsSelected = item.Key == key;
        }
        _ = page.InitializeAsync();
    }
}
