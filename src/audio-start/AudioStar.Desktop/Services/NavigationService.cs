namespace AudioStar.Desktop.Services;

public enum PageKey
{
    Dashboard,
    NowPlaying,
    Queue,
    MyMusic,
    HomeShare,
    Radio,
    YouTube,
    Spotify,
    SoundCloud,
    Recent,
    Presets,
    DeviceSettings,
    AppSettings
}

public interface INavigationService
{
    event EventHandler<PageKey>? NavigationRequested;
    void Navigate(PageKey key);
}

public sealed class NavigationService : INavigationService
{
    public event EventHandler<PageKey>? NavigationRequested;

    public void Navigate(PageKey key) => NavigationRequested?.Invoke(this, key);
}
