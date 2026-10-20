using AudioStar.Sources.Radio;
using FluentAssertions;

namespace AudioStar.Sources.Tests;

public class RadioMapperTests
{
    [Fact]
    public void MapStations_FromCapturedRadioBrowserReply_MapsFields()
    {
        using var doc = Fixture.Load("radio-stations-at.json");

        var stations = RadioMapper.MapStations(doc.RootElement);

        stations.Should().HaveCount(3);
        var first = stations[0];
        first.Id.Should().Be("e723f7f8-0db1-4bc5-a64c-64d8377f9f9a");
        first.Name.Should().Be("ORF Hitradio Ö3 | HQ");
        first.StreamUri.Should().Be(new Uri("https://orf-live.ors-shoutcast.at/oe3-q2a"));
        first.LogoUri.Should().NotBeNull();
        first.CountryCode.Should().Be("AT");
        first.Country.Should().Be("Austria");
        first.Tags.Should().Equal("orf", "pop");
        first.Bitrate.Should().Be(192);
        first.Codec.Should().Be("MP3");
    }

    [Fact]
    public void MapStation_PrefersResolvedUrlAndFallsBackToUrl()
    {
        using var doc = Fixture.Parse("""
            [{"stationuuid":"1","name":" A ","url":"http://x/raw","url_resolved":"http://x/resolved","bitrate":0,"favicon":"","tags":""},
             {"stationuuid":"2","name":"B","url":"http://x/raw2","url_resolved":""}]
            """);

        var stations = RadioMapper.MapStations(doc.RootElement);

        stations[0].Name.Should().Be("A");
        stations[0].StreamUri.Should().Be(new Uri("http://x/resolved"));
        stations[0].Bitrate.Should().BeNull();
        stations[0].LogoUri.Should().BeNull();
        stations[0].Tags.Should().BeEmpty();
        stations[1].StreamUri.Should().Be(new Uri("http://x/raw2"));
    }

    [Fact]
    public void MapStations_SkipsStationsWithoutUsableStreamOrName()
    {
        using var doc = Fixture.Parse("""
            [{"stationuuid":"1","name":"No stream","url":"","url_resolved":""},
             {"stationuuid":"2","name":"","url":"http://x/a"},
             {"stationuuid":"3","name":"Bad scheme","url":"rtmp://x/a"}]
            """);

        RadioMapper.MapStations(doc.RootElement).Should().BeEmpty();
    }

    [Fact]
    public void MapServerNames_DeduplicatesHostnames()
    {
        using var doc = Fixture.Parse("""[{"ip":"1.2.3.4","name":"de1.api.radio-browser.info"},{"ip":"::1","name":"de1.api.radio-browser.info"},{"name":"fi1.api.radio-browser.info"}]""");

        RadioMapper.MapServerNames(doc.RootElement).Should().Equal("de1.api.radio-browser.info", "fi1.api.radio-browser.info");
    }
}
