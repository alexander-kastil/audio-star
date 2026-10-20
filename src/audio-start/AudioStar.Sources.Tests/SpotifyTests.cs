using System.Web;
using AudioStar.Core;
using AudioStar.Sources.Spotify;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using NSubstitute;
using NSubstitute.ExceptionExtensions;

namespace AudioStar.Sources.Tests;

public class SpotifyTests
{
    [Fact]
    public void Challenge_MatchesRfc7636Example()
    {
        SpotifyPkce.CreateChallenge("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk")
            .Should().Be("E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM");
    }

    [Fact]
    public void Verifier_IsUrlSafeAndWithinPkceLengthLimits()
    {
        var verifier = SpotifyPkce.CreateVerifier();

        verifier.Length.Should().BeInRange(43, 128);
        verifier.Should().MatchRegex("^[A-Za-z0-9_-]+$");
        SpotifyPkce.CreateVerifier().Should().NotBe(verifier);
    }

    [Fact]
    public void AuthorizeUri_CarriesPkceParametersScopesAndLoopbackRedirect()
    {
        var uri = SpotifyAuth.BuildAuthorizeUri("client123", "http://127.0.0.1:22547/callback", "challenge", "state1");

        var query = HttpUtility.ParseQueryString(uri.Query);
        uri.GetLeftPart(UriPartial.Path).Should().Be("https://accounts.spotify.com/authorize");
        query["client_id"].Should().Be("client123");
        query["response_type"].Should().Be("code");
        query["code_challenge_method"].Should().Be("S256");
        query["code_challenge"].Should().Be("challenge");
        query["redirect_uri"].Should().Be("http://127.0.0.1:22547/callback");
        query["scope"]!.Split(' ').Should().BeEquivalentTo(
            "playlist-read-private", "playlist-read-collaborative", "user-library-read", "user-read-playback-state", "user-modify-playback-state");
    }

    [Fact]
    public void ParseRedirect_ReadsCodeAndState()
    {
        var callback = SpotifyAuth.ParseRedirect(new Uri("http://127.0.0.1:22547/callback?code=abc&state=xyz"));

        callback.Should().Be(new SpotifyCallback("abc", "xyz", null));
    }

    [Fact]
    public void ParseRedirect_ReadsDeniedError()
    {
        SpotifyAuth.ParseRedirect(new Uri("http://127.0.0.1:22547/callback?error=access_denied&state=xyz")).Error.Should().Be("access_denied");
    }

    [Fact]
    public void ParseRedirect_WithoutQueryHasNoCode()
    {
        SpotifyAuth.ParseRedirect(new Uri("http://127.0.0.1:22547/callback")).Should().Be(new SpotifyCallback(null, null, null));
    }

    [Fact]
    public async Task SignIn_OpensAuthorizeUriInRedirectModeAndRejectsClosedWindow()
    {
        var settings = Substitute.For<ISettingsStore>();
        settings.Current.Returns(new AudioStarSettings { SpotifyClientId = "client123" });
        var webSignIn = Substitute.For<IWebSignIn>();
        webSignIn.SignInAsync(Arg.Any<WebSignInRequest>(), Arg.Any<CancellationToken>()).Returns((WebSignInResult?)null);
        using var auth = new SpotifyAuth(settings, webSignIn, NullLogger<SpotifyAuth>.Instance);

        var act = () => auth.SignInAsync(CancellationToken.None);

        await act.Should().ThrowAsync<SpotifyAuthException>();
        var request = (WebSignInRequest)webSignIn.ReceivedCalls().Single().GetArguments()[0]!;
        request.RedirectUri.Should().Be(new Uri("http://127.0.0.1:22547/callback"));
        request.StartUri.GetLeftPart(UriPartial.Path).Should().Be("https://accounts.spotify.com/authorize");
    }

