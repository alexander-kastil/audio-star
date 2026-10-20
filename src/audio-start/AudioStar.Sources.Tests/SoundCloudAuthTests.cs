using System.Net;
using AudioStar.Core;
using AudioStar.Sources.SoundCloud;
using AudioStar.Sources.Spotify;
using AudioStar.Sources.YtDlp;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using NSubstitute;
using NSubstitute.ExceptionExtensions;

namespace AudioStar.Sources.Tests;

public sealed class SoundCloudAuthTests : IDisposable
{
    private const string Token = "2-293456-1234567-AbCdEfGhIj";
    private const string ClientId = "abcdefghijklmnopqrstuvwxyz012345";

    private readonly string _directory = Path.Combine(Path.GetTempPath(), $"audiostar-sc-{Guid.NewGuid():N}");
    private readonly IWebSignIn _webSignIn = Substitute.For<IWebSignIn>();
    private readonly ISettingsStore _settings = Substitute.For<ISettingsStore>();
    private readonly IYtDlp _ytDlp = Substitute.For<IYtDlp>();
    private readonly StubHandler _handler = new();

    public SoundCloudAuthTests()
    {
        _settings.Current.Returns(new AudioStarSettings());
    }

    public void Dispose()
    {
        if (Directory.Exists(_directory))
        {
            Directory.Delete(_directory, true);
        }
    }

    [Fact]
    public void TokenStore_RoundTripsThroughDpapi()
    {
        var path = Path.Combine(_directory, "soundcloud-token.bin");
        var store = new SoundCloudTokenStore(path);
        store.Load().Should().BeNull();

        store.Save(Token);

        store.Load().Should().Be(Token);
        File.ReadAllText(path).Should().NotContain(Token);
        store.Delete();
        store.Load().Should().BeNull();
    }

    [Fact]
    public void TokenStore_DoesNotReadTheSpotifyEntropy()
    {
        var path = Path.Combine(_directory, "shared.bin");
        new SpotifyTokenStore(path).Save("client", "refresh");

        new SoundCloudTokenStore(path).Load().Should().BeNull();
    }

    [Fact]
    public void AuthArguments_UseTheOauthLogin()
    {
        SoundCloudSession.AuthArguments(Token).Should().Equal("--username", "oauth", "--password", Token);
        SoundCloudSession.AuthArguments(null).Should().BeEmpty();
        SoundCloudSession.AuthArguments("").Should().BeEmpty();
    }

    [Fact]
    public void Redact_MasksThePasswordArgumentInOutput()
    {
        var arguments = new[] { "-J", "--username", "oauth", "--password", Token, "https://soundcloud.com/a" };

        var text = YtDlpRedaction.Redact(arguments, $"ERROR: login failed for {Token}");

        text.Should().Be("ERROR: login failed for ***");
        YtDlpRedaction.Redact(["-J"], "unchanged").Should().Be("unchanged");
    }

    [Fact]
    public void FindClientId_ReadsTheWebClientIdFromAScript()
    {
        SoundCloudSession.FindClientId($"x={{}};t={{client_id:\"{ClientId}\",y:1}}").Should().Be(ClientId);
        SoundCloudSession.FindClientId("nothing here").Should().BeNull();
    }

    [Fact]
    public void ParseAccount_ReadsNameAndProfile()
    {
        using var doc = Fixture.Parse("""{"id":1,"username":"Alex Beats","permalink":"alex-beats","permalink_url":"https://soundcloud.com/alex-beats"}""");

        SoundCloudSession.ParseAccount(doc.RootElement).Should().Be(new SoundCloudAccount("Alex Beats", "https://soundcloud.com/alex-beats"));
    }

