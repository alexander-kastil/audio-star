using System.Net;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace AudioStar.Sources.SoundCloud;

public sealed class SoundCloudTokenRejectedException() : Exception("SoundCloud rejected the stored sign-in.");

public sealed record SoundCloudAccount(string Name, string? ProfileUrl);

public sealed partial class SoundCloudSession : IDisposable
{
    private const string ApiUrl = "https://api-v2.soundcloud.com";
    internal const string RequestKey = "SoundCloudRequest";
    private const string MeUrl = ApiUrl + "/me";

    private readonly SoundCloudTokenStore _store;
    private readonly HttpClient _http;
    private readonly SemaphoreSlim _clientIdGate = new(1, 1);
    private string? _token;
    private bool _loaded;
    private string? _clientId;

    public SoundCloudSession() : this(new SoundCloudTokenStore(), CreateClient())
    {
    }

    internal SoundCloudSession(SoundCloudTokenStore store, HttpClient http)
    {
        _store = store;
        _http = http;
    }

    public bool HasToken => Token is not null;

    private string? Token
    {
        get
        {
            if (!_loaded)
            {
                _token = _store.Load();
                _loaded = true;
            }
            return _token;
        }
    }

    internal static IReadOnlyList<string> AuthArguments(string? token) =>
        string.IsNullOrEmpty(token) ? [] : ["--username", "oauth", "--password", token];

    public IReadOnlyList<string> AuthArguments() => AuthArguments(Token);

    public void Save(string token)
    {
        _store.Save(token);
        _token = token;
        _loaded = true;
    }

    public void Clear()
    {
        _store.Delete();
        _token = null;
        _loaded = true;
    }

    public async Task<SoundCloudAccount> GetAccountAsync(CancellationToken cancellationToken)
    {
        var token = Token ?? throw new InvalidOperationException("SoundCloud is not signed in.");
        for (var attempt = 0; ; attempt++)
        {
            var clientId = await GetClientIdAsync(attempt > 0, cancellationToken);
            using var request = new HttpRequestMessage(HttpMethod.Get, $"{MeUrl}?client_id={clientId}");
            request.Headers.Authorization = new AuthenticationHeaderValue("OAuth", token);
            using var response = await SendAsync(request, cancellationToken);
            if (response.StatusCode is HttpStatusCode.Unauthorized or HttpStatusCode.Forbidden)
            {
                if (attempt == 0)
                {
                    continue;
                }
                throw new SoundCloudTokenRejectedException();
            }
            response.EnsureSuccessStatusCode();
            using var json = JsonDocument.Parse(await response.Content.ReadAsStringAsync(cancellationToken));
            return ParseAccount(json.RootElement) ?? throw new HttpRequestException("SoundCloud returned no account.");
        }
    }

    internal async Task<IReadOnlyList<SoundCloudTrackInfo>> GetTrackInfosAsync(IReadOnlyList<string> ids, CancellationToken cancellationToken)
    {
        var batches = ids.Chunk(SoundCloudApi.TrackBatchSize).Select(async batch =>
        {
            using var json = await GetApiAsync("/tracks", $"ids={string.Join(',', batch)}", cancellationToken);
            return SoundCloudApi.ParseTracks(json.RootElement);
        });
        return (await Task.WhenAll(batches)).SelectMany(b => b).ToList();
    }

    internal async Task<Uri?> GetPlaylistArtworkAsync(string url, CancellationToken cancellationToken)
    {
        using var json = await GetApiAsync("/resolve", $"url={Uri.EscapeDataString(url)}", cancellationToken);
        return SoundCloudApi.PlaylistArtwork(json.RootElement);
    }

    internal async Task<Uri?> GetLikesArtworkAsync(string likesUrl, CancellationToken cancellationToken)
    {
        using var user = await GetApiAsync("/resolve", $"url={Uri.EscapeDataString(likesUrl)}", cancellationToken);
        var userId = user.RootElement.Str("id");
        if (string.IsNullOrEmpty(userId))
        {
            return null;
        }
        using var likes = await GetApiAsync($"/users/{Uri.EscapeDataString(userId)}/track_likes", "limit=1", cancellationToken);
        return SoundCloudApi.FirstLikeArtwork(likes.RootElement);
    }

    internal async Task<IReadOnlyList<SoundCloudTrackInfo>> GetHistoryAsync(CancellationToken cancellationToken)
    {
        var infos = new List<SoundCloudTrackInfo>();
        string? url = $"{ApiUrl}/me/play-history/tracks?limit={SoundCloudApi.HistoryPageSize}&linked_partitioning=1";
        for (var page = 0; page < SoundCloudApi.HistoryMaxPages && url is not null; page++)
        {
            using var json = await GetApiAsync(url, cancellationToken);
            var (tracks, next) = SoundCloudApi.ParseHistory(json.RootElement);
            infos.AddRange(tracks);
            url = next;
        }
        return infos;
    }

