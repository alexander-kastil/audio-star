using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Server.Kestrel.Core;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

namespace AudioStar.Speakers.Events;

internal sealed class SpeakerEventListener(SpeakerEventRouter router, ILogger<SpeakerEventListener> logger) : IAsyncDisposable
{
    private const long MaxBodyBytes = 1024 * 1024;

    private WebApplication? _app;

    public bool IsListening => _app is not null;

    public async Task StartAsync(int port, CancellationToken cancellationToken)
    {
        if (_app is not null)
        {
            return;
        }
        try
        {
            var builder = WebApplication.CreateSlimBuilder();
            builder.Logging.ClearProviders();
            builder.WebHost.ConfigureKestrel(options => options.ListenAnyIP(port));
            builder.Services.Configure<KestrelServerOptions>(options => options.AddServerHeader = false);
            var app = builder.Build();
            app.Run(HandleAsync);
            await app.StartAsync(cancellationToken);
            _app = app;
            logger.LogInformation("Event listener bound to port {Port}", port);
        }
        catch (Exception ex) when (ex is IOException or InvalidOperationException or System.Net.Sockets.SocketException)
        {
            logger.LogWarning(ex, "Event listener could not bind port {Port}; speaker events are unavailable", port);
        }
    }

    public async Task StopAsync(CancellationToken cancellationToken)
    {
        var app = _app;
        _app = null;
        if (app is not null)
        {
            await app.StopAsync(cancellationToken);
            await app.DisposeAsync();
        }
    }

    public async ValueTask DisposeAsync()
    {
        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(3));
        await StopAsync(cts.Token);
    }

    private async Task HandleAsync(HttpContext context)
    {
        var request = context.Request;
        if (!string.Equals(request.Path.Value, "/Event", StringComparison.OrdinalIgnoreCase))
        {
            context.Response.StatusCode = StatusCodes.Status404NotFound;
            return;
        }
        var length = request.ContentLength ?? 0;
        if (length > MaxBodyBytes)
        {
            context.Response.StatusCode = StatusCodes.Status413PayloadTooLarge;
            return;
        }
        using var reader = new StreamReader(request.Body, Encoding.UTF8);
        var body = await reader.ReadToEndAsync(context.RequestAborted);
        var sid = request.Headers["SID"].ToString();
        foreach (var lastChange in ExtractLastChanges(body))
        {
            try
            {
                router.Dispatch(sid, lastChange);
            }
            catch (Exception ex)
            {
                logger.LogDebug(ex, "Event handler failed");
            }
        }
        context.Response.StatusCode = StatusCodes.Status200OK;
    }

    internal static IReadOnlyList<string> ExtractLastChanges(string body)
    {
        try
        {
            var document = XDocument.Parse(body);
            return [.. document.Descendants()
                .Where(e => e.Name.LocalName == "LastChange")
                .Select(e => e.HasElements ? string.Concat(e.Nodes().Select(n => n.ToString())) : e.Value)];
        }
        catch (System.Xml.XmlException)
        {
            return [];
        }
    }
}
