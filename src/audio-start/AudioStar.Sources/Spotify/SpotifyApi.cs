using System.Net;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;

namespace AudioStar.Sources.Spotify;

public sealed class SpotifyApiException(int status, string? reason, string message) : Exception(message)
{
    public int Status { get; } = status;
    public string? Reason { get; } = reason;
}

public sealed class SpotifyApi(SpotifyAuth auth) : IDisposable
{
    private const string BaseUrl = "https://api.spotify.com/v1/";

    private readonly HttpClient _http = new() { BaseAddress = new Uri(BaseUrl), Timeout = TimeSpan.FromSeconds(30) };

    public async Task<JsonDocument> GetAsync(string pathOrUrl, CancellationToken cancellationToken)
    {
        using var response = await SendCoreAsync(HttpMethod.Get, pathOrUrl, null, cancellationToken);
        return JsonDocument.Parse(await response.Content.ReadAsStringAsync(cancellationToken));
    }

    public async Task SendAsync(HttpMethod method, string path, string? jsonBody, CancellationToken cancellationToken)
    {
        using var response = await SendCoreAsync(method, path, jsonBody, cancellationToken);
    }

    public async Task<IReadOnlyList<JsonElement>> GetAllAsync(string path, int maxItems, CancellationToken cancellationToken)
    {
        var items = new List<JsonElement>();
        string? next = path;
        while (next is not null && items.Count < maxItems)
        {
            using var page = await GetAsync(next, cancellationToken);
            foreach (var item in page.RootElement.Items("items"))
            {
                items.Add(item.Clone());
            }
            next = page.RootElement.Str("next");
        }
        return items;
    }

    public void Dispose() => _http.Dispose();

    private async Task<HttpResponseMessage> SendCoreAsync(HttpMethod method, string pathOrUrl, string? jsonBody, CancellationToken cancellationToken)
    {
        for (var attempt = 0; ; attempt++)
        {
            using var request = new HttpRequestMessage(method, pathOrUrl);
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", await auth.GetAccessTokenAsync(cancellationToken));
            if (jsonBody is not null)
            {
                request.Content = new StringContent(jsonBody, Encoding.UTF8, "application/json");
            }
            var response = await _http.SendAsync(request, cancellationToken);
            if (response.IsSuccessStatusCode)
            {
                return response;
            }

            var body = await response.Content.ReadAsStringAsync(cancellationToken);
            var status = (int)response.StatusCode;
            if (attempt == 0 && response.StatusCode == HttpStatusCode.Unauthorized)
            {
                response.Dispose();
                auth.InvalidateAccessToken();
                continue;
            }
            if (attempt == 0 && response.StatusCode == HttpStatusCode.TooManyRequests)
            {
                var wait = response.Headers.RetryAfter?.Delta ?? TimeSpan.FromSeconds(2);
                response.Dispose();
                await Task.Delay(wait > TimeSpan.FromSeconds(10) ? TimeSpan.FromSeconds(10) : wait, cancellationToken);
                continue;
            }
            response.Dispose();
            throw ToException(status, body);
        }
    }

    internal static SpotifyApiException ToException(int status, string body)
    {
        string? message = null;
        string? reason = null;
        try
        {
            using var json = JsonDocument.Parse(body);
            var error = json.RootElement.Get("error");
            message = error?.Str("message");
            reason = error?.Str("reason");
        }
        catch (JsonException)
        {
        }

        var friendly = (status, reason) switch
        {
            (_, "PREMIUM_REQUIRED") => "Spotify Premium is required to play on a speaker.",
            (404, _) when message?.Contains("device", StringComparison.OrdinalIgnoreCase) == true || reason == "NO_ACTIVE_DEVICE" =>
                "Spotify could not reach the speaker. Pick the speaker once in the Spotify app, then try again.",
            (403, _) => $"Spotify refused the request: {message ?? "forbidden"}. In development mode the account must be added to the app's users and the app owner needs Premium.",
            (429, _) => "The Spotify rate limit was reached. Try again in a moment.",
            _ => $"Spotify returned {status}: {message ?? "unexpected answer"}"
        };
        return new SpotifyApiException(status, reason, friendly);
    }
}