    internal async Task<Uri?> GetHistoryArtworkAsync(CancellationToken cancellationToken)
    {
        using var json = await GetApiAsync($"{ApiUrl}/me/play-history/tracks?limit=1&linked_partitioning=1", cancellationToken);
        return SoundCloudApi.ParseHistory(json.RootElement).Tracks.Select(t => t.Artwork).FirstOrDefault(a => a is not null);
    }

    internal Task<JsonDocument> GetApiAsync(string path, string query, CancellationToken cancellationToken) =>
        GetApiAsync($"{ApiUrl}{path}?{query}", cancellationToken);

    internal async Task<JsonDocument> GetApiAsync(string url, CancellationToken cancellationToken)
    {
        if (!url.StartsWith(ApiUrl + "/", StringComparison.Ordinal))
        {
            throw new HttpRequestException("Refusing to send the SoundCloud sign-in to another host.");
        }
        var token = Token;
        for (var attempt = 0; ; attempt++)
        {
            var clientId = await GetClientIdAsync(attempt > 0, cancellationToken);
            var target = url.Contains("client_id=", StringComparison.Ordinal) ? url : $"{url}{(url.Contains('?') ? '&' : '?')}client_id={clientId}";
            using var request = new HttpRequestMessage(HttpMethod.Get, target);
            if (!string.IsNullOrEmpty(token))
            {
                request.Headers.Authorization = new AuthenticationHeaderValue("OAuth", token);
            }
            using var response = await SendAsync(request, cancellationToken);
            if (attempt == 0 && response.StatusCode is HttpStatusCode.Unauthorized or HttpStatusCode.Forbidden)
            {
                continue;
            }
            response.EnsureSuccessStatusCode();
            return JsonDocument.Parse(await response.Content.ReadAsStringAsync(cancellationToken));
        }
    }

    internal static SoundCloudAccount? ParseAccount(JsonElement root)
    {
        var name = root.Str("username") ?? root.Str("permalink");
        if (name is null)
        {
            return null;
        }
        var profile = SoundCloudMapper.NormalizeProfile(root.Str("permalink_url"));
        return new SoundCloudAccount(name, profile);
    }

    internal static string? FindClientId(string script) =>
        ClientIdPattern().Match(script) is { Success: true } match ? match.Groups[1].Value : null;

    internal static IReadOnlyList<string> FindScriptUrls(string html) =>
        ScriptPattern().Matches(html).Select(m => m.Groups[1].Value).Where(u => Uri.IsWellFormedUriString(u, UriKind.Absolute)).ToList();

    public void Dispose()
    {
        _http.Dispose();
        _clientIdGate.Dispose();
    }

    private async Task<string> GetClientIdAsync(bool refresh, CancellationToken cancellationToken)
    {
        await _clientIdGate.WaitAsync(cancellationToken);
        try
        {
            if (_clientId is not null && !refresh)
            {
                return _clientId;
            }
            var html = await GetStringAsync("https://soundcloud.com/", cancellationToken);
            foreach (var url in FindScriptUrls(html).AsEnumerable().Reverse())
            {
                var script = await GetStringAsync(url, cancellationToken);
                if (FindClientId(script) is { } found)
                {
                    return _clientId = found;
                }
            }
            throw new HttpRequestException("Could not read the SoundCloud web client id.");
        }
        finally
        {
            _clientIdGate.Release();
        }
    }

    private async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
    {
        try
        {
            return await _http.SendAsync(request, cancellationToken);
        }
        catch (Exception exception) when (exception is HttpRequestException or TaskCanceledException && !cancellationToken.IsCancellationRequested)
        {
            Tag(exception, request.RequestUri!);
            throw;
        }
    }

    private async Task<string> GetStringAsync(string url, CancellationToken cancellationToken)
    {
        try
        {
            return await _http.GetStringAsync(url, cancellationToken);
        }
        catch (Exception exception) when (exception is HttpRequestException or TaskCanceledException && !cancellationToken.IsCancellationRequested)
        {
            Tag(exception, new Uri(url));
            throw;
        }
    }

    private static void Tag(Exception exception, Uri uri) =>
        exception.Data[RequestKey] = $"GET {uri.GetLeftPart(UriPartial.Path)}";

    private static HttpClient CreateClient()
    {
        var http = new HttpClient { Timeout = TimeSpan.FromSeconds(30) };
        http.DefaultRequestHeaders.UserAgent.ParseAdd("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36");
        return http;
    }

    [GeneratedRegex(@"client_id\s*:\s*""([0-9a-zA-Z]{32})""")]
    private static partial Regex ClientIdPattern();

    [GeneratedRegex(@"<script[^>]+src=""([^""]+)""")]
    private static partial Regex ScriptPattern();
}
