using System.Buffers;
using System.Diagnostics;
using System.Globalization;
using AudioStar.Core;
using AudioStar.Library.Music;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Http.Features;
using Microsoft.Extensions.Logging;

namespace AudioStar.Library.Media;

internal sealed class StreamEndpoint(IEnumerable<IStreamResolver> resolvers, ILogger<StreamEndpoint> logger)
{
    private static readonly HttpClient Client = new(new SocketsHttpHandler { AllowAutoRedirect = true, ConnectTimeout = TimeSpan.FromSeconds(15) }) { Timeout = Timeout.InfiniteTimeSpan };

    private static readonly string[] FfmpegFallbacks = [@"C:\ProgramData\chocolatey\bin\ffmpeg.exe"];

    public static (string SourceId, string ItemId)? ParseTarget(string? rawTarget)
    {
        if (string.IsNullOrEmpty(rawTarget))
        {
            return null;
        }
        var path = rawTarget;
        var query = path.IndexOfAny(['?', '#']);
        if (query >= 0)
        {
            path = path[..query];
        }
        const string prefix = "/stream/";
        if (!path.StartsWith(prefix, StringComparison.OrdinalIgnoreCase))
        {
            return null;
        }
        var parts = path[prefix.Length..].Split('/');
        if (parts.Length != 2 || parts[0].Length == 0 || parts[1].Length == 0)
        {
            return null;
        }
        return (Uri.UnescapeDataString(parts[0]), Uri.UnescapeDataString(parts[1]));
    }

    public static string? FindFfmpeg()
    {
        var names = OperatingSystem.IsWindows() ? new[] { "ffmpeg.exe" } : ["ffmpeg"];
        foreach (var directory in (Environment.GetEnvironmentVariable("PATH") ?? "").Split(Path.PathSeparator, StringSplitOptions.RemoveEmptyEntries))
        {
            foreach (var name in names)
            {
                try
                {
                    var candidate = Path.Combine(directory.Trim('"'), name);
                    if (File.Exists(candidate))
                    {
                        return candidate;
                    }
                }
                catch (ArgumentException)
                {
                }
            }
        }
        return FfmpegFallbacks.FirstOrDefault(File.Exists);
    }

    public async Task HandleAsync(HttpContext context)
    {
        var target = ParseTarget(context.Features.Get<IHttpRequestFeature>()?.RawTarget);
        var resolver = target is null ? null : resolvers.FirstOrDefault(r => r.SourceId.Equals(target.Value.SourceId, StringComparison.OrdinalIgnoreCase));
        if (target is null || resolver is null)
        {
            context.Response.StatusCode = StatusCodes.Status404NotFound;
            return;
        }
        ResolvedStream resolved;
        try
        {
            resolved = await resolver.ResolveAsync(target.Value.ItemId, context.RequestAborted);
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            logger.LogWarning(ex, "Resolving {Source}/{Item} failed", target.Value.SourceId, target.Value.ItemId);
            context.Response.StatusCode = StatusCodes.Status502BadGateway;
            return;
        }
        if (resolved.RequiresTranscode)
        {
            await TranscodeAsync(context, resolved);
        }
        else
        {
            await ProxyAsync(context, resolved);
        }
    }