    [Fact]
    public async Task Connect_SignsInThroughCookieModeAndStoresTheToken()
    {
        _webSignIn.SignInAsync(Arg.Any<WebSignInRequest>(), Arg.Any<CancellationToken>()).Returns(new WebSignInResult(null, Token));
        var (source, session) = CreateSource();

        var status = await source.ConnectAsync();

        status.State.Should().Be(SourceConnectionState.Connected);
        status.AccountName.Should().Be("Alex Beats");
        session.HasToken.Should().BeTrue();
        new SoundCloudTokenStore(Path.Combine(_directory, "soundcloud-token.bin")).Load().Should().Be(Token);
        var request = (WebSignInRequest)_webSignIn.ReceivedCalls().Single().GetArguments()[0]!;
        request.StartUri.Should().Be(new Uri("https://soundcloud.com/signin"));
        request.CookieUri.Should().Be(new Uri("https://soundcloud.com"));
        request.CookieName.Should().Be("oauth_token");
        _handler.MeAuthorization.Should().Be($"OAuth {Token}");
    }

    [Fact]
    public async Task Connect_WindowClosed_ContinuesWithoutSignIn()
    {
        _webSignIn.SignInAsync(Arg.Any<WebSignInRequest>(), Arg.Any<CancellationToken>()).Returns((WebSignInResult?)null);
        var (source, session) = CreateSource();

        var status = await source.ConnectAsync();

        status.State.Should().Be(SourceConnectionState.NotConfigured);
        session.HasToken.Should().BeFalse();
    }

    [Fact]
    public async Task Connect_MissingWebView_SetsErrorWithItsMessage()
    {
        _webSignIn.SignInAsync(Arg.Any<WebSignInRequest>(), Arg.Any<CancellationToken>()).ThrowsAsync(new InvalidOperationException("WebView2 runtime missing"));
        var (source, _) = CreateSource();

        var status = await source.ConnectAsync();

        status.Should().Be(new SourceStatus(SourceConnectionState.Error, null, "WebView2 runtime missing"));
    }

    [Fact]
    public async Task ConnectSilently_NeverOpensTheWindow_AndUsesTheStoredToken()
    {
        var (source, session) = CreateSource();
        var withoutToken = await source.ConnectSilentlyAsync();
        session.Save(Token);

        var withToken = await source.ConnectSilentlyAsync();

        withoutToken.State.Should().Be(SourceConnectionState.NotConfigured);
        withToken.State.Should().Be(SourceConnectionState.Connected);
        await _webSignIn.DidNotReceiveWithAnyArgs().SignInAsync(default!, default);
    }

    [Fact]
    public async Task ConnectSilently_ThroughTheInterface_ReachesTheOverride()
    {
        var (source, session) = CreateSource();
        session.Save(Token);

        var status = await ((IMusicSource)source).ConnectSilentlyAsync();

        status.State.Should().Be(SourceConnectionState.Connected);
        await _webSignIn.DidNotReceiveWithAnyArgs().SignInAsync(default!, default);
    }

    [Fact]
    public async Task Connect_RejectedToken_IsDeletedAndTellsTheUserToConnectAgain()
    {
        _handler.MeStatus = HttpStatusCode.Unauthorized;
        var (source, session) = CreateSource();
        session.Save(Token);

        var status = await source.ConnectSilentlyAsync();

        status.State.Should().Be(SourceConnectionState.Error);
        status.Message.Should().Contain("Connect again").And.NotContain(Token);
        session.HasToken.Should().BeFalse();
        new SoundCloudTokenStore(Path.Combine(_directory, "soundcloud-token.bin")).Load().Should().BeNull();
    }

