using System.Text.Json;
using AudioStar.Core;
using AudioStar.Sources.YouTube;
using AudioStar.Sources.YtDlp;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using NSubstitute;

namespace AudioStar.Sources.Tests;

public sealed class EditablePlaylistTests : IDisposable
{
    private const string First = "https://www.youtube.com/playlist?list=PL1";
    private const string Second = "https://www.youtube.com/playlist?list=PL2";
    private const string Third = "https://www.youtube.com/playlist?list=PL3";
    private const string Replacement = "https://www.youtube.com/playlist?list=PL9";

    private readonly string _directory = Path.Combine(Path.GetTempPath(), $"audiostar-edit-{Guid.NewGuid():N}");
    private readonly JsonPlaylistCache _cache;
    private readonly JsonSettingsStore _settings;
    private readonly IYtDlp _ytDlp = Substitute.For<IYtDlp>();

    public EditablePlaylistTests()
    {
        _cache = new JsonPlaylistCache(Path.Combine(_directory, "playlists"), NullLogger<JsonPlaylistCache>.Instance);
        _settings = new JsonSettingsStore(Path.Combine(_directory, "settings.json"));
        _ytDlp.GetJsonAsync(Arg.Any<IReadOnlyList<string>>(), Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>())
            .Returns(call => Listing(TitleFor(call.ArgAt<IReadOnlyList<string>>(0)[^1])));
    }

    public void Dispose()
    {
        if (Directory.Exists(_directory))
        {
            Directory.Delete(_directory, true);
        }
    }

    [Fact]
    public async Task Remove_TakesUrlOutOfSettings_AndDeletesCacheFile()
    {
        var source = CreateSource();
        var first = (await source.AddPlaylistByUrlAsync(First))!;
        await source.AddPlaylistByUrlAsync(Second);
        CacheFiles().Should().HaveCount(2);

        await source.RemovePlaylistAsync(first);

        _settings.Current.YouTubePlaylistUrls.Should().Equal(Second);
        new JsonSettingsStore(Path.Combine(_directory, "settings.json")).Current.YouTubePlaylistUrls.Should().Equal(Second);
        (await _cache.GetAsync(SourceIds.YouTube, First)).Should().BeNull();
        CacheFiles().Should().ContainSingle();
        source.IsAdded(first).Should().BeFalse();
    }

    [Fact]
    public async Task ChangeUrl_KeepsPosition_DropsOldCache_AndSavesNewHeader()
    {
        var source = CreateSource();
        await source.AddPlaylistByUrlAsync(First);
        var second = (await source.AddPlaylistByUrlAsync(Second))!;
        await source.AddPlaylistByUrlAsync(Third);

        var changed = await source.ChangePlaylistUrlAsync(second, Replacement);

        changed!.Id.Should().Be(Replacement);
        changed.Title.Should().Be("Title PL9");
        _settings.Current.YouTubePlaylistUrls.Should().Equal(First, Replacement, Third);
        new JsonSettingsStore(Path.Combine(_directory, "settings.json")).Current.YouTubePlaylistUrls.Should().Equal(First, Replacement, Third);
        (await _cache.GetAsync(SourceIds.YouTube, Second)).Should().BeNull();
        (await _cache.GetAsync(SourceIds.YouTube, Replacement))!.Playlist.Title.Should().Be("Title PL9");
        CacheFiles().Should().HaveCount(3);
        source.IsAdded(changed).Should().BeTrue();
        source.IsAdded(second).Should().BeFalse();
    }

    [Fact]
    public async Task ChangeUrl_Invalid_ReturnsNull_AndChangesNothing()
    {
        var source = CreateSource();
        var first = (await source.AddPlaylistByUrlAsync(First))!;
        await source.AddPlaylistByUrlAsync(Second);
        var calls = _ytDlp.ReceivedCalls().Count();

        var changed = await source.ChangePlaylistUrlAsync(first, "https://example.com/not-a-playlist");

        changed.Should().BeNull();
        _settings.Current.YouTubePlaylistUrls.Should().Equal(First, Second);
        (await _cache.GetAsync(SourceIds.YouTube, First)).Should().NotBeNull();
        CacheFiles().Should().HaveCount(2);
        _ytDlp.ReceivedCalls().Should().HaveCount(calls);
        source.IsAdded(first).Should().BeTrue();
    }

