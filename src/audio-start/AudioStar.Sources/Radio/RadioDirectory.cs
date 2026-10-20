using System.Globalization;
using System.Text.Json;
using AudioStar.Core;
using Microsoft.Extensions.Logging;

namespace AudioStar.Sources.Radio;

public sealed class RadioDirectory : IRadioDirectory
{
    private const int SectionSize = 20;

    private static readonly (string Key, string Title, string Tag)[] TagSections =
    [
        ("top-music", "Top Music", "music"),
        ("top-news", "Top News", "news"),
        ("top-talk", "Top Talk", "talk"),
        ("top-sports", "Top Sports", "sports"),
        ("relax", "Relax & Unwind", "relax")
    ];

    private readonly RadioBrowserClient _client;
    private readonly ISettingsStore _settings;
    private readonly IRecentlyPlayed _recentlyPlayed;
    private readonly ILogger<RadioDirectory> _logger;
    private readonly string _favoritesPath;
    private readonly object _favoritesLock = new();
    private List<RadioStation> _favorites;

    public RadioDirectory(RadioBrowserClient client, ISettingsStore settings, IRecentlyPlayed recentlyPlayed, ILogger<RadioDirectory> logger)
        : this(client, settings, recentlyPlayed, logger, Path.Combine(AppPaths.DataDirectory, "radio-favorites.json"))
    {
    }

    internal RadioDirectory(RadioBrowserClient client, ISettingsStore settings, IRecentlyPlayed recentlyPlayed, ILogger<RadioDirectory> logger, string favoritesPath)
    {
        _client = client;
        _settings = settings;
        _recentlyPlayed = recentlyPlayed;
        _logger = logger;
        _favoritesPath = favoritesPath;
        _favorites = LoadFavorites();
    }

    public IReadOnlyList<RadioStation> Favorites
    {
        get
        {
            lock (_favoritesLock)
            {
                return _favorites.ToList();
            }
        }
    }

    public event EventHandler? FavoritesChanged;

    public async Task<IReadOnlyList<RadioSection>> GetHomeAsync(CancellationToken cancellationToken = default)
    {
        var country = CountryCode();
        var popular = country is null ? _client.TopClickedAsync(SectionSize, cancellationToken) : _client.TopByCountryAsync(country, SectionSize, cancellationToken);
        var tagged = TagSections.Select(s => _client.ByTagAsync(s.Tag, 0, SectionSize, cancellationToken)).ToList();
        await Task.WhenAll(tagged.Prepend(popular));

        var sections = new List<RadioSection> { new("popular", "Popular in your area", popular.Result) };
        for (var i = 0; i < TagSections.Length; i++)
        {
            sections.Add(new RadioSection(TagSections[i].Key, TagSections[i].Title, tagged[i].Result));
        }
        var favorites = Favorites;
        if (favorites.Count > 0)
        {
            sections.Add(new RadioSection("favorites", "Favorites", favorites));
        }
        return sections;
    }

    public Task<IReadOnlyList<RadioStation>> SearchAsync(string query, int offset = 0, int limit = 50, CancellationToken cancellationToken = default) =>
        _client.SearchAsync(query, offset, limit, cancellationToken);

    public Task<IReadOnlyList<RadioStation>> GetByTagAsync(string tag, int offset = 0, int limit = 50, CancellationToken cancellationToken = default) =>
        _client.ByTagAsync(tag, offset, limit, cancellationToken);

    public async Task SetFavoriteAsync(RadioStation station, bool favorite, CancellationToken cancellationToken = default)
    {
        lock (_favoritesLock)
        {
            _favorites.RemoveAll(s => s.Id == station.Id);
            if (favorite)
            {
                _favorites.Add(station);
            }
            Directory.CreateDirectory(Path.GetDirectoryName(_favoritesPath)!);
            var temp = _favoritesPath + ".tmp";
            File.WriteAllText(temp, JsonSerializer.Serialize(_favorites, new JsonSerializerOptions { WriteIndented = true }));
            File.Move(temp, _favoritesPath, overwrite: true);
        }
        FavoritesChanged?.Invoke(this, EventArgs.Empty);
        await Task.CompletedTask;
    }

    public async Task PlayAsync(ISpeakerSession speaker, RadioStation station, CancellationToken cancellationToken = default)
    {
        await speaker.Controller.PlayUrlAsync(station.Name, station.StreamUri, station.LogoUri, "Radio", cancellationToken);
        var item = new PlayItem(station.Id, station.Name, null, null, station.StreamUri, station.LogoUri, null);
        var request = new PlayRequest(station.Name, "Radio", [item], 0, station.LogoUri);
        var subtitle = station.Country is null ? "Radio" : $"Radio, {station.Country}";
        await _recentlyPlayed.AddAsync(RecentKinds.Request, SourceIds.Radio, station.Name, subtitle, station.LogoUri, JsonSerializer.Serialize(request), cancellationToken);
        _ = _client.RegisterClickAsync(station.Id, CancellationToken.None);
        _logger.LogInformation("Playing radio station {Station} on {Speaker}", station.Name, speaker.Info.Name);
    }

    private string? CountryCode()
    {
        var configured = _settings.Current.RadioCountryCode?.Trim();
        if (!string.IsNullOrEmpty(configured))
        {
            return configured.ToUpperInvariant();
        }
        var region = RegionInfo.CurrentRegion.TwoLetterISORegionName;
        return region.Length == 2 && region.All(char.IsLetter) ? region.ToUpperInvariant() : null;
    }

    private List<RadioStation> LoadFavorites()
    {
        if (!File.Exists(_favoritesPath))
        {
            return [];
        }
        try
        {
            return JsonSerializer.Deserialize<List<RadioStation>>(File.ReadAllText(_favoritesPath)) ?? [];
        }
        catch (Exception exception) when (exception is JsonException or IOException)
        {
            _logger.LogWarning("Radio favorites could not be read: {Message}", exception.Message);
            return [];
        }
    }
}
