using System.Windows;
using System.Windows.Threading;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using AudioStar.Desktop.ViewModels;
using AudioStar.Desktop.Views;
using AudioStar.Devices;
using AudioStar.Library;
using AudioStar.Sources;
using AudioStar.Speakers;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace AudioStar.Desktop;

public partial class App : Application
{
    private IHost? _host;
    private SingleInstance? _singleInstance;
    private TrayService? _tray;
    private SleepGuard? _sleepGuard;
    private ThemeService? _theme;
    private MainWindow? _window;
    private ILogger<App>? _logger;
    private IToastService? _toast;
    private bool _hostStarted;

    public static bool IsQuitting { get; private set; }

    protected override async void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        if (Environment.GetEnvironmentVariable("AUDIOSTAR_HARDWARE_RENDER") != "1")
        {
            System.Windows.Media.RenderOptions.ProcessRenderMode = System.Windows.Interop.RenderMode.SoftwareOnly;
        }
        _singleInstance = new SingleInstance();
        if (!_singleInstance.TryAcquire())
        {
            SingleInstance.SignalExisting();
            Shutdown();
            return;
        }

        DispatcherUnhandledException += OnDispatcherUnhandledException;
        TaskScheduler.UnobservedTaskException += OnUnobservedTaskException;
        AppDomain.CurrentDomain.UnhandledException += OnDomainUnhandledException;

        _theme = new ThemeService();
        _theme.Start();

        _host = BuildHost(e.Args);
        _logger = _host.Services.GetRequiredService<ILogger<App>>();
        _toast = _host.Services.GetRequiredService<IToastService>();
        _sleepGuard = _host.Services.GetRequiredService<SleepGuard>();
        _sleepGuard.Start();
        var navigation = _host.Services.GetRequiredService<INavigationService>();
        _tray = new TrayService(
            ShowMainWindow,
            () =>
            {
                ShowMainWindow();
                navigation.Navigate(PageKey.AppSettings);
            },
            Quit,
            _host.Services.GetRequiredService<ICurrentSpeaker>(),
            _host.Services.GetRequiredService<IUiDispatcher>(),
            _toast);
        _singleInstance.ListenForActivation(() => Dispatcher.BeginInvoke(ShowMainWindow));

        try
        {
            _window = _host.Services.GetRequiredService<MainWindow>();
            MainWindow = _window;
            if (!e.Args.Contains(Autostart.Argument))
            {
                _window.Show();
            }
            _host.Services.GetRequiredService<MainViewModel>().Start();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Could not open the main window");
            MessageBox.Show(ex.Message, "Audio Star", MessageBoxButton.OK, MessageBoxImage.Error);
            Quit();
            return;
        }

        try
        {
            await _host.StartAsync();
            _hostStarted = true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "A background service failed to start");
            _toast.ShowError($"A background service failed to start: {ex.Message}");
        }
    }

    private static IHost BuildHost(string[] args)
    {
        var builder = Host.CreateApplicationBuilder(args);
        builder.Logging.ClearProviders();
        builder.Logging.AddDebug();
        builder.Logging.AddProvider(new FileLoggerProvider());
        builder.Logging.SetMinimumLevel(LogLevel.Information);
        builder.Logging.AddFilter("System.Net.Http.HttpClient", LogLevel.Warning);
        builder.Logging.AddFilter("Microsoft.Hosting.Lifetime", LogLevel.Warning);
        builder.Logging.AddFilter("Microsoft.AspNetCore", LogLevel.Warning);

        var services = builder.Services;
        services.AddAudioStarCore();
        services.AddAudioStarSpeakers();
        services.AddAudioStarDevices();
        services.AddAudioStarLibrary();
        services.AddAudioStarSources();

        services.AddSingleton<IUiDispatcher, UiDispatcher>();
        services.AddSingleton<IToastService, ToastService>();
        services.AddSingleton<INavigationService, NavigationService>();
        services.AddSingleton<ICurrentSpeaker, CurrentSpeakerService>();
        services.AddSingleton<IDialogService, DialogService>();
        services.AddSingleton<IWebSignIn, WebSignInService>();
        services.AddSingleton<SleepGuard>();
        services.AddSingleton<IPageFactory, PageFactory>();
        services.AddSingleton<PlayerViewModel>();
        services.AddSingleton<MainViewModel>();
        services.AddSingleton<MainWindow>();

        services.AddTransient<DashboardViewModel>();
        services.AddTransient<NowPlayingViewModel>();
        services.AddTransient<QueueViewModel>();
        services.AddTransient<MyMusicViewModel>();
        services.AddTransient<HomeShareViewModel>();
        services.AddTransient<RadioViewModel>();
        services.AddTransient<RecentViewModel>();
        services.AddTransient<PresetsViewModel>();
        services.AddTransient<DeviceSettingsViewModel>();
        services.AddTransient<AppSettingsViewModel>();
        services.AddTransient<GroupEditorViewModel>();
        return builder.Build();
    }

    private void ShowMainWindow()
    {
        if (_window is null)
        {
            return;
        }
        if (!_window.IsVisible)
        {
            _window.Show();
        }
        if (_window.WindowState == WindowState.Minimized)
        {
            _window.WindowState = WindowState.Normal;
        }
        _window.Activate();
        _window.Topmost = true;
        _window.Topmost = false;
        _window.Focus();
    }

    public async void Quit()
    {
        if (IsQuitting)
        {
            return;
        }
        IsQuitting = true;
        if (_window is not null)
        {
            WindowPlacementStore.Save(_window);
        }
        _tray?.Dispose();
        _tray = null;
        try
        {
            if (_host is not null && _hostStarted)
            {
                using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(8));
                await _host.StopAsync(timeout.Token);
            }
        }
        catch (Exception ex)
        {
            _logger?.LogError(ex, "A background service failed to stop");
        }
        Shutdown();
    }

    protected override void OnSessionEnding(SessionEndingCancelEventArgs e)
    {
        base.OnSessionEnding(e);
        Quit();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        _tray?.Dispose();
        _sleepGuard?.Dispose();
        _theme?.Dispose();
        _singleInstance?.Dispose();
        _host?.Dispose();
        base.OnExit(e);
    }

    private void OnDispatcherUnhandledException(object sender, DispatcherUnhandledExceptionEventArgs e)
    {
        e.Handled = true;
        Report(e.Exception);
    }

    private void OnUnobservedTaskException(object? sender, UnobservedTaskExceptionEventArgs e)
    {
        e.SetObserved();
        Report(e.Exception);
    }

    private void OnDomainUnhandledException(object sender, UnhandledExceptionEventArgs e)
    {
        if (e.ExceptionObject is Exception exception)
        {
            _logger?.LogCritical(exception, "Unhandled exception");
            _toast?.ShowError(exception);
        }
    }

    private void Report(Exception exception)
    {
        var root = exception is AggregateException { InnerExceptions.Count: > 0 } aggregate ? aggregate.InnerExceptions[0] : exception;
        if (root is OperationCanceledException)
        {
            return;
        }
        _logger?.LogError(exception, "Unhandled exception");
        _toast?.ShowError(root);
    }
}
