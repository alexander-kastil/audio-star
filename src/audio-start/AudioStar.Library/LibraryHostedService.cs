using AudioStar.Core;
using AudioStar.Library.Media;
using AudioStar.Library.Music;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace AudioStar.Library;

internal sealed class LibraryHostedService(
    MusicLibrary library,
    IMediaServer mediaServer,
    IDlnaServer dlnaServer,
    IHomeShareBrowser homeShare,
    ISettingsStore settings,
    ILogger<LibraryHostedService> logger) : IHostedService
{
    private readonly SemaphoreSlim _gate = new(1, 1);
    private int _mediaPort;

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        await _gate.WaitAsync(cancellationToken);
        try
        {
            _mediaPort = settings.Current.MediaServerPort;
            await Safe("music library", () => library.StartAsync(cancellationToken));
            await Safe("media server", () => mediaServer.StartAsync(cancellationToken));
            await Safe("Home Share discovery", () => homeShare.StartAsync(cancellationToken));
            await ApplyDlnaAsync(cancellationToken);
            settings.Changed += OnSettingsChanged;
        }
        finally
        {
            _gate.Release();
        }
    }

    public async Task StopAsync(CancellationToken cancellationToken)
    {
        settings.Changed -= OnSettingsChanged;
        await Safe("DLNA server", () => dlnaServer.StopAsync(cancellationToken));
        await Safe("media server", () => mediaServer.StopAsync(cancellationToken));
        await library.StopAsync();
        if (homeShare is IAsyncDisposable disposable)
        {
            await disposable.DisposeAsync();
        }
    }

    private void OnSettingsChanged(object? sender, EventArgs e) => _ = Task.Run(ReconcileAsync);

    private async Task ReconcileAsync()
    {
        await _gate.WaitAsync();
        try
        {
            if (settings.Current.MediaServerPort != _mediaPort)
            {
                _mediaPort = settings.Current.MediaServerPort;
                await Safe("DLNA server", () => dlnaServer.StopAsync(CancellationToken.None));
                await Safe("media server", () => mediaServer.StopAsync(CancellationToken.None));
                await Safe("media server", () => mediaServer.StartAsync(CancellationToken.None));
            }
            await ApplyDlnaAsync(CancellationToken.None);
        }
        finally
        {
            _gate.Release();
        }
    }

    private Task ApplyDlnaAsync(CancellationToken cancellationToken)
    {
        if (settings.Current.DlnaServerEnabled == dlnaServer.IsRunning)
        {
            return Task.CompletedTask;
        }
        return Safe("DLNA server", () => settings.Current.DlnaServerEnabled ? dlnaServer.StartAsync(cancellationToken) : dlnaServer.StopAsync(cancellationToken));
    }

    private async Task Safe(string what, Func<Task> action)
    {
        try
        {
            await action();
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            logger.LogError(ex, "Starting or stopping the {Component} failed", what);
        }
    }
}