    private async Task ProxyAsync(HttpContext context, ResolvedStream resolved)
    {
        using var request = new HttpRequestMessage(HttpMethods.IsHead(context.Request.Method) ? HttpMethod.Head : HttpMethod.Get, resolved.Url);
        if (resolved.Headers is not null)
        {
            foreach (var (name, value) in resolved.Headers)
            {
                request.Headers.TryAddWithoutValidation(name, value);
            }
        }
        if (context.Request.Headers.TryGetValue("Range", out var range) && range.Count > 0)
        {
            request.Headers.TryAddWithoutValidation("Range", range.ToString());
        }
        HttpResponseMessage upstream;
        try
        {
            upstream = await Client.SendAsync(request, HttpCompletionOption.ResponseHeadersRead, context.RequestAborted);
        }
        catch (HttpRequestException ex)
        {
            logger.LogWarning(ex, "Upstream request to {Url} failed", resolved.Url.Host);
            context.Response.StatusCode = StatusCodes.Status502BadGateway;
            return;
        }
        using (upstream)
        {
            var response = context.Response;
            response.StatusCode = (int)upstream.StatusCode;
            response.ContentType = upstream.Content.Headers.ContentType?.ToString() ?? resolved.ContentType;
            if (upstream.Content.Headers.ContentLength is { } length)
            {
                response.ContentLength = length;
            }
            else if (resolved.Length is { } known && (int)upstream.StatusCode == StatusCodes.Status200OK)
            {
                response.ContentLength = known;
            }
            if (upstream.Content.Headers.ContentRange is { } contentRange)
            {
                response.Headers.ContentRange = contentRange.ToString();
            }
            response.Headers.AcceptRanges = "bytes";
            if (HttpMethods.IsHead(context.Request.Method))
            {
                return;
            }
            await using var body = await upstream.Content.ReadAsStreamAsync(context.RequestAborted);
            try
            {
                await body.CopyToAsync(response.Body, 81920, context.RequestAborted);
            }
            catch (OperationCanceledException)
            {
            }
        }
    }

    private async Task TranscodeAsync(HttpContext context, ResolvedStream resolved)
    {
        if (resolved.Duration is { } duration && duration > TimeSpan.Zero)
        {
            await ServeWavAsync(context, resolved, duration);
            return;
        }
        context.Response.ContentType = "audio/flac";
        if (HttpMethods.IsHead(context.Request.Method))
        {
            return;
        }
        if (FindFfmpeg() is not { } ffmpeg)
        {
            logger.LogWarning("ffmpeg was not found on PATH or in the Chocolatey bin folder");
            context.Response.StatusCode = StatusCodes.Status501NotImplemented;
            return;
        }
        using var process = Process.Start(FfmpegInfo(ffmpeg, resolved, null, ["-f", "flac", "pipe:1"]));
        if (process is null)
        {
            context.Response.StatusCode = StatusCodes.Status500InternalServerError;
            return;
        }
        using var registration = context.RequestAborted.Register(() => Kill(process));
        _ = process.StandardError.ReadToEndAsync();
        try
        {
            await process.StandardOutput.BaseStream.CopyToAsync(context.Response.Body, 65536, context.RequestAborted);
        }
        catch (Exception ex) when (ex is OperationCanceledException or IOException)
        {
        }
        finally
        {
            Kill(process);
        }
    }

    private async Task ServeWavAsync(HttpContext context, ResolvedStream resolved, TimeSpan duration)
    {
        var response = context.Response;
        var dataLength = WavStream.DataLength(duration);
        var total = WavStream.HeaderLength + dataLength;
        var outcome = RangeParser.Parse(context.Request.Headers.Range.ToString(), total, out var start, out var end);
        if (outcome == RangeOutcome.NotSatisfiable)
        {
            response.StatusCode = StatusCodes.Status416RangeNotSatisfiable;
            response.Headers.ContentRange = $"bytes */{total}";
            return;
        }
        var isHead = HttpMethods.IsHead(context.Request.Method);
        var ffmpeg = FindFfmpeg();
        if (ffmpeg is null && !isHead && end >= WavStream.HeaderLength)
        {
            logger.LogWarning("ffmpeg was not found on PATH or in the Chocolatey bin folder");
            response.StatusCode = StatusCodes.Status501NotImplemented;
            return;
        }
        response.ContentType = "audio/wav";
        response.Headers.AcceptRanges = "bytes";
        response.ContentLength = end - start + 1;
        if (outcome == RangeOutcome.Partial)
        {
            response.StatusCode = StatusCodes.Status206PartialContent;
            response.Headers.ContentRange = $"bytes {start}-{end}/{total}";
        }
        if (isHead)
        {
            return;
        }
        try
        {
            if (start < WavStream.HeaderLength)
            {
                var header = WavStream.Header(dataLength);
                var headerEnd = Math.Min(end, WavStream.HeaderLength - 1);
                await response.Body.WriteAsync(header.AsMemory((int)start, (int)(headerEnd - start + 1)), context.RequestAborted);
            }
            if (end >= WavStream.HeaderLength)
            {
                await StreamPcmAsync(context, resolved, ffmpeg!, start, end - Math.Max(start, WavStream.HeaderLength) + 1);
            }
        }
        catch (Exception ex) when (ex is OperationCanceledException or IOException)
        {
        }
    }

