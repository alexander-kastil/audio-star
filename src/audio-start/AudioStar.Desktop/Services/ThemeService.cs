using System.Windows;
using System.Windows.Media;
using Microsoft.Win32;

namespace AudioStar.Desktop.Services;

public sealed class ThemeService : IDisposable
{
    public void Start()
    {
        Apply();
        SystemEvents.UserPreferenceChanged += OnPreferenceChanged;
    }

    private void OnPreferenceChanged(object sender, UserPreferenceChangedEventArgs e)
    {
        if (e.Category is UserPreferenceCategory.General or UserPreferenceCategory.Color)
        {
            Application.Current.Dispatcher.BeginInvoke(Apply);
        }
    }

    public static bool IsLight()
    {
        using var key = Registry.CurrentUser.OpenSubKey(@"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize");
        return key?.GetValue("AppsUseLightTheme") is not int value || value != 0;
    }

    private static void Apply()
    {
        var light = IsLight();
        var accent = SystemParameters.WindowGlassColor;
        var resources = Application.Current.Resources;
        Set(resources, "AppBackgroundBrush", light ? "#F3F3F3" : "#1F1F1F");
        Set(resources, "AppSidebarBrush", light ? "#EBEBEB" : "#181818");
        Set(resources, "AppCardBrush", light ? "#FFFFFF" : "#2B2B2B");
        Set(resources, "AppCardHoverBrush", light ? "#F7F7F7" : "#333333");
        Set(resources, "AppStrokeBrush", light ? "#E0E0E0" : "#3C3C3C");
        Set(resources, "AppHoverBrush", light ? "#14000000" : "#1FFFFFFF");
        Set(resources, "AppSelectedBrush", light ? "#22000000" : "#2EFFFFFF");
        Set(resources, "AppTextBrush", light ? "#1A1A1A" : "#FFFFFF");
        Set(resources, "AppSubtleTextBrush", light ? "#5F5F5F" : "#C2C2C2");
        Set(resources, "AppPlaceholderBrush", light ? "#DADADA" : "#3A3A3A");
        Set(resources, "AppToastBrush", light ? "#2B2B2B" : "#3A3A3A");
        Set(resources, "AppErrorBrush", "#C42B1C");
        Set(resources, "AppSuccessBrush", light ? "#0F7B0F" : "#6CCB5F");
        var accentBrush = new SolidColorBrush(Color.FromRgb(accent.R, accent.G, accent.B));
        accentBrush.Freeze();
        resources["AppAccentBrush"] = accentBrush;
        var accentSoft = new SolidColorBrush(Color.FromArgb(light ? (byte)0x26 : (byte)0x40, accent.R, accent.G, accent.B));
        accentSoft.Freeze();
        resources["AppAccentSoftBrush"] = accentSoft;
        var accentHover = new SolidColorBrush(Blend(accent, light ? Colors.Black : Colors.White, 0.12));
        accentHover.Freeze();
        resources["AppAccentHoverBrush"] = accentHover;
        var accentText = new SolidColorBrush(Luminance(accent) > 0.6 ? Colors.Black : Colors.White);
        accentText.Freeze();
        resources["AppAccentTextBrush"] = accentText;
    }

    private static double Luminance(Color color) => (0.299 * color.R + 0.587 * color.G + 0.114 * color.B) / 255;

    private static Color Blend(Color from, Color to, double amount) => Color.FromRgb(
        (byte)(from.R + (to.R - from.R) * amount),
        (byte)(from.G + (to.G - from.G) * amount),
        (byte)(from.B + (to.B - from.B) * amount));

    private static void Set(ResourceDictionary resources, string key, string color)
    {
        var brush = new SolidColorBrush((Color)ColorConverter.ConvertFromString(color));
        brush.Freeze();
        resources[key] = brush;
    }

    public void Dispose() => SystemEvents.UserPreferenceChanged -= OnPreferenceChanged;
}
