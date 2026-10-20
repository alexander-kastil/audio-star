using System.Text.Json;
using System.Windows;
using AudioStar.Core;

namespace AudioStar.Desktop.Services;

public sealed record WindowPlacement(double Left, double Top, double Width, double Height, bool Maximized);

public static class WindowPlacementStore
{
    private static string FilePath => Path.Combine(AppPaths.DataDirectory, "window.json");

    public static WindowPlacement? Load()
    {
        try
        {
            if (!File.Exists(FilePath))
            {
                return null;
            }
            var placement = JsonSerializer.Deserialize<WindowPlacement>(File.ReadAllText(FilePath));
            if (placement is null || placement.Width < 400 || placement.Height < 300)
            {
                return null;
            }
            var visible = new Rect(placement.Left, placement.Top, placement.Width, placement.Height);
            var screen = new Rect(SystemParameters.VirtualScreenLeft, SystemParameters.VirtualScreenTop, SystemParameters.VirtualScreenWidth, SystemParameters.VirtualScreenHeight);
            return screen.IntersectsWith(visible) ? placement : null;
        }
        catch (Exception ex) when (ex is IOException or JsonException or UnauthorizedAccessException)
        {
            return null;
        }
    }

    public static void Save(Window window)
    {
        try
        {
            var bounds = window.WindowState == WindowState.Normal
                ? new Rect(window.Left, window.Top, window.Width, window.Height)
                : window.RestoreBounds;
            if (bounds.IsEmpty)
            {
                return;
            }
            Directory.CreateDirectory(AppPaths.DataDirectory);
            var placement = new WindowPlacement(bounds.Left, bounds.Top, bounds.Width, bounds.Height, window.WindowState == WindowState.Maximized);
            File.WriteAllText(FilePath, JsonSerializer.Serialize(placement));
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
        {
        }
    }
}
