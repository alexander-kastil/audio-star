using AudioStar.Core;
using AudioStar.Sources.SoundCloud;
using FluentAssertions;

namespace AudioStar.Sources.Tests;

public class SoundCloudMapperTests
{
    [Fact]
    public void MapTracks_FromCapturedPlaylist_UsesNumericIdsAndSlugTitles()
    {
        using var doc = Fixture.Load("soundcloud-playlist-flat.json");

        var tracks = SoundCloudMapper.MapTracks(doc.RootElement);

        tracks.Should().HaveCount(7);
        tracks[0].SourceId.Should().Be(SourceIds.SoundCloud);
        tracks[0].Id.Should().Be("28301249");
        tracks[0].Title.Should().Be("1 durufl introit and kyrie");
        tracks[5].Id.Should().Be("30370224");
        tracks[5].Title.Should().Be("SoundCloud track 30370224");
    }

    [Fact]
    public void MapTracks_FromCapturedLikes_SkipsLikedSets()
    {
        using var doc = Fixture.Load("soundcloud-likes-flat.json");

        var tracks = SoundCloudMapper.MapTracks(doc.RootElement);

        tracks.Should().OnlyContain(t => t.Id.Length > 0);
        tracks.Should().NotContain(t => t.Title == "Acid Jazz");
    }

    [Fact]
    public void MapSets_FromCapturedProfile_ReturnsSetPlaylists()
    {
        using var doc = Fixture.Load("soundcloud-sets-flat.json");

        var sets = SoundCloudMapper.MapSets(doc.RootElement, "Forss");

        sets.Should().NotBeEmpty();
        sets[0].Title.Should().Be("Ecclesia Inspiration");
        sets[0].Id.Should().Be("https://soundcloud.com/forss/sets/ecclesia-inspiration");
        sets[0].Owner.Should().Be("Forss");
    }

    [Theory]
    [InlineData("https://soundcloud.com/forss/sets/x/", "https://soundcloud.com/forss/sets/x")]
    [InlineData("https://example.com/forss", null)]
    [InlineData("garbage", null)]
    public void NormalizeUrl_KeepsOnlySoundCloudLinks(string input, string? expected)
    {
        SoundCloudMapper.NormalizeUrl(input).Should().Be(expected);
    }

    [Fact]
    public void NormalizeProfile_ReducesLinkToProfileRoot()
    {
        SoundCloudMapper.NormalizeProfile("https://soundcloud.com/forss/likes").Should().Be("https://soundcloud.com/forss");
    }
}
