using System.Net;
using AudioStar.Core;
using AudioStar.Sources.SoundCloud;
using AudioStar.Sources.YtDlp;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using NSubstitute;

namespace AudioStar.Sources.Tests;

public sealed class SoundCloudConnectRetryTests : IDisposable
{
    private const string Token = "2-293456-1234567-AbCdEfGhIj";
    private const string ClientId = "abcdefghijklmnopqrstuvwxyz012345";

    private readonly string _directory = Path.Combine(Path.GetTempPath(), $"audiostar-scr-{Guid.NewGuid():N}");

    public void Dispose()
    {
        if (Directory.Exists(_directory))
        {
            Directory.Delete(_directory, true);
        }
    }

    [Fact]
    public void ShouldRetry_TimeoutAndHttpErrors_UntilTheLastAttempt()
    {
        SoundCloudSource.ShouldRetry(new TaskCanceledException(), 0, 3, default).Should().BeTrue();
        SoundCloudSource.ShouldRetry(new HttpRequestException(), 2, 3, default).Should().BeTrue();
        SoundCloudSource.ShouldRetry(new HttpRequestException(), 3, 3, default).Should().BeFalse();
    }

    [Fact]
    public void ShouldRetry_NotForRejectionParseErrorsOrCancellation()
    {
        using var cts = new CancellationTokenSource();
        cts.Cancel();

        SoundCloudSource.ShouldRetry(new SoundCloudTokenRejectedException(), 0, 3, default).Should().BeFalse();
        SoundCloudSource.ShouldRetry(new System.Text.Json.JsonException(), 0, 3, default).Should().BeFalse();
        SoundCloudSource.ShouldRetry(new TaskCanceledException(), 0, 3, cts.Token).Should().BeFalse();
    }

    [Fact]
    public async Task Connect_TransientTimeouts_RetryAndConnect()
    {
        var handler = new FlakyHandler(failures: 2);
        var (source, _) = CreateSource(handler);

        var status = await source.ConnectSilentlyAsync();

        status.State.Should().Be(SourceConnectionState.Connected);
        handler.MeCalls.Should().Be(3);
    }

    [Fact]
    public async Task Connect_KeepsConnectingBetweenAttempts()
    {
        var handler = new FlakyHandler(failures: 1);
        var (source, _) = CreateSource(handler);
        var states = new List<SourceConnectionState>();
        source.StatusChanged += (_, s) => states.Add(s.State);

        await source.ConnectSilentlyAsync();

        states.Should().NotContain(SourceConnectionState.Error);
        states.Last().Should().Be(SourceConnectionState.Connected);
    }

    [Fact]
    public async Task Connect_AllAttemptsFail_SetsErrorAfterTheLastOne()
    {
        var handler = new FlakyHandler(failures: 100);
        var (source, _) = CreateSource(handler);

        var status = await source.ConnectSilentlyAsync();

        status.State.Should().Be(SourceConnectionState.Error);
        handler.MeCalls.Should().Be(4);
    }

    [Fact]
    public async Task Connect_RejectedToken_IsNotRetried()
    {
        var handler = new FlakyHandler(failures: 0) { Status = HttpStatusCode.Unauthorized };
        var (source, session) = CreateSource(handler);

        var status = await source.ConnectSilentlyAsync();

        status.State.Should().Be(SourceConnectionState.Error);
        session.HasToken.Should().BeFalse();
        handler.MeCalls.Should().Be(2);
    }

    [Fact]
    public async Task Session_FailedRequest_IsNamedWithoutQueryOrToken()
    {
        var handler = new FlakyHandler(failures: 1);
        var (_, session) = CreateSource(handler);

        var act = () => session.GetAccountAsync(default);

        var thrown = (await act.Should().ThrowAsync<TaskCanceledException>()).Which;
        var request = (string)thrown.Data[SoundCloudSession.RequestKey]!;
        request.Should().Be("GET https://api-v2.soundcloud.com/me");
        request.Should().NotContain(ClientId).And.NotContain(Token);
    }

    private (SoundCloudSource Source, SoundCloudSession Session) CreateSource(HttpMessageHandler handler)
    {
        var store = new SoundCloudTokenStore(Path.Combine(_directory, "soundcloud-token.bin"));
        var session = new SoundCloudSession(store, new HttpClient(handler));
        session.Save(Token);
        var settings = Substitute.For<ISettingsStore>();
        settings.Current.Returns(new AudioStarSettings());
        var source = new SoundCloudSource(
            Substitute.For<IYtDlp>(),
            settings,
            Substitute.For<IMediaServer>(),
            Substitute.For<IRecentlyPlayed>(),
            Substitute.For<IPlaylistCache>(),
            session,
            Substitute.For<IWebSignIn>(),
            NullLogger<SoundCloudSource>.Instance)
        {
            RetryDelays = [TimeSpan.Zero, TimeSpan.Zero, TimeSpan.Zero]
        };
        return (source, session);
    }

    private sealed class FlakyHandler(int failures) : HttpMessageHandler
    {
        public int MeCalls { get; private set; }
        public HttpStatusCode Status { get; set; } = HttpStatusCode.OK;

        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            var url = request.RequestUri!.AbsoluteUri;
            if (url == "https://soundcloud.com/")
            {
                return Reply(HttpStatusCode.OK, "<html><script src=\"https://a-v2.sndcdn.com/assets/app.js\"></script></html>");
            }
            if (url.EndsWith("app.js", StringComparison.Ordinal))
            {
                return Reply(HttpStatusCode.OK, $"t={{client_id:\"{ClientId}\"}}");
            }
            MeCalls++;
            if (MeCalls <= failures)
            {
                throw new TaskCanceledException("The request was canceled due to the configured HttpClient.Timeout of 30 seconds elapsing.");
            }
            return Reply(Status, """{"id":1,"username":"Alex Beats","permalink":"alex-beats","permalink_url":"https://soundcloud.com/alex-beats"}""");
        }

        private static Task<HttpResponseMessage> Reply(HttpStatusCode status, string body) =>
            Task.FromResult(new HttpResponseMessage(status) { Content = new StringContent(body) });
    }
}
