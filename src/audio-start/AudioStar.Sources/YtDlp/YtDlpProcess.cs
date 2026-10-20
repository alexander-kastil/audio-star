using System.Diagnostics;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Logging;

namespace AudioStar.Sources.YtDlp;

public sealed class YtDlpResult(JsonDocument? json, string stdErr, int exitCode) : IDisposable
{
    public JsonDocument? Json { get; } = json;
    public string StdErr { get; } = stdErr;
    public int ExitCode { get; } = exitCode;

    public JsonElement Root => Json?.RootElement ?? throw new YtDlpException(YtDlpErrors.Describe(StdErr), StdErr);

    public void Dispose() => Json?.Dispose();
}

public interface IYtDlp
{
    Task<YtDlpResult> GetJsonAsync(IReadOnlyList<string> arguments, TimeSpan timeout, CancellationToken cancellationToken = default);
}

public sealed class YtDlpProcess(ILogger<YtDlpProcess> logger) : IYtDlp
{
    private const string FallbackPath = @"C:\ProgramData\chocolatey\bin\yt-dlp.exe";
    private string? _executable;

    public async Task<YtDlpResult> GetJsonAsync(IReadOnlyList<string> arguments, TimeSpan timeout, CancellationToken cancellationToken = default)
    {
        var startInfo = new ProcessStartInfo(Locate())
        {
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            RedirectStandardInput = true,
            UseShellExecute = false,
            CreateNoWindow = true,
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8
        };
        startInfo.Environment["PYTHONIOENCODING"] = "utf-8";
        startInfo.Environment["PYTHONUTF8"] = "1";
        foreach (var argument in arguments)
        {
            startInfo.ArgumentList.Add(argument);
        }

        using var process = new Process { StartInfo = startInfo };
        process.Start();
        process.StandardInput.Close();

        using var timeoutSource = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeoutSource.CancelAfter(timeout);
        var stdOutTask = process.StandardOutput.ReadToEndAsync(timeoutSource.Token);
        var stdErrTask = process.StandardError.ReadToEndAsync(timeoutSource.Token);
        try
        {
            await process.WaitForExitAsync(timeoutSource.Token);
            await Task.WhenAll(stdOutTask, stdErrTask);
        }
        catch (OperationCanceledException)
        {
            Kill(process);
            if (cancellationToken.IsCancellationRequested)
            {
                throw;
            }
            throw new YtDlpException($"yt-dlp did not answer within {timeout.TotalSeconds:0} seconds.");
        }

        var stdOut = stdOutTask.Result.Trim();
        var stdErr = YtDlpRedaction.Redact(arguments, stdErrTask.Result);
        if (process.ExitCode != 0)
        {
            logger.LogWarning("yt-dlp exited with {ExitCode}: {StdErr}", process.ExitCode, stdErr.Trim());
        }
        JsonDocument? json = null;
        if (stdOut.Length > 0)
        {
            try
            {
                json = JsonDocument.Parse(stdOut);
            }
            catch (JsonException)
            {
                logger.LogWarning("yt-dlp output was not JSON");
            }
        }
        return new YtDlpResult(json, stdErr, process.ExitCode);
    }

    private string Locate()
    {
        if (File.Exists(YtDlpUpdater.ManagedPath))
        {
            return YtDlpUpdater.ManagedPath;
        }
        if (_executable is not null)
        {
            return _executable;
        }
        var fromPath = (Environment.GetEnvironmentVariable("PATH") ?? "")
            .Split(Path.PathSeparator, StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .Select(directory => SafeCombine(directory, "yt-dlp.exe"))
            .FirstOrDefault(path => path is not null && File.Exists(path));
        var found = fromPath ?? (File.Exists(FallbackPath) ? FallbackPath : null);
        return _executable = found ?? throw new YtDlpException("yt-dlp was not found. Install it (choco install yt-dlp) or add it to PATH.");
    }

    private static string? SafeCombine(string directory, string file)
    {
        try
        {
            return Path.Combine(directory, file);
        }
        catch (ArgumentException)
        {
            return null;
        }
    }

    private static void Kill(Process process)
    {
        try
        {
            process.Kill(entireProcessTree: true);
        }
        catch (InvalidOperationException)
        {
        }
    }
}
