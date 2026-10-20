using System.Collections.ObjectModel;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AudioStar.Desktop.ViewModels;

public sealed class ShareRow(DlnaItem item)
{
    public DlnaItem Item { get; } = item;

    public string Title => Item.Title;

    public bool IsContainer => Item.IsContainer;

    public bool IsPlayable => !Item.IsContainer && Item.ResourceUri is not null;

    public string Details => Item.IsContainer
        ? "Folder"
        : string.Join(" - ", new[] { Item.Artist, Item.Album }.Where(s => !string.IsNullOrWhiteSpace(s)));

    public string Duration => Item.Duration is { } d ? PlaybackFormat.Time(d) : "";

    public Uri? ArtworkUri => Item.ArtworkUri;

    public string Glyph => Item.IsContainer ? "" : "";
}

public sealed partial class HomeShareViewModel : SpeakerPageViewModel
{
    private readonly IHomeShareBrowser _browser;
    private readonly IUiDispatcher _dispatcher;
    private readonly IRecentlyPlayed _recent;
    private readonly Stack<(string Id, string Title)> _path = new();

    public HomeShareViewModel(IToastService toast, ICurrentSpeaker speakers, IHomeShareBrowser browser, IUiDispatcher dispatcher, IRecentlyPlayed recent) : base(toast, speakers)
    {
        _recent = recent;
        _browser = browser;
        _dispatcher = dispatcher;
        _browser.ServersChanged += OnServersChanged;
    }

    public override string Title => "Home Share";

    public ObservableCollection<DlnaServerInfo> Servers { get; } = [];

    public ObservableCollection<ShareRow> Rows { get; } = [];

    [ObservableProperty]
    private DlnaServerInfo? _selectedServer;

    [ObservableProperty]
    private string _location = "";

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CanGoUp))]
    private bool _isBrowsing;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(NoServers))]
    private bool _loaded;

    public bool NoServers => Loaded && Servers.Count == 0;

    public bool CanGoUp => IsBrowsing && _path.Count > 0;

    protected override void OnSpeakerSwitched()
    {
    }

    public override Task LoadAsync()
    {
        SyncServers();
        Loaded = true;
        OnPropertyChanged(nameof(NoServers));
        return Task.CompletedTask;
    }

    private void OnServersChanged(object? sender, EventArgs e) => _dispatcher.Post(SyncServers);

    private void SyncServers()
    {
        var current = _browser.Servers;
        foreach (var gone in Servers.Where(s => current.All(c => c.Id != s.Id)).ToList())
        {
            Servers.Remove(gone);
        }
        foreach (var server in current)
        {
            if (Servers.All(s => s.Id != server.Id))
            {
                Servers.Add(server);
            }
        }
        OnPropertyChanged(nameof(NoServers));
    }

    partial void OnSelectedServerChanged(DlnaServerInfo? value)
    {
        _path.Clear();
        Rows.Clear();
        IsBrowsing = false;
        Location = value?.Name ?? "";
        if (value is not null)
        {
            _ = InvokeBrowseAsync("0", value.Name, push: false);
        }
    }

    private Task InvokeBrowseAsync(string objectId, string title, bool push) => LoadGuardedAsync(async () =>
    {
        var server = SelectedServer ?? throw new InvalidOperationException("Select a server first.");
        var items = await _browser.BrowseAsync(server, objectId);
        if (push)
        {
            _path.Push((objectId, title));
        }
        Rows.Clear();
        foreach (var item in items.OrderByDescending(i => i.IsContainer).ThenBy(i => i.Title, StringComparer.CurrentCultureIgnoreCase))
        {
            Rows.Add(new ShareRow(item));
        }
        IsBrowsing = true;
        Location = string.Join(" / ", new[] { server.Name }.Concat(_path.Reverse().Select(p => p.Title)));
        OnPropertyChanged(nameof(CanGoUp));
    });

    private string CurrentId => _path.Count > 0 ? _path.Peek().Id : "0";

    [RelayCommand]
    private Task OpenAsync(ShareRow? row) => row is null
        ? Task.CompletedTask
        : row.IsContainer
            ? InvokeBrowseAsync(row.Item.Id, row.Title, push: true)
            : PlayFromAsync(row);

    [RelayCommand]
    private Task UpAsync()
    {
        if (_path.Count == 0)
        {
            return Task.CompletedTask;
        }
        _path.Pop();
        return InvokeBrowseAsync(CurrentId, string.Empty, push: false);
    }

    [RelayCommand]
    private Task PlayFromAsync(ShareRow? row) => row is null
        ? Task.CompletedTask
        : GuardAsync(async () =>
        {
            var playable = Rows.Where(r => r.IsPlayable).ToList();
            var index = playable.IndexOf(row);
            if (index < 0)
            {
                return;
            }
            await PlayAsync(playable.Select(r => r.Item).ToList(), index, Location);
        });

    [RelayCommand]
    private Task PlayContainerAsync(ShareRow? row) => row is null || !row.IsContainer
        ? Task.CompletedTask
        : GuardAsync(async () =>
        {
            var server = SelectedServer ?? throw new InvalidOperationException("Select a server first.");
            var items = (await _browser.BrowseAsync(server, row.Item.Id)).Where(i => !i.IsContainer && i.ResourceUri is not null).ToList();
            if (items.Count == 0)
            {
                Toast.Show("This folder has no playable items.");
                return;
            }
            await PlayAsync(items, 0, row.Title);
        });

    [RelayCommand]
    private Task PlayHereAsync() => GuardAsync(async () =>
    {
        var items = Rows.Where(r => r.IsPlayable).Select(r => r.Item).ToList();
        if (items.Count == 0)
        {
            Toast.Show("Nothing playable here.");
            return;
        }
        await PlayAsync(items, 0, Location);
    });

    private async Task PlayAsync(IReadOnlyList<DlnaItem> items, int start, string name)
    {
        var session = Speakers.Require();
        var playItems = items
            .Select(i => new PlayItem(i.Id, i.Title, i.Artist, i.Album, i.ResourceUri!, i.ArtworkUri, i.Duration))
            .ToList();
        var request = new PlayRequest(name, "Home Share", playItems, start, items[0].ArtworkUri);
        await session.Controller.PlayAsync(request);
        await _recent.AddAsync(RecentKinds.Request, SourceIds.HomeShare, name, $"Home Share, {playItems.Count} tracks", items[0].ArtworkUri, System.Text.Json.JsonSerializer.Serialize(request));
    }

    public override void Dispose()
    {
        _browser.ServersChanged -= OnServersChanged;
        base.Dispose();
    }
}
