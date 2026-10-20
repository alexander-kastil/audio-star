using AudioStar.Core;
using AudioStar.Library.Data;
using AudioStar.Library.Dlna;
using AudioStar.Library.HomeShare;
using FluentAssertions;
using NSubstitute;

namespace AudioStar.Library.Tests;

public class DlnaTests
{
    private static readonly Uri Base = new("http://192.168.0.10:22545/");

    private static LibraryTrack Track(long id, string title, string path = @"D:\Music\A\a.mp3") =>
        new(id, path, title, "Artist", "Artist", "Album", "Rock", (int)id, 1, 2020, TimeSpan.FromSeconds(185.5), true);

    [Fact]
    public void Build_WritesTrackItemWithResourceAndEscaping()
    {
        var item = new DidlObject("tr:1", "all", "Rock & <Roll>", false, DidlLite.TrackClass, Artist: "AC/DC", Album: "Back", TrackNumber: 3,
            Resource: new Uri("http://h:1/media/music/aa"), MimeType: "audio/flac", Duration: TimeSpan.FromSeconds(185.5));

        var xml = DidlLite.Build([item]);

        xml.Should().Contain("<item id=\"tr:1\" parentID=\"all\" restricted=\"1\">");
        xml.Should().Contain("<dc:title>Rock &amp; &lt;Roll&gt;</dc:title>");
        xml.Should().Contain("<upnp:class>object.item.audioItem.musicTrack</upnp:class>");
        xml.Should().Contain("protocolInfo=\"http-get:*:audio/flac:*\"");
        xml.Should().Contain("duration=\"0:03:05.500\"");
        xml.Should().Contain(">http://h:1/media/music/aa</res>");
    }

    [Fact]
    public void Build_WritesContainerWithChildCount()
    {
        var xml = DidlLite.Build([new DidlObject("albums", "0", "Albums", true, DidlLite.ContainerClass, 12)]);

        xml.Should().Contain("<container id=\"albums\" parentID=\"0\" restricted=\"1\" searchable=\"0\" childCount=\"12\">");
    }

    [Fact]
    public void Parse_ReadsItemsAndContainersBack()
    {
        var xml = DidlLite.Build(
        [
            new DidlObject("c1", "0", "Albums", true, DidlLite.ContainerClass, 2),
            new DidlObject("t1", "c1", "Song", false, DidlLite.TrackClass, Artist: "Band", Album: "LP", Resource: new Uri("http://h/x.mp3"), MimeType: "audio/mpeg", Duration: TimeSpan.FromSeconds(61), Artwork: new Uri("http://h/c.jpg"))
        ]);

        var items = DidlLite.Parse(xml);

        items.Should().HaveCount(2);
        items[0].Should().Match<DlnaItem>(i => i.IsContainer && i.Title == "Albums" && i.Id == "c1");
        items[1].Should().BeEquivalentTo(new DlnaItem("t1", "c1", "Song", false, "Band", "LP", new Uri("http://h/x.mp3"), new Uri("http://h/c.jpg"), TimeSpan.FromSeconds(61)));
    }

    [Theory]
    [InlineData("0:03:05.500", 185.5)]
    [InlineData("1:00:00", 3600.0)]
    [InlineData("garbage", null)]
    public void ParseDuration_HandlesUpnpFormat(string value, double? seconds)
    {
        DidlLite.ParseDuration(value)?.TotalSeconds.Should().Be(seconds);
        (DidlLite.ParseDuration(value) is null).Should().Be(seconds is null);
    }

    [Fact]
    public void Slice_PagesAndTreatsZeroCountAsAll()
    {
        var all = Enumerable.Range(0, 10).ToList();

        Paging.Slice(all, 0, 0).Should().HaveCount(10);
        Paging.Slice(all, 3, 4).Should().Equal(3, 4, 5, 6);
        Paging.Slice(all, 8, 5).Should().Equal(8, 9);
        Paging.Slice(all, 50, 5).Should().BeEmpty();
    }

