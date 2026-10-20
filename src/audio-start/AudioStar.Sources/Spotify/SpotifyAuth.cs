using System.Text.Json;
using System.Text.RegularExpressions;
using System.Web;
using AudioStar.Core;
using Microsoft.Extensions.Logging;

namespace AudioStar.Sources.Spotify;

public sealed class SpotifyAuthException(string message) : Exception(message);

public sealed record SpotifyCallback(string? Code, string? State, string? Error);

public sealed class SpotifyAuth(ISettingsStore settings, IWebSignIn webSignIn, ILogger<SpotifyAuth> logger) : IDisposable
{
    public const string AuthorizeEndpoint = "https://accounts.spotify.com/authorize";
    public const string TokenEndpoint = "https://accounts.spotify.com/api/token";
    public const string Scopes = "playlist-read-private playlist-read-collaborative user-library-read user-read-playback-state user-modify-playback-state";

    public const string SetupAddressPattern = @"^https://developer\.spotify\.com/dashboard/(?:applications/)?(?<id>[0-9a-fA-F]{32})(?:[/?#]|$)";
    public const string SetupInstructions = "Sign in to Spotify, then create an app with any name and description. Paste the redirect URI shown below into Redirect URIs, tick Web API, accept the terms and save. If you already have an app with this redirect URI, open it instead.";

    private static readonly TimeSpan SignInTimeout = TimeSpan.FromMinutes(3);
    private static readonly TimeSpan SetupTimeout = TimeSpan.FromMinutes(10);

    private readonly HttpClient _http = new();
    private readonly SpotifyTokenStore _store = new();
    private readonly SemaphoreSlim _gate = new(1, 1);
    private string? _accessToken;
    private DateTimeOffset _accessTokenExpiresAt;

    public string? ClientId => string.IsNullOrWhiteSpace(settings.Current.SpotifyClientId) ? null : settings.Current.SpotifyClientId.Trim();

    public string RedirectUri => $"http://127.0.0.1:{settings.Current.SpotifyRedirectPort}/callback";

    public bool HasStoredToken => ClientId is { } id && _store.Load(id) is not null;

    internal static Uri BuildAuthorizeUri(string clientId, string redirectUri, string challenge, string state)
    {
        var query = HttpUtility.ParseQueryString(string.Empty);
        query["client_id"] = clientId;
        query["response_type"] = "code";
        query["redirect_uri"] = redirectUri;
        query["code_challenge_method"] = "S256";
        query["code_challenge"] = challenge;
        query["state"] = state;
        query["scope"] = Scopes;
        return new Uri($"{AuthorizeEndpoint}?{query}");
    }

    internal static SpotifyCallback ParseRedirect(Uri redirected)
    {
        var query = HttpUtility.ParseQueryString(redirected.Query);
        return new SpotifyCallback(query["code"], query["state"], query["error"]);
    }

    public async Task<string> SetUpClientIdAsync(CancellationToken cancellationToken)
    {
        var request = new WebSignInRequest("Set up Spotify", new Uri("https://developer.spotify.com/dashboard/create"))
        {
            AddressPattern = SetupAddressPattern,
            Instructions = SetupInstructions,
            CopyText = RedirectUri
        };

        WebSignInResult? result;
        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeout.CancelAfter(SetupTimeout);
        try
        {
            result = await webSignIn.SignInAsync(request, timeout.Token);
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            throw new SpotifyAuthException("The Spotify setup was not completed in time.");
        }
        catch (InvalidOperationException exception)
        {
            throw new SpotifyAuthException(exception.Message);
        }

        var match = result?.RedirectedTo is { } address ? Regex.Match(address.AbsoluteUri, SetupAddressPattern) : null;
        if (match is not { Success: true })
        {
            throw new SpotifyAuthException("The Spotify setup was closed before an app was created.");
        }

        var clientId = match.Groups["id"].Value.ToLowerInvariant();
        settings.Current.SpotifyClientId = clientId;
        await settings.SaveAsync(cancellationToken);
        return clientId;
    }