    [Fact]
    public async Task SetUp_ReadsClientIdFromDashboardAddressAndSavesIt()
    {
        var settings = Substitute.For<ISettingsStore>();
        var current = new AudioStarSettings();
        settings.Current.Returns(current);
        var webSignIn = Substitute.For<IWebSignIn>();
        webSignIn.SignInAsync(Arg.Any<WebSignInRequest>(), Arg.Any<CancellationToken>())
            .Returns(new WebSignInResult(new Uri("https://developer.spotify.com/dashboard/0123456789abcdef0123456789ABCDEF/settings"), null));
        using var auth = new SpotifyAuth(settings, webSignIn, NullLogger<SpotifyAuth>.Instance);

        var id = await auth.SetUpClientIdAsync(CancellationToken.None);

        id.Should().Be("0123456789abcdef0123456789abcdef");
        current.SpotifyClientId.Should().Be(id);
        await settings.Received(1).SaveAsync(Arg.Any<CancellationToken>());
        var request = (WebSignInRequest)webSignIn.ReceivedCalls().Single().GetArguments()[0]!;
        request.StartUri.Should().Be(new Uri("https://developer.spotify.com/dashboard/create"));
        request.CopyText.Should().Be("http://127.0.0.1:22547/callback");
    }

    [Fact]
    public async Task SetUp_ClosedWindow_ThrowsAuthException()
    {
        var settings = Substitute.For<ISettingsStore>();
        settings.Current.Returns(new AudioStarSettings());
        var webSignIn = Substitute.For<IWebSignIn>();
        webSignIn.SignInAsync(Arg.Any<WebSignInRequest>(), Arg.Any<CancellationToken>()).Returns((WebSignInResult?)null);
        using var auth = new SpotifyAuth(settings, webSignIn, NullLogger<SpotifyAuth>.Instance);

        var act = () => auth.SetUpClientIdAsync(CancellationToken.None);

        await act.Should().ThrowAsync<SpotifyAuthException>();
        await settings.DidNotReceive().SaveAsync(Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task SignIn_MissingWebView_BecomesAuthException()
    {
        var settings = Substitute.For<ISettingsStore>();
        settings.Current.Returns(new AudioStarSettings { SpotifyClientId = "client123" });
        var webSignIn = Substitute.For<IWebSignIn>();
        webSignIn.SignInAsync(Arg.Any<WebSignInRequest>(), Arg.Any<CancellationToken>()).ThrowsAsync(new InvalidOperationException("WebView2 runtime missing"));
        using var auth = new SpotifyAuth(settings, webSignIn, NullLogger<SpotifyAuth>.Instance);

        var act = () => auth.SignInAsync(CancellationToken.None);

        await act.Should().ThrowAsync<SpotifyAuthException>().WithMessage("WebView2 runtime missing");
    }

    [Fact]
    public void MapPlaylist_ReadsFebruary2026ItemsTotal()
    {
        using var doc = Fixture.Parse("""
            {"id":"37i9dQZF1DXcBWIGoYBM5M","name":"Chill","owner":{"display_name":"Alex"},"items":{"href":"x","total":42},
             "images":[{"url":"https://i.scdn.co/image/a"}],"external_urls":{"spotify":"https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"}}
            """);

        var playlist = SpotifyMapper.MapPlaylist(doc.RootElement)!;

        playlist.SourceId.Should().Be(SourceIds.Spotify);
        playlist.Id.Should().Be("37i9dQZF1DXcBWIGoYBM5M");
        playlist.Title.Should().Be("Chill");
        playlist.Owner.Should().Be("Alex");
        playlist.TrackCount.Should().Be(42);
        playlist.ArtworkUri.Should().Be(new Uri("https://i.scdn.co/image/a"));
    }

    [Fact]
    public void MapPlaylist_FallsBackToLegacyTracksTotal()
    {
        using var doc = Fixture.Parse("""{"id":"abcdefghij1","name":"Old","tracks":{"total":7}}""");

        SpotifyMapper.MapPlaylist(doc.RootElement)!.TrackCount.Should().Be(7);
    }

    [Fact]
    public void MapTracks_ReadsItemAndLegacyTrackAndSkipsEpisodesAndLocalFiles()
    {
        using var doc = Fixture.Parse("""
            {"items":[
              {"item":{"id":"t1","type":"track","name":"One","duration_ms":180500,"artists":[{"name":"A"},{"name":"B"}],"album":{"name":"Album","images":[{"url":"https://i.scdn.co/image/c"}]}}},
              {"track":{"id":"t2","type":"track","name":"Two","artists":[],"album":{}}},
              {"item":{"id":"e1","type":"episode","name":"Pod"}},
              {"item":{"id":"l1","type":"track","name":"Local","is_local":true}},
              {"item":null}
            ]}
            """);

        var tracks = SpotifyMapper.MapTracks(doc.RootElement.GetProperty("items").EnumerateArray());

        tracks.Should().HaveCount(2);
        tracks[0].Id.Should().Be("t1");
        tracks[0].Artist.Should().Be("A, B");
        tracks[0].Album.Should().Be("Album");
        tracks[0].Duration.Should().Be(TimeSpan.FromMilliseconds(180500));
        tracks[0].ArtworkUri.Should().Be(new Uri("https://i.scdn.co/image/c"));
        tracks[1].Artist.Should().BeNull();
    }

    [Fact]
    public void FindDevice_MatchesSpeakerNameCaseInsensitively()
    {
        using var doc = Fixture.Parse("""{"devices":[{"id":"d1","name":"Desktop","is_active":true},{"id":"d2","name":"WiiM Amp Living Room","is_active":false}]}""");

        var device = SpotifyMapper.FindDevice(doc.RootElement, "wiim amp living room");

        device!.Id.Should().Be("d2");
        SpotifyMapper.FindDevice(doc.RootElement, "Kitchen").Should().BeNull();
    }

    [Fact]
    public void BuildPlayBody_PlaylistUsesContextUriAndOffset()
    {
        SpotifyMapper.BuildPlayBody("abc", [], 3).Should().Be("""{"context_uri":"spotify:playlist:abc","offset":{"position":3}}""");
    }

    [Fact]
    public void BuildPlayBody_LikedSongsSendTrackUrisFromStartIndex()
    {
        var tracks = Enumerable.Range(0, 5).Select(i => new SourceTrack(SourceIds.Spotify, $"t{i}", "x", null, null, null, null)).ToList();

        SpotifyMapper.BuildPlayBody(SpotifyMapper.LikedId, tracks, 3).Should().Be("""{"uris":["spotify:track:t3","spotify:track:t4"]}""");
    }

    [Theory]
    [InlineData("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=abc", "37i9dQZF1DXcBWIGoYBM5M")]
    [InlineData("spotify:playlist:37i9dQZF1DXcBWIGoYBM5M", "37i9dQZF1DXcBWIGoYBM5M")]
    [InlineData("https://open.spotify.com/album/37i9dQZF1DXcBWIGoYBM5M", null)]
    public void ParsePlaylistId_AcceptsLinksAndUris(string input, string? expected)
    {
        SpotifyMapper.ParsePlaylistId(input).Should().Be(expected);
    }

    [Fact]
    public void ToException_PremiumRequired_SaysSo()
    {
        var exception = SpotifyApi.ToException(403, """{"error":{"status":403,"message":"Player command failed: Premium required","reason":"PREMIUM_REQUIRED"}}""");

        exception.Message.Should().Contain("Premium");
        exception.Reason.Should().Be("PREMIUM_REQUIRED");
    }

    [Fact]
    public void TokenStore_RoundTripsThroughDpapiAndIgnoresOtherClientIds()
    {
        var path = Path.Combine(Path.GetTempPath(), $"audiostar-token-{Guid.NewGuid():N}.bin");
        try
        {
            var store = new SpotifyTokenStore(path);
            store.Save("client-a", "refresh-secret");

            store.Load("client-a").Should().Be("refresh-secret");
            store.Load("client-b").Should().BeNull();
            File.ReadAllText(path).Should().NotContain("refresh-secret");
        }
        finally
        {
            File.Delete(path);
        }
    }
}
