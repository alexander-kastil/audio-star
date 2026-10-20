using System.Collections.ObjectModel;
using System.Collections.Specialized;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AudioStar.Desktop.ViewModels;

public sealed partial class DashboardViewModel : PageViewModel
{
    private readonly ISpeakerHub _hub;
    private readonly IGroupService _groups;
    private readonly ICurrentSpeaker _current;
    private readonly IUiDispatcher _dispatcher;
    private readonly IDialogService _dialogs;
    private readonly ISettingsStore _settings;
    private readonly Debouncer _refreshDebouncer = new(TimeSpan.FromMilliseconds(400));
    private readonly HashSet<ISpeakerSession> _subscribed = [];

    public DashboardViewModel(
        ISpeakerHub hub,
        IGroupService groups,
        ICurrentSpeaker current,
        IUiDispatcher dispatcher,
        IToastService toast,
        IDialogService dialogs,
        ISettingsStore settings) : base(toast)
    {
        _hub = hub;
        _groups = groups;
        _current = current;
        _dispatcher = dispatcher;
        _dialogs = dialogs;
        _settings = settings;
        _current.Speakers.CollectionChanged += OnSpeakersChanged;
    }

    public override string Title => "Home";

    public ObservableCollection<SpeakerCardViewModel> Cards { get; } = [];

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(IsEmpty))]
    private bool _loaded;

    [ObservableProperty]
    private string _ipAddress = "";

    public bool IsEmpty => Loaded && Cards.Count == 0;

    public override async Task LoadAsync()
    {
        IReadOnlyList<SpeakerGroup> active;
        try
        {
            active = await _groups.GetActiveGroupsAsync();
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            active = [];
            Toast.ShowError(ex);
        }
        Rebuild(active);
    }

    private void Rebuild(IReadOnlyList<SpeakerGroup> active)
    {
        foreach (var card in Cards)
        {
            card.Dispose();
        }
        Cards.Clear();
        var sessions = _current.Speakers.ToList();
        foreach (var known in sessions)
        {
            Subscribe(known);
        }
        var followerIds = new HashSet<string>();
        var groupByLeader = new Dictionary<string, SpeakerGroup>();
        foreach (var group in active)
        {
            if (sessions.All(s => s.Info.Id != group.LeaderId) || group.Members.Count < 2)
            {
                continue;
            }
            groupByLeader[group.LeaderId] = group;
            foreach (var member in group.Members.Where(m => m.SpeakerId != group.LeaderId))
            {
                followerIds.Add(member.SpeakerId);
            }
        }
        foreach (var session in sessions)
        {
            if (followerIds.Contains(session.Info.Id))
            {
                continue;
            }
            groupByLeader.TryGetValue(session.Info.Id, out var group);
            Cards.Add(new SpeakerCardViewModel(session, group, _groups, _current, _dispatcher, Toast, _dialogs, RequestRefresh));
        }
        Loaded = true;
        OnPropertyChanged(nameof(IsEmpty));
    }

    private void Subscribe(ISpeakerSession session)
    {
        if (_subscribed.Add(session))
        {
            session.GroupChanged += OnGroupChanged;
        }
    }

    private void OnGroupChanged(object? sender, EventArgs e) => _dispatcher.Post(RequestRefresh);

    private void OnSpeakersChanged(object? sender, NotifyCollectionChangedEventArgs e) => RequestRefresh();

    private void RequestRefresh() => _ = GuardAsync(() => _refreshDebouncer.RunAsync(_ => LoadAsync()));

    [RelayCommand]
    private Task RefreshAsync() => GuardAsync(async () =>
    {
        IsBusy = true;
        try
        {
            await _hub.RefreshAsync();
            await LoadAsync();
        }
        finally
        {
            IsBusy = false;
        }
    });

    [RelayCommand]
    private Task PlayAllAsync() => GuardAsync(() => Task.WhenAll(Cards.Select(c => c.PlayAsync())));

    [RelayCommand]
    private Task PauseAllAsync() => GuardAsync(() => Task.WhenAll(Cards.Select(c => c.PauseAsync())));

    [RelayCommand]
    private Task NewGroupAsync() => GuardAsync(async () =>
    {
        await _dialogs.ShowGroupEditorAsync(null);
        RequestRefresh();
    });

    [RelayCommand]
    private Task AddSpeakerAsync() => GuardAsync(async () =>
    {
        var address = IpAddress.Trim();
        if (address.Length == 0)
        {
            return;
        }
        var session = await _hub.AddByIpAsync(address);
        if (session is null)
        {
            Toast.ShowError($"No speaker answered at {address}.");
            return;
        }
        IpAddress = "";
        Toast.Show($"Added {session.Info.Name}.");
        if (!_settings.Current.ManualSpeakerIps.Contains(address))
        {
            _settings.Current.ManualSpeakerIps.Add(address);
            await _settings.SaveAsync();
        }
        RequestRefresh();
    });

    public override void Dispose()
    {
        _current.Speakers.CollectionChanged -= OnSpeakersChanged;
        _refreshDebouncer.Cancel();
        foreach (var session in _subscribed)
        {
            session.GroupChanged -= OnGroupChanged;
        }
        _subscribed.Clear();
        foreach (var card in Cards)
        {
            card.Dispose();
        }
        base.Dispose();
    }
}
