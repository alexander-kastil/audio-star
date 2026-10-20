using System.Collections.ObjectModel;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AudioStar.Desktop.ViewModels;

public sealed partial class StationRow(RadioStation station, bool isFavorite) : ObservableObject
{
    public RadioStation Station { get; } = station;

    public string Name => Station.Name;

    public Uri? LogoUri => Station.LogoUri;

    public string Details => string.Join(" - ", new[]
    {
        Station.Country,
        Station.Tags.Count > 0 ? string.Join(", ", Station.Tags.Take(2)) : null,
        Station.Bitrate is > 0 ? $"{Station.Bitrate} kbps" : null
    }.Where(s => !string.IsNullOrWhiteSpace(s)));

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(FavoriteGlyph))]
    [NotifyPropertyChangedFor(nameof(FavoriteToolTip))]
    private bool _isFavorite = isFavorite;

    public string FavoriteGlyph => IsFavorite ? "" : "";

    public string FavoriteToolTip => IsFavorite ? "Remove from favorites" : "Add to favorites";
}

public sealed class StationSection(string title, IReadOnlyList<StationRow> stations)
{
    public string Title { get; } = title;

    public IReadOnlyList<StationRow> Stations { get; } = stations;
}

public sealed partial class RadioViewModel : SpeakerPageViewModel
{
    private readonly IRadioDirectory _radio;
    private readonly IUiDispatcher _dispatcher;
    private readonly Debouncer _searchDebouncer = new(TimeSpan.FromMilliseconds(500));
    private readonly List<StationRow> _rows = [];

    public RadioViewModel(IToastService toast, ICurrentSpeaker speakers, IRadioDirectory radio, IUiDispatcher dispatcher) : base(toast, speakers)
    {
        _radio = radio;
        _dispatcher = dispatcher;
        _radio.FavoritesChanged += OnFavoritesChanged;
    }

    public override string Title => "Radio";

    public ObservableCollection<StationSection> Sections { get; } = [];

    public ObservableCollection<StationRow> Results { get; } = [];

    [ObservableProperty]
    private string _query = "";

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(NoResults))]
    private bool _isSearching;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(NoResults))]
    private bool _searched;

    public bool NoResults => IsSearching && Searched && Results.Count == 0;

    protected override void OnSpeakerSwitched()
    {
    }

    public override async Task LoadAsync()
    {
        var home = await _radio.GetHomeAsync();
        Sections.Clear();
        _rows.Clear();
        var favorites = _radio.Favorites;
        if (favorites.Count > 0)
        {
            Sections.Add(new StationSection("Favorites", favorites.Select(f => Row(f)).ToList()));
        }
        foreach (var section in home)
        {
            Sections.Add(new StationSection(section.Title, section.Stations.Select(s => Row(s)).ToList()));
        }
    }

    private StationRow Row(RadioStation station)
    {
        var row = new StationRow(station, _radio.Favorites.Any(f => f.Id == station.Id));
        _rows.Add(row);
        return row;
    }

    partial void OnQueryChanged(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            _searchDebouncer.Cancel();
            IsSearching = false;
            Searched = false;
            Results.Clear();
            return;
        }
        _ = GuardAsync(() => _searchDebouncer.RunAsync(_ => SearchAsync()));
    }

    [RelayCommand]
    private Task SearchAsync() => GuardAsync(async () =>
    {
        var text = Query.Trim();
        if (text.Length == 0)
        {
            return;
        }
        IsBusy = true;
        try
        {
            var found = await _radio.SearchAsync(text);
            Results.Clear();
            foreach (var station in found)
            {
                Results.Add(Row(station));
            }
            IsSearching = true;
            Searched = true;
            OnPropertyChanged(nameof(NoResults));
        }
        finally
        {
            IsBusy = false;
        }
    });

    [RelayCommand]
    private Task PlayAsync(StationRow? row) => row is null
        ? Task.CompletedTask
        : GuardAsync(() => _radio.PlayAsync(Speakers.Require(), row.Station));

    [RelayCommand]
    private Task ToggleFavoriteAsync(StationRow? row) => row is null
        ? Task.CompletedTask
        : GuardAsync(async () =>
        {
            var target = !row.IsFavorite;
            await _radio.SetFavoriteAsync(row.Station, target);
            row.IsFavorite = target;
        });

    private void OnFavoritesChanged(object? sender, EventArgs e) => _dispatcher.Post(() =>
    {
        var ids = _radio.Favorites.Select(f => f.Id).ToHashSet();
        foreach (var row in _rows)
        {
            row.IsFavorite = ids.Contains(row.Station.Id);
        }
    });

    public override void Dispose()
    {
        _radio.FavoritesChanged -= OnFavoritesChanged;
        _searchDebouncer.Cancel();
        base.Dispose();
    }
}
