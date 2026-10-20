using AudioStar.Core;
using AudioStar.Sources.YouTube;
using FluentAssertions;

namespace AudioStar.Sources.Tests;

public class YouTubeMapperTests
{
    [Fact]
    public void MapTracks_FromCapturedPlaylist_MapsFlatEntries()
    {
        using var doc = Fixture.Load("youtube-playlist-flat.json");

        var tracks = YouTubeMapper.MapTracks(doc.RootElement);

        tracks.Should().HaveCount(4);
        tracks[0].SourceId.Should().Be(SourceIds.YouTube);
        tracks[0].Id.Should().Be("kPa7bsKwL-c");
        tracks[0].Title.Should().Contain("Die With A Smile");
        tracks[0].Artist.Should().Be("Lady Gaga");
        tracks[0].Duration.Should().Be(TimeSpan.FromSeconds(253));
        tracks[0].ArtworkUri.Should().Be(new Uri("https://i.ytimg.com/vi/kPa7bsKwL-c/hqdefault.jpg"));
    }

    [Fact]
    public void MapTracks_SkipsPrivateAndDeletedEntries()
    {
        using var doc = Fixture.Parse("""
            {"entries":[
              {"id":"aaaaaaaaaaa","title":"[Private video]"},
              {"id":"bbbbbbbbbbb","title":"[Deleted video]"},
              {"id":"ccccccccccc","title":"Hidden","availability":"private"},
              {"id":"ddddddddddd","title":"Kept","duration":61.5},
              {"title":"No id"}
            ]}
            """);

        var tracks = YouTubeMapper.MapTracks(doc.RootElement);

        tracks.Should().ContainSingle().Which.Id.Should().Be("ddddddddddd");
    }

    [Fact]
    public void MapLibrary_MapsPlaylistFeedEntries()
    {
        using var doc = Fixture.Parse("""
            {"entries":[
              {"_type":"url","ie_key":"YoutubeTab","id":"PLabcdefghijklmnop","title":"Morning","url":"https://www.youtube.com/playlist?list=PLabcdefghijklmnop","playlist_count":12,"thumbnails":[{"url":"https://i.ytimg.com/vi/x/hq.jpg"}]},
              {"_type":"url","id":"LL","title":"Liked videos","url":"https://www.youtube.com/playlist?list=LL"},
              {"id":"zzz","title":"Not a list","url":"https://www.youtube.com/watch?v=zzz"}
            ]}
            """);

        var playlists = YouTubeMapper.MapLibrary(doc.RootElement);

        playlists.Should().HaveCount(2);
        playlists[0].Id.Should().Be("https://www.youtube.com/playlist?list=PLabcdefghijklmnop");
        playlists[0].Title.Should().Be("Morning");
        playlists[0].TrackCount.Should().Be(12);
        playlists[0].ArtworkUri.Should().NotBeNull();
        playlists[1].Id.Should().Be("https://www.youtube.com/playlist?list=LL");
    }

    [Fact]
    public void MapPlaylistHeader_UsesTitleCountAndFirstVideoArtwork()
    {
        using var doc = Fixture.Parse("""{"id":"PL1","title":"Mix","playlist_count":182,"uploader":"Music","entries":[{"id":"vid12345678","title":"x"}]}""");

        var playlist = YouTubeMapper.MapPlaylistHeader(doc.RootElement, "https://www.youtube.com/playlist?list=PL1");

        playlist.Title.Should().Be("Mix");
        playlist.Owner.Should().Be("Music");
        playlist.TrackCount.Should().Be(182);
        playlist.ArtworkUri.Should().Be(new Uri("https://i.ytimg.com/vi/vid12345678/hqdefault.jpg"));
    }

    [Theory]
    [InlineData("https://www.youtube.com/playlist?list=PL123", "https://www.youtube.com/playlist?list=PL123")]
    [InlineData("https://www.youtube.com/watch?v=abc&list=PL123&index=4", "https://www.youtube.com/playlist?list=PL123")]
    [InlineData("https://music.youtube.com/playlist?list=PL123", "https://www.youtube.com/playlist?list=PL123")]
    [InlineData("https://www.youtube.com/watch?v=abc", null)]
    [InlineData("https://example.com/playlist?list=PL123", null)]
    [InlineData("not a url", null)]
    public void NormalizePlaylistUrl_AcceptsOnlyYouTubePlaylistLinks(string input, string? expected)
    {
        YouTubeMapper.NormalizePlaylistUrl(input).Should().Be(expected);
    }
}