    [Fact]
    public async Task IsAdded_IsFalseForLibraryPlaylists_EvenWhenTheUrlWasAlsoPasted()
    {
        _settings.Current.YouTubeCookieSource = "firefox";
        _ytDlp.GetJsonAsync(Arg.Any<IReadOnlyList<string>>(), Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>())
            .Returns(call => call.ArgAt<IReadOnlyList<string>>(0)[^1].Contains("feed/playlists")
                ? Library(("PL1", "Library one"), ("PL2", "Library two"))
                : Listing("Pasted"));
        var source = CreateSource();
        _settings.Current.YouTubePlaylistUrls.Add(Second);
        var playlists = await source.GetPlaylistsAsync();
        playlists.Should().HaveCount(3);
        playlists[0].Title.Should().Be("History");
        playlists[0].Id.Should().Be("https://www.youtube.com/feed/history");

        playlists.Select(source.IsAdded).Should().AllBeEquivalentTo(false);

        var pasted = (await source.AddPlaylistByUrlAsync(Third))!;
        source.IsAdded(pasted).Should().BeTrue();
    }

    [Fact]
    public async Task History_IsOfferedOnlyWithCookies_AndTakesTheFirstThumbnail()
    {
        _ytDlp.GetJsonAsync(Arg.Any<IReadOnlyList<string>>(), Arg.Any<TimeSpan>(), Arg.Any<CancellationToken>())
            .Returns(call => call.ArgAt<IReadOnlyList<string>>(0)[^1].Contains("feed/history")
                ? new YtDlpResult(JsonDocument.Parse("""{"title":"Watch history","entries":[{"id":"a","title":"One","thumbnails":[{"url":"https://i.ytimg.com/vi/a/hq.jpg"}]}]}"""), "", 0)
                : Library(("PL1", "Library one")));
        var source = CreateSource();

        (await source.GetPlaylistsAsync()).Should().NotContain(p => p.Title == "History");

        _settings.Current.YouTubeCookieSource = "firefox";
        var playlists = await source.GetPlaylistsAsync();

        playlists[0].Title.Should().Be("History");
        playlists[0].ArtworkUri.Should().Be(new Uri("https://i.ytimg.com/vi/a/hqdefault.jpg"));
        source.IsAdded(playlists[0]).Should().BeFalse();
    }

    private YouTubeSource CreateSource() =>
        new(_ytDlp, _settings, Substitute.For<IMediaServer>(), Substitute.For<IRecentlyPlayed>(), _cache, NullLogger<YouTubeSource>.Instance);

    private string[] CacheFiles() =>
        Directory.Exists(Path.Combine(_directory, "playlists", SourceIds.YouTube))
            ? Directory.GetFiles(Path.Combine(_directory, "playlists", SourceIds.YouTube), "*.json")
            : [];

    private static string TitleFor(string url) => $"Title {url[(url.LastIndexOf('=') + 1)..]}";

    private static YtDlpResult Listing(string title)
    {
        var json = JsonSerializer.Serialize(new { title, playlist_count = 1, entries = new[] { new { id = "a", title = "One" } } });
        return new YtDlpResult(JsonDocument.Parse(json), "", 0);
    }

    private static YtDlpResult Library(params (string Id, string Title)[] lists)
    {
        var json = JsonSerializer.Serialize(new { entries = lists.Select(l => new { id = l.Id, title = l.Title, url = $"https://www.youtube.com/playlist?list={l.Id}" }) });
        return new YtDlpResult(JsonDocument.Parse(json), "", 0);
    }
}