    [Fact]
    public async Task Playlists_WithAccountAndNoProfileSetting_UseTheAccountProfile_AndPassTheToken()
    {
        _ytDlp.GetJsonAsync(Arg.Any<IReadOnlyList<string>>(), Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>())
            .Returns(_ => new YtDlpResult(Fixture.Parse("""{"entries":[]}"""), "", 0));
        var (source, session) = CreateSource();
        session.Save(Token);
        await source.ConnectSilentlyAsync();

        var playlists = await source.GetPlaylistsAsync();

        playlists.Should().Contain(p => p.Id == "https://soundcloud.com/alex-beats/likes");
        await _ytDlp.Received().GetJsonAsync(
            Arg.Is<IReadOnlyList<string>>(a => a.SequenceEqual(new[] { "--username", "oauth", "--password", Token, "-J", "--flat-playlist", "--ignore-errors", "https://soundcloud.com/alex-beats/sets" })),
            Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task Playlists_ProfileSettingWinsOverTheAccountProfile()
    {
        _settings.Current.Returns(new AudioStarSettings { SoundCloudProfileUrl = "https://soundcloud.com/other" });
        _ytDlp.GetJsonAsync(Arg.Any<IReadOnlyList<string>>(), Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>())
            .Returns(_ => new YtDlpResult(Fixture.Parse("""{"entries":[]}"""), "", 0));
        var (source, session) = CreateSource();
        session.Save(Token);
        await source.ConnectSilentlyAsync();

        var playlists = await source.GetPlaylistsAsync();

        playlists.Should().Contain(p => p.Id == "https://soundcloud.com/other/likes");
    }

    [Fact]
    public async Task Disconnect_DeletesTheTokenAndSignsOutOfSoundCloud()
    {
        var (source, session) = CreateSource();
        session.Save(Token);

        await source.DisconnectAsync();

        session.HasToken.Should().BeFalse();
        await _webSignIn.Received().SignOutAsync(new Uri("https://soundcloud.com"), Arg.Any<CancellationToken>());
        source.Status.State.Should().Be(SourceConnectionState.Disconnected);
    }

    [Fact]
    public async Task StreamResolver_PassesTheTokenToYtDlp()
    {
        _ytDlp.GetJsonAsync(Arg.Any<IReadOnlyList<string>>(), Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>())
            .Returns(_ => new YtDlpResult(Fixture.Parse("""{"formats":[]}"""), "", 0));
        var (_, session) = CreateSource();
        session.Save(Token);
        var resolver = new SoundCloudStreamResolver(_ytDlp, session, NullLogger<SoundCloudStreamResolver>.Instance);

        var act = () => resolver.ResolveAsync("123456");

        await act.Should().ThrowAsync<YtDlpException>();
        await _ytDlp.Received().GetJsonAsync(
            Arg.Is<IReadOnlyList<string>>(a => a.Take(4).SequenceEqual(new[] { "-J", "--no-playlist", "--no-warnings", "--username" }) && a.Contains(Token)),
            Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>());
    }

    private (SoundCloudSource Source, SoundCloudSession Session) CreateSource()
    {
        var store = new SoundCloudTokenStore(Path.Combine(_directory, "soundcloud-token.bin"));
        var session = new SoundCloudSession(store, new HttpClient(_handler));
        var source = new SoundCloudSource(
            _ytDlp,
            _settings,
            Substitute.For<IMediaServer>(),
            Substitute.For<IRecentlyPlayed>(),
            Substitute.For<IPlaylistCache>(),
            session,
            _webSignIn,
            NullLogger<SoundCloudSource>.Instance);
        return (source, session);
    }

    private sealed class StubHandler : HttpMessageHandler
    {
        public HttpStatusCode MeStatus { get; set; } = HttpStatusCode.OK;
        public string? MeAuthorization { get; private set; }

        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            var url = request.RequestUri!.AbsoluteUri;
            if (url == "https://soundcloud.com/")
            {
                return Reply(HttpStatusCode.OK, "<html><script crossorigin src=\"https://a-v2.sndcdn.com/assets/app.js\"></script></html>");
            }
            if (url.EndsWith("app.js", StringComparison.Ordinal))
            {
                return Reply(HttpStatusCode.OK, $"t={{client_id:\"{ClientId}\"}}");
            }
            MeAuthorization = request.Headers.Authorization?.ToString();
            return Reply(MeStatus, """{"id":1,"username":"Alex Beats","permalink":"alex-beats","permalink_url":"https://soundcloud.com/alex-beats"}""");
        }

        private static Task<HttpResponseMessage> Reply(HttpStatusCode status, string body) =>
            Task.FromResult(new HttpResponseMessage(status) { Content = new StringContent(body) });
    }
}
