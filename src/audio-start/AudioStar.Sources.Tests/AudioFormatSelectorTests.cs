using AudioStar.Sources.YtDlp;
using FluentAssertions;

namespace AudioStar.Sources.Tests;

public class AudioFormatSelectorTests
{
    [Fact]
    public void Select_CapturedYouTubeVideo_PrefersHighestM4a()
    {
        using var doc = Fixture.Load("youtube-video.json");

        var selected = AudioFormatSelector.Select(doc.RootElement);

        selected.Should().NotBeNull();
        selected!.Stream.ContentType.Should().Be("audio/mp4");
        selected.Stream.RequiresTranscode.Should().BeFalse();
        selected.Stream.Url.OriginalString.Should().Contain("itag=140");
        selected.Stream.Headers.Should().ContainKey("User-Agent");
        selected.ExpiresAt.Should().Be(DateTimeOffset.FromUnixTimeSeconds(1792427273));
    }

    [Fact]
    public void Select_OnlyOpusAvailable_RequiresTranscode()
    {
        using var doc = Fixture.Parse("""
            {"formats":[
              {"format_id":"249","ext":"webm","acodec":"opus","vcodec":"none","abr":50,"protocol":"https","url":"https://h/a?expire=1"},
              {"format_id":"251","ext":"webm","acodec":"opus","vcodec":"none","abr":130,"protocol":"https","url":"https://h/b?expire=1"}
            ]}
            """);

        var selected = AudioFormatSelector.Select(doc.RootElement);

        selected!.Stream.Url.AbsoluteUri.Should().Contain("/b");
        selected.Stream.ContentType.Should().Be("audio/webm");
        selected.Stream.RequiresTranscode.Should().BeTrue();
    }

    [Fact]
    public void Select_ProgressiveMp3BeatsHls()
    {
        using var doc = Fixture.Parse("""
            {"formats":[
              {"format_id":"hls_aac_160k","ext":"m4a","acodec":"mp4a.40.2","vcodec":"none","abr":160,"protocol":"m3u8_native","url":"https://h/playlist.m3u8"},
              {"format_id":"http_mp3_128","ext":"mp3","acodec":"mp3","vcodec":"none","abr":128,"protocol":"https","url":"https://h/track.mp3"}
            ]}
            """);

        var selected = AudioFormatSelector.Select(doc.RootElement);

        selected!.Stream.ContentType.Should().Be("audio/mpeg");
        selected.Stream.RequiresTranscode.Should().BeFalse();
    }

    [Fact]
    public void Select_CapturedSoundCloudHlsOnly_PicksBestHlsAndRequiresTranscode()
    {
        using var doc = Fixture.Load("soundcloud-track-hls.json");

        var selected = AudioFormatSelector.Select(doc.RootElement);

        selected!.Stream.Url.AbsoluteUri.Should().Contain("m3u8");
        selected.Stream.ContentType.Should().Be("application/vnd.apple.mpegurl");
        selected.Stream.RequiresTranscode.Should().BeTrue();
        selected.ExpiresAt.Should().Be(DateTimeOffset.FromUnixTimeSeconds(1792413359));
    }

    [Fact]
    public void Select_SkipsVideoOnlyAndDashFormats()
    {
        using var doc = Fixture.Parse("""
            {"formats":[
              {"format_id":"137","ext":"mp4","acodec":"none","vcodec":"avc1","protocol":"https","url":"https://h/v"},
              {"format_id":"140","ext":"m4a","acodec":"mp4a.40.2","vcodec":"none","abr":128,"protocol":"http_dash_segments","url":"https://h/d"}
            ]}
            """);

        AudioFormatSelector.Select(doc.RootElement).Should().BeNull();
    }

    [Theory]
    [InlineData("https://h/videoplayback?expire=1792427273&x=1", 1792427273L)]
    [InlineData("https://h/a.m3u8?expires=1792413359&Policy=x", 1792413359L)]
    [InlineData("https://h/videoplayback/expire/1792427273/id/a", 1792427273L)]
    public void ExpiryOf_ReadsQueryAndPathForms(string url, long expected)
    {
        AudioFormatSelector.ExpiryOf(new Uri(url)).Should().Be(DateTimeOffset.FromUnixTimeSeconds(expected));
    }

    [Fact]
    public void ExpiryOf_WithoutExpiry_ReturnsNull()
    {
        AudioFormatSelector.ExpiryOf(new Uri("https://h/track.mp3")).Should().BeNull();
    }
}