    [Fact]
    public async Task Browse_RootListsFiveContainersWithPaging()
    {
        var browser = new DlnaBrowser(Substitute.For<ITrackCatalog>(), () => []);

        var all = await browser.BrowseAsync(DlnaBrowser.RootId, false, 0, 0, Base, "Audio Star", CancellationToken.None);
        var page = await browser.BrowseAsync(DlnaBrowser.RootId, false, 1, 2, Base, "Audio Star", CancellationToken.None);

        all.TotalMatches.Should().Be(5);
        all.Objects.Select(o => o.Title).Should().Equal("All tracks", "Albums", "Artists", "Genres", "Folders");
        page.NumberReturned.Should().Be(2);
        page.TotalMatches.Should().Be(5);
        page.Objects.Select(o => o.Id).Should().Equal(DlnaBrowser.AlbumsId, DlnaBrowser.ArtistsId);
    }

    [Fact]
    public async Task Browse_AllTracksPagesThroughTheCatalog()
    {
        var catalog = Substitute.For<ITrackCatalog>();
        catalog.CountTracksAsync(Arg.Any<LibraryQuery>(), Arg.Any<CancellationToken>()).Returns(250);
        catalog.GetTracksAsync(Arg.Is<LibraryQuery>(q => q.Offset == 100 && q.Limit == 50), Arg.Any<CancellationToken>())
            .Returns(Enumerable.Range(100, 50).Select(i => Track(i, $"T{i}")).ToList());
        var browser = new DlnaBrowser(catalog, () => []);

        var result = await browser.BrowseAsync(DlnaBrowser.AllId, false, 100, 50, Base, "x", CancellationToken.None);

        result.TotalMatches.Should().Be(250);
        result.NumberReturned.Should().Be(50);
        result.Objects[0].Resource.Should().Be(new Uri(Base, "media/music/" + Music.PathCodec.Encode(@"D:\Music\A\a.mp3")));
    }

    [Fact]
    public async Task Browse_AlbumChildrenAreSlicedAndTotalIsFull()
    {
        var catalog = Substitute.For<ITrackCatalog>();
        catalog.GetAlbumsAsync(null, Arg.Any<CancellationToken>()).Returns([new LibraryAlbum("Album", "Artist", 7, 2020, null)]);
        catalog.GetTracksAsync(Arg.Is<LibraryQuery>(q => q.Album == "Album" && q.Artist == "Artist"), Arg.Any<CancellationToken>())
            .Returns(Enumerable.Range(1, 7).Select(i => Track(i, $"T{i}")).ToList());
        var browser = new DlnaBrowser(catalog, () => []);
        var albums = await browser.BrowseAsync(DlnaBrowser.AlbumsId, false, 0, 0, Base, "x", CancellationToken.None);

        var result = await browser.BrowseAsync(albums.Objects[0].Id, false, 2, 3, Base, "x", CancellationToken.None);

        albums.Objects[0].ChildCount.Should().Be(7);
        result.TotalMatches.Should().Be(7);
        result.Objects.Select(o => o.Title).Should().Equal("T3", "T4", "T5");
    }

    [Fact]
    public async Task Browse_FolderGroupsSubfoldersBeforeTracks()
    {
        var catalog = Substitute.For<ITrackCatalog>();
        catalog.GetTracksUnderAsync(@"D:\Music", Arg.Any<CancellationToken>()).Returns(
        [
            Track(1, "Top", @"D:\Music\top.mp3"),
            Track(2, "Deep1", @"D:\Music\Rock\one.mp3"),
            Track(3, "Deep2", @"D:\Music\Rock\Sub\two.mp3")
        ]);
        var browser = new DlnaBrowser(catalog, () => [@"D:\Music"]);
        var roots = await browser.BrowseAsync(DlnaBrowser.FoldersId, false, 0, 0, Base, "x", CancellationToken.None);

        var result = await browser.BrowseAsync(roots.Objects[0].Id, false, 0, 0, Base, "x", CancellationToken.None);

        result.Objects.Select(o => (o.Title, o.IsContainer)).Should().Equal(("Rock", true), ("Top", false));
    }

