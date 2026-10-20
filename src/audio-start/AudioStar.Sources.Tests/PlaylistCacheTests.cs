using System.Text.Json;
using AudioStar.Core;
using AudioStar.Sources.YouTube;
using AudioStar.Sources.YtDlp;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using NSubstitute;

namespace AudioStar.Sources.Tests;

public sealed class PlaylistCacheTests : IDisposable
{
    private const string Url = "https://www.youtube.com/playlist?list=PL1";

    private readonly string _directory = Path.Combine(Path.GetTempPath(), $"audiostar-cache-{Guid.NewGuid():N}");
    private readonly JsonPlaylistCache _cache;

    public PlaylistCacheTests()
    {
        _cache = new JsonPlaylistCache(_directory, NullLogger<JsonPlaylistCache>.Instance);
    }

    public void Dispose()
    {
        if (Directory.Exists(_directory))
        {
            Directory.Delete(_directory, true);
        }
    }

    [Fact]
    public async Task Cache_RoundTrip_KeepsHeaderTracksAndFetchTime()
    {
        var entry = new CachedPlaylist(
            new SourcePlaylist(SourceIds.YouTube, Url, "Mix", "Me", 2, new Uri("https://i.ytimg.com/a.jpg"), new Uri(Url)),
            [new SourceTrack(SourceIds.YouTube, "a", "First", "Me", null, TimeSpan.FromSeconds(61), null), new SourceTrack(SourceIds.YouTube, "b", "Second", null, null, null, null)],
            new DateTimeOffset(2026, 10, 19, 8, 0, 0, TimeSpan.Zero));

        await _cache.SaveAsync(entry);
        var loaded = await _cache.GetAsync(SourceIds.YouTube, Url);

        loaded.Should().BeEquivalentTo(entry);
        Directory.GetFiles(Path.Combine(_directory, SourceIds.YouTube), "*.json").Should().ContainSingle();
    }

    [Fact]
    public async Task Cache_UnknownPlaylist_IsMiss()
    {
        (await _cache.GetAsync(SourceIds.YouTube, Url)).Should().BeNull();
    }

    [Fact]
    public async Task Cache_CorruptFile_IsMiss()
    {
        await _cache.SaveAsync(Entry("Mix", Track("a", "First")));
        var file = Directory.GetFiles(Path.Combine(_directory, SourceIds.YouTube), "*.json").Single();
        await File.WriteAllTextAsync(file, "{ not json");

        (await _cache.GetAsync(SourceIds.YouTube, Url)).Should().BeNull();
    }

