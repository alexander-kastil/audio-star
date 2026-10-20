using AudioStar.Core;
using AudioStar.Sources.SoundCloud;
using AudioStar.Sources.YtDlp;
using FluentAssertions;

namespace AudioStar.Sources.Tests;

public class SoundCloudApiTests
{
    private const string TrackJson = """
        {"id":111,"title":"Real Title","duration":445982,
         "artwork_url":"https://i1.sndcdn.com/artworks-000066182438-aadpbh-large.jpg",
         "user":{"username":"Some Artist","avatar_url":"https://i1.sndcdn.com/avatars-1-large.jpg"}}
        """;

    [Fact]
    public void ParseTracks_ReadsFieldsAndUpscalesArtwork()
    {
        using var doc = Fixture.Parse($"[{TrackJson}]");

        var info = SoundCloudApi.ParseTracks(doc.RootElement).Single();

        info.Id.Should().Be("111");
        info.Title.Should().Be("Real Title");
        info.Artist.Should().Be("Some Artist");
        info.Duration.Should().Be(TimeSpan.FromMilliseconds(445982));
        info.Artwork.Should().Be(new Uri("https://i1.sndcdn.com/artworks-000066182438-aadpbh-t500x500.jpg"));
    }

    [Fact]
    public void ParseTracks_NullArtwork_FallsBackToAvatar()
    {
        using var doc = Fixture.Parse("""[{"id":5,"artwork_url":null,"user":{"username":"u","avatar_url":"https://i1.sndcdn.com/avatars-1-large.jpg"}}]""");

        SoundCloudApi.ParseTracks(doc.RootElement).Single().Artwork.Should().Be(new Uri("https://i1.sndcdn.com/avatars-1-t500x500.jpg"));
    }

    [Fact]
    public void PlaylistArtwork_PrefersOwnThenFirstTrackWithArtwork()
    {
        using var own = Fixture.Parse("""{"artwork_url":"https://x/a-large.jpg","tracks":[{"id":1,"artwork_url":"https://x/b-large.jpg"}]}""");
        using var fromTrack = Fixture.Parse("""{"artwork_url":null,"tracks":[{"id":1},{"id":2,"artwork_url":"https://x/b-large.jpg"}]}""");
        using var none = Fixture.Parse("""{"artwork_url":null,"tracks":[{"id":1}]}""");

        SoundCloudApi.PlaylistArtwork(own.RootElement).Should().Be(new Uri("https://x/a-t500x500.jpg"));
        SoundCloudApi.PlaylistArtwork(fromTrack.RootElement).Should().Be(new Uri("https://x/b-t500x500.jpg"));
        SoundCloudApi.PlaylistArtwork(none.RootElement).Should().BeNull();
    }

    [Fact]
    public void FirstLikeArtwork_UsesNewestLike()
    {
        using var doc = Fixture.Parse("""{"collection":[{"track":{"id":1,"artwork_url":"https://x/a-large.jpg"}},{"track":{"id":2,"artwork_url":"https://x/b-large.jpg"}}]}""");

        SoundCloudApi.FirstLikeArtwork(doc.RootElement).Should().Be(new Uri("https://x/a-t500x500.jpg"));
    }

    [Fact]
    public void Enrich_FillsMissingValuesAndKeepsFlatTitle()
    {
        using var doc = Fixture.Parse($"[{TrackJson}]");
        var infos = SoundCloudApi.ParseTracks(doc.RootElement);
        var tracks = new[]
        {
            new SourceTrack(SourceIds.SoundCloud, "111", "Flat title", null, "Set", null, null),
            new SourceTrack(SourceIds.SoundCloud, "222", "Other", null, "Set", null, null)
        };

        var result = SoundCloudApi.Enrich(tracks, infos);

        result[0].Title.Should().Be("Flat title");
        result[0].Artist.Should().Be("Some Artist");
        result[0].Duration.Should().Be(TimeSpan.FromMilliseconds(445982));
        result[0].ArtworkUri.Should().NotBeNull();
        result[1].Should().Be(tracks[1]);
    }

    [Fact]
    public void Enrich_PlaceholderTitle_IsReplaced()
    {
        using var doc = Fixture.Parse($"[{TrackJson}]");
        var tracks = new[] { new SourceTrack(SourceIds.SoundCloud, "111", "SoundCloud track 111", null, null, null, null) };

        SoundCloudApi.Enrich(tracks, SoundCloudApi.ParseTracks(doc.RootElement))[0].Title.Should().Be("Real Title");
    }

    [Fact]
    public void ParseHistory_ReadsTracksAndNextHref()
    {
        using var doc = Fixture.Parse($$"""{"collection":[{"played_at":1,"track_id":111,"track":{{TrackJson}}},{"played_at":2,"track_id":9}],"next_href":"https://api-v2.soundcloud.com/me/play-history/tracks?offset=1"}""");

        var (tracks, next) = SoundCloudApi.ParseHistory(doc.RootElement);

        tracks.Should().ContainSingle().Which.Id.Should().Be("111");
        next.Should().Be("https://api-v2.soundcloud.com/me/play-history/tracks?offset=1");
    }

    [Fact]
    public void ToSourceTracks_KeepsFirstOccurrenceOfDuplicates()
    {
        var infos = new[]
        {
            new SoundCloudTrackInfo("1", "New", "A", null, null),
            new SoundCloudTrackInfo("2", null, null, null, null),
            new SoundCloudTrackInfo("1", "Old", "A", null, null)
        };

        var tracks = SoundCloudApi.ToSourceTracks(infos, "History");

        tracks.Select(t => t.Title).Should().Equal("New", "SoundCloud track 2");
        tracks.Should().OnlyContain(t => t.Album == "History");
    }

    [Fact]
    public void DurationOf_ReadsSecondsAndIgnoresLiveOrMissing()
    {
        using var track = Fixture.Load("soundcloud-track-hls.json");
        using var live = Fixture.Parse("""{"duration":120,"is_live":true}""");
        using var zero = Fixture.Parse("""{"duration":0}""");

        AudioFormatSelector.DurationOf(track.RootElement).Should().Be(TimeSpan.FromSeconds(445.982));
        AudioFormatSelector.DurationOf(live.RootElement).Should().BeNull();
        AudioFormatSelector.DurationOf(zero.RootElement).Should().BeNull();
        AudioFormatSelector.Select(track.RootElement)!.Stream.Duration.Should().Be(TimeSpan.FromSeconds(445.982));
    }
}
