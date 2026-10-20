using System.ComponentModel;
using System.Windows;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using AudioStar.Desktop.ViewModels;

namespace AudioStar.Desktop.Views;

public partial class MainWindow : Window
{
    private readonly ISettingsStore _settings;

    public MainWindow(MainViewModel viewModel, ISettingsStore settings)
    {
        _settings = settings;
        InitializeComponent();
        DataContext = viewModel;
        Icon = AppIcon.CreateImageSource();
        RestorePlacement();
    }

    private void RestorePlacement()
    {
        var placement = WindowPlacementStore.Load();
        if (placement is null)
        {
            WindowStartupLocation = WindowStartupLocation.CenterScreen;
            return;
        }
        WindowStartupLocation = WindowStartupLocation.Manual;
        Left = placement.Left;
        Top = placement.Top;
        Width = placement.Width;
        Height = placement.Height;
        if (placement.Maximized)
        {
            WindowState = WindowState.Maximized;
        }
    }

    protected override void OnStateChanged(EventArgs e)
    {
        base.OnStateChanged(e);
        if (WindowState == WindowState.Minimized && _settings.Current.MinimizeToTray)
        {
            Hide();
        }
    }

    protected override void OnClosing(CancelEventArgs e)
    {
        base.OnClosing(e);
        if (App.IsQuitting)
        {
            return;
        }
        WindowPlacementStore.Save(this);
        e.Cancel = true;
        if (_settings.Current.MinimizeToTray)
        {
            Hide();
        }
        else
        {
            ((App)Application.Current).Quit();
        }
    }
}