    [Fact]
    public async Task GetTracks_CacheHit_ReturnsWithoutWaitingOnYtDlp_AndRefreshUpdatesFile()
    {
        await _cache.SaveAsync(Entry("Old title", Track("a", "Old")));
        var release = new TaskCompletionSource();
        var ytDlp = Substitute.For<IYtDlp>();
        ytDlp.GetJsonAsync(Arg.Any<IReadOnlyList<string>>(), Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>())
            .Returns(async _ =>
            {
                await release.Task;
                return Listing("New title", ("b", "New one"), ("a", "Old"));
            });
        var source = CreateSource(ytDlp, [Url]);
        var playlist = (await source.GetPlaylistsAsync()).Single();

        var tracks = await source.GetTracksAsync(playlist).WaitAsync(TimeSpan.FromSeconds(5));

        playlist.Title.Should().Be("Old title");
        tracks.Select(t => t.Id).Should().Equal("a");
        await ytDlp.DidNotReceive().GetJsonAsync(Arg.Is<IReadOnlyList<string>>(a => a.Contains("--playlist-items")), Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>());

        release.SetResult();
        var refreshed = await WaitForAsync(async () => await _cache.GetAsync(SourceIds.YouTube, Url) is { Tracks.Count: 2 } entry ? entry : null);
        refreshed.Playlist.Title.Should().Be("New title");
        refreshed.Tracks!.Select(t => t.Id).Should().Equal("b", "a");
        await ytDlp.Received(1).GetJsonAsync(Arg.Any<IReadOnlyList<string>>(), Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task GetTracks_NoCache_FetchesAndSaves()
    {
        var ytDlp = Substitute.For<IYtDlp>();
        ytDlp.GetJsonAsync(Arg.Any<IReadOnlyList<string>>(), Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>())
            .Returns(_ => Listing("Fresh", ("a", "One")));
        var source = CreateSource(ytDlp, []);
        var playlist = new SourcePlaylist(SourceIds.YouTube, Url, Url, null, null, null, null);
        await source.AddPlaylistByUrlAsync(Url);

        var tracks = await source.GetTracksAsync(playlist);

        tracks.Select(t => t.Id).Should().Equal("a");
        var saved = await _cache.GetAsync(SourceIds.YouTube, Url);
        saved!.Tracks!.Select(t => t.Id).Should().Equal("a");
        saved.Playlist.Title.Should().Be("Fresh");
    }

    [Fact]
    public async Task Play_UsesTheListLastShown_EvenWhenTheCacheChangedInTheBackground()
    {
        await _cache.SaveAsync(Entry("Mix", Track("a", "A"), Track("b", "B"), Track("c", "C")));
        var ytDlp = Substitute.For<IYtDlp>();
        ytDlp.GetJsonAsync(Arg.Any<IReadOnlyList<string>>(), Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>())
            .Returns(_ => Listing("Mix", ("c", "C"), ("new", "New"), ("a", "A"), ("b", "B")));
        var source = CreateSource(ytDlp, [Url]);
        var playlist = (await source.GetPlaylistsAsync()).Single();
        await source.GetTracksAsync(playlist);
        await WaitForAsync(async () => await _cache.GetAsync(SourceIds.YouTube, Url) is { Tracks.Count: 4 } entry ? entry : null);
        var controller = Substitute.For<ISpeakerController>();
        var speaker = Substitute.For<ISpeakerSession>();
        speaker.Controller.Returns(controller);
        speaker.Info.Returns(new SpeakerInfo("id", "Kitchen", "192.168.0.1", 1400, "Model", "1.0"));
        PlayRequest? played = null;
        await controller.PlayAsync(Arg.Do<PlayRequest>(r => played = r), Arg.Any<CancellationToken>());

        await source.PlayAsync(speaker, playlist, 1);

        played!.Items.Select(i => i.Id).Should().Equal("a", "b", "c");
        played.StartIndex.Should().Be(1);
        await ytDlp.Received(1).GetJsonAsync(Arg.Any<IReadOnlyList<string>>(), Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task Play_WithoutShownList_FallsBackToGetTracks()
    {
        var ytDlp = Substitute.For<IYtDlp>();
        ytDlp.GetJsonAsync(Arg.Any<IReadOnlyList<string>>(), Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>())
            .Returns(_ => Listing("Mix", ("a", "A"), ("b", "B")));
        var source = CreateSource(ytDlp, []);
        var playlist = new SourcePlaylist(SourceIds.YouTube, "library-list", "Library", null, null, null, null);
        var controller = Substitute.For<ISpeakerController>();
        var speaker = Substitute.For<ISpeakerSession>();
        speaker.Controller.Returns(controller);
        speaker.Info.Returns(new SpeakerInfo("id", "Kitchen", "192.168.0.1", 1400, "Model", "1.0"));
        PlayRequest? played = null;
        await controller.PlayAsync(Arg.Do<PlayRequest>(r => played = r), Arg.Any<CancellationToken>());

        await source.PlayAsync(speaker, playlist);

        played!.Items.Select(i => i.Id).Should().Equal("a", "b");
        Directory.Exists(_directory).Should().BeFalse();
    }

    private YouTubeSource CreateSource(IYtDlp ytDlp, List<string> savedUrls)
    {
        var settings = Substitute.For<ISettingsStore>();
        settings.Current.Returns(new AudioStarSettings { YouTubePlaylistUrls = savedUrls });
        var mediaServer = Substitute.For<IMediaServer>();
        mediaServer.GetStreamUri(Arg.Any<string>(), Arg.Any<string>()).Returns(call => new Uri($"http://localhost/{call.ArgAt<string>(1)}"));
        return new YouTubeSource(ytDlp, settings, mediaServer, Substitute.For<IRecentlyPlayed>(), _cache, NullLogger<YouTubeSource>.Instance);
    }

    private static CachedPlaylist Entry(string title, params SourceTrack[] tracks) =>
        new(new SourcePlaylist(SourceIds.YouTube, Url, title, null, tracks.Length, null, new Uri(Url)), tracks, DateTimeOffset.UtcNow.AddDays(-1));

    private static SourceTrack Track(string id, string title) => new(SourceIds.YouTube, id, title, null, null, null, null);

    private static YtDlpResult Listing(string title, params (string Id, string Title)[] entries)
    {
        var json = JsonSerializer.Serialize(new { title, playlist_count = entries.Length, entries = entries.Select(e => new { id = e.Id, title = e.Title }) });
        return new YtDlpResult(JsonDocument.Parse(json), "", 0);
    }

    private static async Task<T> WaitForAsync<T>(Func<Task<T?>> probe) where T : class
    {
        var deadline = DateTime.UtcNow.AddSeconds(5);
        while (DateTime.UtcNow < deadline)
        {
            if (await probe() is { } value)
            {
                return value;
            }
            await Task.Delay(20);
        }
        throw new TimeoutException("The background refresh did not finish.");
    }
}
