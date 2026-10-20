using System.Net.Http.Headers;
using System.Text.Json;
using AudioStar.Core;
using Microsoft.Extensions.Logging;

namespace AudioStar.Sources.Radio;

public sealed class RadioBrowserClient(ILogger<RadioBrowserClient> logger) : IDisposable
{
    private const string ServersUrl = "https://all.api.radio-browser.info/json/servers";

    private readonly HttpClient _http = CreateHttp();
    private string[] _servers = [];
    private int _current;

    public Task<IReadOnlyList<RadioStation>> TopByCountryAsync(string countryCode, int limit, CancellationToken cancellationToken) =>
        StationsAsync($"stations/search?countrycode={Uri.EscapeDataString(countryCode)}&order=clickcount&reverse=true&hidebroken=true&limit={limit}", cancellationToken);

    public Task<IReadOnlyList<RadioStation>> TopClickedAsync(int limit, CancellationToken cancellationToken) =>
        StationsAsync($"stations/search?order=clickcount&reverse=true&hidebroken=true&limit={limit}", cancellationToken);

    public Task<IReadOnlyList<RadioStation>> ByTagAsync(string tag, int offset, int limit, CancellationToken cancellationToken) =>
        StationsAsync($"stations/search?tag={Uri.EscapeDataString(tag)}&tagExact=true&order=votes&reverse=true&hidebroken=true&offset={offset}&limit={limit}", cancellationToken);

    public Task<IReadOnlyList<RadioStation>> SearchAsync(string query, int offset, int limit, CancellationToken cancellationToken) =>
        StationsAsync($"stations/search?name={Uri.EscapeDataString(query)}&order=clickcount&reverse=true&hidebroken=true&offset={offset}&limit={limit}", cancellationToken);

    public async Task RegisterClickAsync(string stationId, CancellationToken cancellationToken)
    {
        try
        {
            using var _ = await GetAsync($"url/{Uri.EscapeDataString(stationId)}", cancellationToken);
        }
        catch (Exception exception) when (exception is HttpRequestException or JsonException or TaskCanceledException)
        {
            logger.LogDebug("Radio click was not registered: {Message}", exception.Message);
        }
    }

    public void Dispose() => _http.Dispose();

    private async Task<IReadOnlyList<RadioStation>> StationsAsync(string path, CancellationToken cancellationToken)
    {
        using var json = await GetAsync(path, cancellationToken);
        return RadioMapper.MapStations(json.RootElement);
    }

    private async Task<JsonDocument> GetAsync(string path, CancellationToken cancellationToken)
    {
        var servers = await ServersAsync(cancellationToken);
        Exception? last = null;
        for (var attempt = 0; attempt < Math.Min(3, servers.Length); attempt++)
        {
            var server = servers[(_current + attempt) % servers.Length];
            try
            {
                using var response = await _http.GetAsync($"https://{server}/json/{path}", cancellationToken);
                response.EnsureSuccessStatusCode();
                _current = (_current + attempt) % servers.Length;
                return await JsonDocument.ParseAsync(await response.Content.ReadAsStreamAsync(cancellationToken), cancellationToken: cancellationToken);
            }
            catch (Exception exception) when (exception is HttpRequestException or TaskCanceledException && !cancellationToken.IsCancellationRequested)
            {
                logger.LogWarning("radio-browser server {Server} failed: {Message}", server, exception.Message);
                last = exception;
            }
        }
        throw new HttpRequestException("The radio directory (radio-browser.info) is not reachable.", last);
    }

    private async Task<string[]> ServersAsync(CancellationToken cancellationToken)
    {
        if (_servers.Length > 0)
        {
            return _servers;
        }
        using var response = await _http.GetAsync(ServersUrl, cancellationToken);
        response.EnsureSuccessStatusCode();
        using var json = await JsonDocument.ParseAsync(await response.Content.ReadAsStreamAsync(cancellationToken), cancellationToken: cancellationToken);
        var names = RadioMapper.MapServerNames(json.RootElement).ToArray();
        Random.Shared.Shuffle(names);
        _current = 0;
        return _servers = names.Length > 0 ? names : throw new HttpRequestException("radio-browser.info returned no servers.");
    }

    private static HttpClient CreateHttp()
    {
        var http = new HttpClient { Timeout = TimeSpan.FromSeconds(20) };
        http.DefaultRequestHeaders.UserAgent.Add(new ProductInfoHeaderValue("AudioStar", "0.1"));
        return http;
    }
}