    private static async Task StreamPcmAsync(HttpContext context, ResolvedStream resolved, string ffmpeg, long rangeStart, long dataBytes)
    {
        var (skip, startSeconds) = WavStream.SeekFor(rangeStart);
        var output = new[] { "-f", "s16le", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", "pipe:1" };
        using var process = Process.Start(FfmpegInfo(ffmpeg, resolved, startSeconds, output))
            ?? throw new IOException("ffmpeg could not be started.");
        using var registration = context.RequestAborted.Register(() => Kill(process));
        _ = process.StandardError.ReadToEndAsync();
        var buffer = ArrayPool<byte>.Shared.Rent(65536);
        try
        {
            var input = process.StandardOutput.BaseStream;
            var remaining = dataBytes;
            var toSkip = skip;
            while (remaining > 0)
            {
                var read = await input.ReadAsync(buffer.AsMemory(0, (int)Math.Min(buffer.Length, remaining + toSkip)), context.RequestAborted);
                if (read == 0)
                {
                    break;
                }
                var offset = (int)Math.Min(toSkip, read);
                toSkip -= offset;
                var count = read - offset;
                if (count > 0)
                {
                    await context.Response.Body.WriteAsync(buffer.AsMemory(offset, count), context.RequestAborted);
                    remaining -= count;
                }
            }
            Array.Clear(buffer);
            while (remaining > 0)
            {
                var count = (int)Math.Min(buffer.Length, remaining);
                await context.Response.Body.WriteAsync(buffer.AsMemory(0, count), context.RequestAborted);
                remaining -= count;
            }
        }
        finally
        {
            ArrayPool<byte>.Shared.Return(buffer);
            Kill(process);
        }
    }

    private static ProcessStartInfo FfmpegInfo(string ffmpeg, ResolvedStream resolved, double? startSeconds, IEnumerable<string> output)
    {
        var info = new ProcessStartInfo(ffmpeg)
        {
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            RedirectStandardInput = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };
        foreach (var argument in new[] { "-nostdin", "-loglevel", "error" })
        {
            info.ArgumentList.Add(argument);
        }
        if (resolved.Headers is { Count: > 0 })
        {
            info.ArgumentList.Add("-headers");
            info.ArgumentList.Add(string.Concat(resolved.Headers.Select(h => $"{h.Key}: {h.Value}\r\n")));
        }
        if (startSeconds is > 0)
        {
            info.ArgumentList.Add("-ss");
            info.ArgumentList.Add(startSeconds.Value.ToString("0.######", CultureInfo.InvariantCulture));
        }
        foreach (var argument in new[] { "-i", resolved.Url.AbsoluteUri, "-vn", "-map_metadata", "-1" }.Concat(output))
        {
            info.ArgumentList.Add(argument);
        }
        return info;
    }

    private static void Kill(Process process)
    {
        try
        {
            if (!process.HasExited)
            {
                process.Kill(entireProcessTree: true);
            }
        }
        catch (Exception ex) when (ex is InvalidOperationException or System.ComponentModel.Win32Exception)
        {
        }
    }
}