    [Fact]
    public async Task Browse_UnknownObjectFaults701()
    {
        var browser = new DlnaBrowser(Substitute.For<ITrackCatalog>(), () => []);

        var act = () => browser.BrowseAsync("nope", false, 0, 0, Base, "x", CancellationToken.None);

        (await act.Should().ThrowAsync<DlnaFaultException>()).Which.Code.Should().Be(701);
    }

    [Fact]
    public async Task Browse_MetadataReturnsTheObjectItself()
    {
        var browser = new DlnaBrowser(Substitute.For<ITrackCatalog>(), () => []);

        var result = await browser.BrowseAsync(DlnaBrowser.RootId, true, 0, 0, Base, "My Star", CancellationToken.None);

        result.Objects.Should().ContainSingle().Which.Should().Match<DidlObject>(o => o.Title == "My Star" && o.ParentId == "-1");
        result.TotalMatches.Should().Be(1);
    }

    [Fact]
    public void Soap_ParsesBrowseRequestAndBuildsResponse()
    {
        var body = Soap.BrowseRequest(Soap.ContentDirectoryType, "albums", 5, 20);

        var request = Soap.ParseRequest(body)!;
        var response = Soap.Response("Browse", Soap.ContentDirectoryType, [new("Result", "<DIDL-Lite/>"), new("NumberReturned", "0")]);

        request.Action.Should().Be("Browse");
        request.Get("ObjectID").Should().Be("albums");
        request.GetInt("StartingIndex").Should().Be(5);
        request.GetInt("RequestedCount").Should().Be(20);
        response.Should().Contain("<u:BrowseResponse").And.Contain("&lt;DIDL-Lite/&gt;");
    }

    [Fact]
    public void Ssdp_MatchesSearchTargets()
    {
        SsdpMessages.MatchSearchTarget("ssdp:all", "uuid:1").Should().HaveCount(4);
        SsdpMessages.MatchSearchTarget("upnp:rootdevice", "uuid:1").Should().Equal("upnp:rootdevice");
        SsdpMessages.MatchSearchTarget(SsdpMessages.MediaServerType, "uuid:1").Should().Equal(SsdpMessages.MediaServerType);
        SsdpMessages.MatchSearchTarget("urn:schemas-upnp-org:device:MediaRenderer:1", "uuid:1").Should().BeEmpty();
    }

    [Fact]
    public void Ssdp_ParsesSearchAndUsesUdnOnlyUsnForDevice()
    {
        var message = SsdpMessages.Parse("M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nST: upnp:rootdevice\r\nMX: 2\r\n\r\n")!;

        SsdpMessages.IsMSearch(message).Should().BeTrue();
        message.Get("st").Should().Be("upnp:rootdevice");
        SsdpMessages.Usn("uuid:1", "uuid:1").Should().Be("uuid:1");
        SsdpMessages.Usn("uuid:1", "upnp:rootdevice").Should().Be("uuid:1::upnp:rootdevice");
    }

    [Fact]
    public void DeviceDescription_FindsContentDirectoryControlUrl()
    {
        var xml = DlnaDescriptions.Device("Audio & Star", "uuid:abc");

        var parsed = DeviceDescriptionParser.Parse(xml, new Uri("http://192.168.0.10:22545/dlna/description.xml"));

        parsed.Should().NotBeNull();
        parsed!.Udn.Should().Be("uuid:abc");
        parsed.FriendlyName.Should().Be("Audio & Star");
        parsed.ControlUri.Should().Be(new Uri("http://192.168.0.10:22545/dlna/contentdirectory/control.xml"));
    }
}
