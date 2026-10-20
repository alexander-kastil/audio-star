using System.Diagnostics;
using AudioStar.Core;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace AudioStar.Sources.YtDlp;

public sealed class YtDlpUpdater(ILogger<YtDlpUpdater> logger) : BackgroundService
{
    private const string DownloadUrl = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe";
    private static readonly TimeSpan UpdateInterval = TimeSpan.FromDays(2);

    public static string ManagedPath { get; } = Path.Combine(AppPaths.CacheDirectory, "tools", "yt-dlp.exe");

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                if (!File.Exists(ManagedPath))
                {
                    await DownloadAsync(stoppingToken);
                }
                else if (DateTime.UtcNow - File.GetLastWriteTimeUtc(ManagedPath) > UpdateInterval)
                {
                    await SelfUpdateAsync(stoppingToken);
                }
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                logger.LogWarning("yt-dlp update failed: {Message}", ex.Message);
            }
            try
            {
                await Task.Delay(TimeSpan.FromHours(6), stoppingToken);
            }
            catch (OperationCanceledException)
            {
                return;
            }
        }
    }

    private async Task DownloadAsync(CancellationToken cancellationToken)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(ManagedPath)!);
        var temp = ManagedPath + ".download";
        using (var http = new HttpClient { Timeout = TimeSpan.FromMinutes(5) })
        {
            http.DefaultRequestHeaders.UserAgent.ParseAdd("AudioStar/0.1");
            await using var source = await http.GetStreamAsync(DownloadUrl, cancellationToken);
            await using var target = File.Create(temp);
            await source.CopyToAsync(target, cancellationToken);
        }
        File.Move(temp, ManagedPath, overwrite: true);
        logger.LogInformation("Downloaded yt-dlp to {Path}", ManagedPath);
    }

    private async Task SelfUpdateAsync(CancellationToken cancellationToken)
    {
        var startInfo = new ProcessStartInfo(ManagedPath, "-U")
        {
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true
        };
        using var process = Process.Start(startInfo)!;
        var output = await process.StandardOutput.ReadToEndAsync(cancellationToken);
        await process.WaitForExitAsync(cancellationToken);
        File.SetLastWriteTimeUtc(ManagedPath, DateTime.UtcNow);
        logger.LogInformation("yt-dlp self-update: {Output}", output.Trim());
    }
}
