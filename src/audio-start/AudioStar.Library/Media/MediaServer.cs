using System.Buffers;
using AudioStar.Core;
using AudioStar.Library.Data;
using AudioStar.Library.Dlna;
using AudioStar.Library.Music;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace AudioStar.Library.Media;

internal sealed class MediaServer(
    ISettingsStore settings,
    TrackStore store,
    CoverService covers,
    StreamEndpoint streams,
    DlnaHttp dlna,
    ILoggerFactory loggerFactory,
    ILogger<MediaServer> logger) : IMediaServer
{
    private static readonly TimeSpan AddressCacheTime = TimeSpan.FromSeconds(30);

    private readonly SemaphoreSlim _gate = new(1, 1);
    private WebApplication? _app;
    private int _boundPort;
    private Uri? _cachedBase;
    private DateTime _cachedAt;

    public Uri BaseUri
    {
        get
        {
            var port = _boundPort > 0 ? _boundPort : settings.Current.MediaServerPort;
            if (_cachedBase is null || _cachedBase.Port != port || DateTime.UtcNow - _cachedAt > AddressCacheTime)
            {
                _cachedBase = new Uri($"http://{NetworkInfo.PrimaryLocalAddress()}:{port}/");
                _cachedAt = DateTime.UtcNow;
            }
            return _cachedBase;
        }
    }

    public int BoundPort => _boundPort;

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        await _gate.WaitAsync(cancellationToken);
        try
        {
            if (_app is not null)
            {
                return;
            }
            var port = settings.Current.MediaServerPort;
            var builder = WebApplication.CreateSlimBuilder();
            builder.WebHost.UseUrls($"http://0.0.0.0:{port}");
            builder.Services.AddSingleton(loggerFactory);
            var app = builder.Build();
            app.MapGet("/", () => "Audio Star Media Service");
            app.MapMethods("/media/music/{hex}", ["GET", "HEAD"], (HttpContext context, string hex) => ServeMusicAsync(context, hex));
            app.MapMethods("/media/cover/{hex}", ["GET", "HEAD"], (HttpContext context, string hex) => ServeCoverAsync(context, hex));
            app.MapMethods("/stream/{sourceId}/{**itemId}", ["GET", "HEAD"], (HttpContext context) => streams.HandleAsync(context));
            dlna.Map(app);
            await app.StartAsync(cancellationToken);
            _app = app;
            _boundPort = port;
            _cachedBase = null;
            logger.LogInformation("Media server listening on port {Port}", port);
        }
        finally
        {
            _gate.Release();
        }
    }

    public async Task StopAsync(CancellationToken cancellationToken)
    {
        await _gate.WaitAsync(cancellationToken);
        try
        {
            if (_app is null)
            {
                return;
            }
            await _app.StopAsync(cancellationToken);
            await _app.DisposeAsync();
            _app = null;
            _boundPort = 0;
            _cachedBase = null;
        }
        finally
        {
            _gate.Release();
        }
    }

    public Uri GetFileUri(string absolutePath) => new(BaseUri, "media/music/" + PathCodec.Encode(absolutePath));

    public Uri GetCoverUri(string absolutePath) => new(BaseUri, "media/cover/" + PathCodec.Encode(absolutePath));

    public Uri GetStreamUri(string sourceId, string itemId) => new(BaseUri, $"stream/{Uri.EscapeDataString(sourceId)}/{Uri.EscapeDataString(itemId)}");

    private async Task<string?> ResolveAccessiblePathAsync(string hex, CancellationToken cancellationToken)
    {
        if (!PathCodec.TryDecode(hex, out var decoded) || !Path.IsPathFullyQualified(decoded) || !AudioFormats.IsSupported(decoded))
        {
            return null;
        }
        var full = Path.GetFullPath(decoded);
        if (!File.Exists(full))
        {
            return null;
        }
        if (settings.Current.MusicFolders.Any(folder => PathCodec.IsUnder(folder, full)))
        {
            return full;
        }
        return await store.IsKnownPathAsync(full, cancellationToken) ? full : null;
    }

    private async Task ServeMusicAsync(HttpContext context, string hex)
    {
        var path = await ResolveAccessiblePathAsync(hex, context.RequestAborted);
        if (path is null)
        {
            context.Response.StatusCode = StatusCodes.Status404NotFound;
            return;
        }
        var length = new FileInfo(path).Length;
        var response = context.Response;
        response.ContentType = AudioFormats.ContentTypeFor(path);
        response.Headers.AcceptRanges = "bytes";
        var outcome = RangeParser.Parse(context.Request.Headers.Range.ToString(), length, out var start, out var end);
        if (outcome == RangeOutcome.NotSatisfiable)
        {
            response.StatusCode = StatusCodes.Status416RangeNotSatisfiable;
            response.Headers.ContentRange = $"bytes */{length}";
            return;
        }
        var count = length == 0 ? 0 : end - start + 1;
        response.ContentLength = count;
        if (outcome == RangeOutcome.Partial)
        {
            response.StatusCode = StatusCodes.Status206PartialContent;
            response.Headers.ContentRange = $"bytes {start}-{end}/{length}";
        }
        if (HttpMethods.IsHead(context.Request.Method) || count == 0)
        {
            return;
        }
        await using var file = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete, 81920, useAsync: true);
        file.Seek(start, SeekOrigin.Begin);
        var buffer = ArrayPool<byte>.Shared.Rent(81920);
        try
        {
            var remaining = count;
            while (remaining > 0)
            {
                var read = await file.ReadAsync(buffer.AsMemory(0, (int)Math.Min(buffer.Length, remaining)), context.RequestAborted);
                if (read == 0)
                {
                    break;
                }
                await response.Body.WriteAsync(buffer.AsMemory(0, read), context.RequestAborted);
                remaining -= read;
            }
        }
        catch (OperationCanceledException)
        {
        }
        finally
        {
            ArrayPool<byte>.Shared.Return(buffer);
        }
    }

    private async Task ServeCoverAsync(HttpContext context, string hex)
    {
        var path = await ResolveAccessiblePathAsync(hex, context.RequestAborted);
        var cover = path is null ? null : await covers.GetAsync(path, context.RequestAborted);
        if (cover is null)
        {
            context.Response.StatusCode = StatusCodes.Status404NotFound;
            return;
        }
        var length = new FileInfo(cover.Path).Length;
        context.Response.ContentType = cover.ContentType;
        context.Response.ContentLength = length;
        context.Response.Headers.CacheControl = "public, max-age=86400";
        if (!HttpMethods.IsHead(context.Request.Method))
        {
            await context.Response.SendFileAsync(cover.Path, context.RequestAborted);
        }
    }
}
