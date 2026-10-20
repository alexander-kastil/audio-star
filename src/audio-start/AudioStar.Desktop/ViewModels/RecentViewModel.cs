using System.Collections.ObjectModel;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AudioStar.Desktop.ViewModels;

public sealed class RecentRow(RecentItem item)
{
    public RecentItem Item { get; } = item;

    public string Title => Item.Title;

    public string? Subtitle => Item.Subtitle;

    public Uri? ArtworkUri => Item.ArtworkUri;

    public string PlayedText => Item.PlayedAt.ToLocalTime().ToString("g");
}

public sealed partial class RecentViewModel : PageViewModel
{
    private readonly IRecentlyPlayed _recent;
    private readonly ICurrentSpeaker _speakers;
    private readonly IUiDispatcher _dispatcher;

    public RecentViewModel(IToastService toast, IRecentlyPlayed recent, ICurrentSpeaker speakers, IUiDispatcher dispatcher) : base(toast)
    {
        _recent = recent;
        _speakers = speakers;
        _dispatcher = dispatcher;
        _recent.Changed += OnChanged;
    }

    public override string Title => "Recently played";

    public ObservableCollection<RecentRow> Rows { get; } = [];

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(IsEmpty))]
    private bool _loaded;

    public bool IsEmpty => Loaded && Rows.Count == 0;

    private void OnChanged(object? sender, EventArgs e) => _dispatcher.Post(() => _ = GuardAsync(LoadAsync));

    public override async Task LoadAsync()
    {
        var items = await _recent.GetAsync();
        Rows.Clear();
        foreach (var item in items)
        {
            Rows.Add(new RecentRow(item));
        }
        Loaded = true;
        OnPropertyChanged(nameof(IsEmpty));
    }

    [RelayCommand]
    private Task ReplayAsync(RecentRow? row) => row is null
        ? Task.CompletedTask
        : GuardAsync(() => _recent.ReplayAsync(_speakers.Require(), row.Item));

    [RelayCommand]
    private Task RemoveAsync(RecentRow? row) => row is null
        ? Task.CompletedTask
        : GuardAsync(async () =>
        {
            await _recent.RemoveAsync(row.Item.Id);
            Rows.Remove(row);
            OnPropertyChanged(nameof(IsEmpty));
        });

    public override void Dispose()
    {
        _recent.Changed -= OnChanged;
        base.Dispose();
    }
}
