using System.Text.Json;

namespace AudioStar.Core;

public sealed class AudioStarSettings
{
    public List<string> MusicFolders { get; set; } = [];
    public int MediaServerPort { get; set; } = 22545;
    public int EventListenerPort { get; set; } = 22534;
    public bool DlnaServerEnabled { get; set; }
    public string DlnaServerName { get; set; } = "Audio Star";
    public bool PreventSleep { get; set; }
    public bool MinimizeToTray { get; set; } = true;
    public string? LastSpeakerId { get; set; }
    public List<string> ManualSpeakerIps { get; set; } = [];
    public string YouTubeCookieSource { get; set; } = "";
    public List<string> YouTubePlaylistUrls { get; set; } = [];
    public string? SoundCloudProfileUrl { get; set; }
    public List<string> SoundCloudPlaylistUrls { get; set; } = [];
    public string? SpotifyClientId { get; set; }
    public int SpotifyRedirectPort { get; set; } = 22547;
    public string RadioCountryCode { get; set; } = "";
}

public interface ISettingsStore
{
    AudioStarSettings Current { get; }
    event EventHandler? Changed;
    Task SaveAsync(CancellationToken cancellationToken = default);
}

public static class AppPaths
{
    public static string DataDirectory { get; } = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "AudioStar");
    public static string CacheDirectory { get; } = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "AudioStar");
    public static string SettingsFile => Path.Combine(DataDirectory, "settings.json");
    public static string DatabaseFile => Path.Combine(DataDirectory, "audiostar.db");
    public static string LogDirectory => Path.Combine(CacheDirectory, "logs");
    public static string PlaylistCacheDirectory => Path.Combine(CacheDirectory, "playlists");
}

public sealed class JsonSettingsStore : ISettingsStore
{
    private static readonly JsonSerializerOptions Options = new() { WriteIndented = true };
    private readonly string _path;
    private readonly SemaphoreSlim _gate = new(1, 1);

    public JsonSettingsStore() : this(AppPaths.SettingsFile) { }

    public JsonSettingsStore(string path)
    {
        _path = path;
        Current = Load(path);
    }

    public AudioStarSettings Current { get; }

    public event EventHandler? Changed;

    public async Task SaveAsync(CancellationToken cancellationToken = default)
    {
        await _gate.WaitAsync(cancellationToken);
        try
        {
            Directory.CreateDirectory(Path.GetDirectoryName(_path)!);
            var temp = _path + ".tmp";
            await File.WriteAllTextAsync(temp, JsonSerializer.Serialize(Current, Options), cancellationToken);
            File.Move(temp, _path, overwrite: true);
        }
        finally
        {
            _gate.Release();
        }
        Changed?.Invoke(this, EventArgs.Empty);
    }

    private static AudioStarSettings Load(string path)
    {
        if (!File.Exists(path))
        {
            return new AudioStarSettings();
        }
        try
        {
            return JsonSerializer.Deserialize<AudioStarSettings>(File.ReadAllText(path), Options) ?? new AudioStarSettings();
        }
        catch (JsonException)
        {
            return new AudioStarSettings();
        }
    }
}