    public async Task SignInAsync(CancellationToken cancellationToken)
    {
        var clientId = ClientId ?? throw new SpotifyAuthException("Enter your Spotify client ID in the settings first.");
        var verifier = SpotifyPkce.CreateVerifier();
        var state = SpotifyPkce.CreateState();
        var authorizeUri = BuildAuthorizeUri(clientId, RedirectUri, SpotifyPkce.CreateChallenge(verifier), state);

        WebSignInResult? result;
        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeout.CancelAfter(SignInTimeout);
        try
        {
            result = await webSignIn.SignInAsync(new WebSignInRequest("Sign in to Spotify", authorizeUri) { RedirectUri = new Uri(RedirectUri) }, timeout.Token);
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            throw new SpotifyAuthException("The Spotify sign-in was not completed in time.");
        }
        catch (InvalidOperationException exception)
        {
            throw new SpotifyAuthException(exception.Message);
        }
        if (result?.RedirectedTo is not { } redirected)
        {
            throw new SpotifyAuthException("The Spotify sign-in was closed before it finished.");
        }

        var callback = ParseRedirect(redirected);
        if (callback.Error is not null)
        {
            throw new SpotifyAuthException($"Spotify sign-in was declined ({callback.Error}).");
        }
        if (callback.State != state || string.IsNullOrEmpty(callback.Code))
        {
            throw new SpotifyAuthException("Spotify sign-in returned an unexpected answer.");
        }

        await ExchangeAsync(clientId, new Dictionary<string, string>
        {
            ["grant_type"] = "authorization_code",
            ["code"] = callback.Code,
            ["redirect_uri"] = RedirectUri,
            ["code_verifier"] = verifier
        }, cancellationToken);
    }

    public async Task<string> GetAccessTokenAsync(CancellationToken cancellationToken)
    {
        if (_accessToken is not null && _accessTokenExpiresAt > DateTimeOffset.UtcNow)
        {
            return _accessToken;
        }
        await _gate.WaitAsync(cancellationToken);
        try
        {
            if (_accessToken is not null && _accessTokenExpiresAt > DateTimeOffset.UtcNow)
            {
                return _accessToken;
            }
            var clientId = ClientId ?? throw new SpotifyAuthException("Enter your Spotify client ID in the settings first.");
            var refreshToken = _store.Load(clientId) ?? throw new SpotifyAuthException("Spotify is not connected. Connect it first.");
            await ExchangeAsync(clientId, new Dictionary<string, string>
            {
                ["grant_type"] = "refresh_token",
                ["refresh_token"] = refreshToken
            }, cancellationToken);
            return _accessToken!;
        }
        finally
        {
            _gate.Release();
        }
    }

    public void InvalidateAccessToken() => _accessToken = null;

    public void SignOut()
    {
        _accessToken = null;
        _store.Delete();
    }

    public void Dispose()
    {
        _http.Dispose();
        _gate.Dispose();
    }

    private async Task ExchangeAsync(string clientId, Dictionary<string, string> form, CancellationToken cancellationToken)
    {
        form["client_id"] = clientId;
        using var response = await _http.PostAsync(TokenEndpoint, new FormUrlEncodedContent(form), cancellationToken);
        var body = await response.Content.ReadAsStringAsync(cancellationToken);
        if (!response.IsSuccessStatusCode)
        {
            var error = TryReadError(body);
            if (error == "invalid_grant" && form["grant_type"] == "refresh_token")
            {
                SignOut();
                throw new SpotifyAuthException("The Spotify session has expired. Connect Spotify again.");
            }
            throw new SpotifyAuthException($"Spotify refused the sign-in ({(int)response.StatusCode} {error}).");
        }

        using var json = JsonDocument.Parse(body);
        _accessToken = json.RootElement.Str("access_token") ?? throw new SpotifyAuthException("Spotify returned no access token.");
        _accessTokenExpiresAt = DateTimeOffset.UtcNow.AddSeconds((json.RootElement.Num("expires_in") ?? 3600) - 60);
        if (json.RootElement.Str("refresh_token") is { Length: > 0 } refresh)
        {
            _store.Save(clientId, refresh);
        }
        logger.LogInformation("Spotify access token obtained via {Grant}", form["grant_type"]);
    }

    private static string? TryReadError(string body)
    {
        try
        {
            using var json = JsonDocument.Parse(body);
            return json.RootElement.Str("error");
        }
        catch (JsonException)
        {
            return null;
        }
    }
}
