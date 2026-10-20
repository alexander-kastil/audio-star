using System.Text.Json;
using AudioStar.Core;
using AudioStar.Library.Data;
using AudioStar.Library.Recent;
using FluentAssertions;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.DependencyInjection;
using NSubstitute;

namespace AudioStar.Library.Tests;

public sealed class RecentlyPlayedTests : IDisposable
{
    private readonly string _path = Path.Combine(Path.GetTempPath(), $"audiostar-recent-{Guid.NewGuid():N}.db");
    private readonly ServiceCollection _services = new();

    private RecentlyPlayed Create() => new(new Database(_path), _services.BuildServiceProvider());

    public void Dispose()
    {
        SqliteConnection.ClearAllPools();
        foreach (var file in Directory.GetFiles(Path.GetDirectoryName(_path)!, Path.GetFileName(_path) + "*"))
        {
            File.Delete(file);
        }
    }

    [Fact]
    public async Task AddAsync_DeduplicatesByKindSourceAndTitle()
    {
        var recent = Create();

        await recent.AddAsync(RecentKinds.Request, "library", "Album A", null, null, "{}");
        await recent.AddAsync(RecentKinds.Request, "library", "Album B", null, null, "{}");
        await recent.AddAsync(RecentKinds.Request, "library", "Album A", "again", null, "{\"x\":1}");
        await recent.AddAsync(RecentKinds.SourcePlaylist, "library", "Album A", null, null, "{}");

        var items = await recent.GetAsync();

        items.Should().HaveCount(3);
        items.Select(i => (i.Kind, i.Title)).Should().Equal((RecentKinds.SourcePlaylist, "Album A"), (RecentKinds.Request, "Album A"), (RecentKinds.Request, "Album B"));
        items[1].Subtitle.Should().Be("again");
        items[1].PayloadJson.Should().Be("{\"x\":1}");
    }

    [Fact]
    public async Task AddAsync_TrimsToTwoHundred()
    {
        var recent = Create();

        for (var i = 0; i < RecentlyPlayed.MaxItems + 15; i++)
        {
            await recent.AddAsync(RecentKinds.Request, "library", $"Title {i}", null, null, "{}");
        }

        var items = await recent.GetAsync(1000);
        items.Should().HaveCount(RecentlyPlayed.MaxItems);
        items[0].Title.Should().Be($"Title {RecentlyPlayed.MaxItems + 14}");
        items.Select(i => i.Title).Should().NotContain("Title 0");
    }

    [Fact]
    public async Task RemoveAsync_DeletesTheRow()
    {
        var recent = Create();
        await recent.AddAsync(RecentKinds.Request, "library", "One", null, new Uri("http://x/c.jpg"), "{}");
        var item = (await recent.GetAsync()).Single();

        await recent.RemoveAsync(item.Id);

        item.ArtworkUri.Should().Be(new Uri("http://x/c.jpg"));
        (await recent.GetAsync()).Should().BeEmpty();
    }

    [Fact]
    public async Task ReplayAsync_RequestKindPlaysTheRequestOnTheSpeaker()
    {
        var recent = Create();
        var request = new PlayRequest("List", "Library", [new PlayItem("1", "Song", "Artist", "Album", new Uri("http://h/a.mp3"), null, TimeSpan.FromSeconds(10))], 0);
        var speaker = Substitute.For<ISpeakerSession>();
        var controller = Substitute.For<ISpeakerController>();
        speaker.Controller.Returns(controller);
        var item = new RecentItem(1, RecentKinds.Request, "library", "List", null, null, DateTimeOffset.UtcNow, JsonSerializer.Serialize(request));

        await recent.ReplayAsync(speaker, item);

        await controller.Received(1).PlayAsync(Arg.Is<PlayRequest>(r => r.ListName == "List" && r.Items.Count == 1 && r.Items[0].StreamUri == new Uri("http://h/a.mp3")), Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task ReplayAsync_SourcePlaylistKindUsesTheMatchingSource()
    {
        var other = Substitute.For<IMusicSource>();
        other.Id.Returns(SourceIds.Spotify);
        var youtube = Substitute.For<IMusicSource>();
        youtube.Id.Returns(SourceIds.YouTube);
        _services.AddSingleton(other);
        _services.AddSingleton(youtube);
        var recent = Create();
        var playlist = new SourcePlaylist(SourceIds.YouTube, "pl1", "Mix", null, 3, null, null);
        var speaker = Substitute.For<ISpeakerSession>();
        var item = new RecentItem(1, RecentKinds.SourcePlaylist, SourceIds.YouTube, "Mix", null, null, DateTimeOffset.UtcNow, JsonSerializer.Serialize(playlist));

        await recent.ReplayAsync(speaker, item);

        await youtube.Received(1).PlayAsync(speaker, Arg.Is<SourcePlaylist>(p => p.Id == "pl1"), 0, Arg.Any<CancellationToken>());
        await other.DidNotReceiveWithAnyArgs().PlayAsync(default!, default!, default, default);
    }

    [Fact]
    public async Task ReplayAsync_UnknownSourceThrows()
    {
        var recent = Create();
        var playlist = new SourcePlaylist(SourceIds.YouTube, "pl1", "Mix", null, null, null, null);
        var item = new RecentItem(1, RecentKinds.SourcePlaylist, SourceIds.YouTube, "Mix", null, null, DateTimeOffset.UtcNow, JsonSerializer.Serialize(playlist));

        var act = () => recent.ReplayAsync(Substitute.For<ISpeakerSession>(), item);

        await act.Should().ThrowAsync<InvalidOperationException>();
    }
}
