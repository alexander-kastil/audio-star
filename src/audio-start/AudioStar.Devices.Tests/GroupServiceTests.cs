using System.Text.Json.Nodes;
using AudioStar.Core;
using AudioStar.Devices.Groups;
using FluentAssertions;
using Microsoft.Extensions.Logging.Abstractions;
using NSubstitute;

namespace AudioStar.Devices.Tests;

public class GroupServiceTests
{
    private readonly Dictionary<string, string> _leaderReplies = new()
    {
        ["multiroom:getnamegrouplist"] = """{"grouplist":[],"current_group_id":""}""",
        ["multiroom:getSlaveList"] = """{"slaves":0}""",
        ["multiroom:Ungroup"] = "OK",
        ["multiroom:SlaveVolume:192.168.0.70:30"] = "OK",
    };

    private readonly ISpeakerController _leaderController;
    private readonly ISpeakerController _followerController = Substitute.For<ISpeakerController>();
    private readonly GroupService _service;

    public GroupServiceTests()
    {
        _leaderController = Fakes.Controller(_leaderReplies);
        var leader = Fakes.Session(Fakes.Info("LEAD", "Living Room", "192.168.0.67"), _leaderController, null, "FOLL");
        var follower = Fakes.Session(Fakes.Info("FOLL", "Kitchen", "192.168.0.70"), _followerController, "LEAD");
        _service = new GroupService(Fakes.Hub(leader, follower), NullLogger<GroupService>.Instance) { VerifyInterval = TimeSpan.Zero };
    }

    [Fact]
    public async Task GetActiveGroups_lists_leader_and_followers_with_volume_and_mute()
    {
        var groups = await _service.GetActiveGroupsAsync();

        var group = groups.Should().ContainSingle().Subject;
        group.LeaderId.Should().Be("LEAD");
        group.Name.Should().Be("Living Room +1");
        group.Members.Select(m => m.SpeakerId).Should().Equal("LEAD", "FOLL");
        group.Members[0].IsLeader.Should().BeTrue();
        group.Members[1].Volume.Should().Be(40);
        group.Members[1].Muted.Should().BeTrue();
    }

    [Fact]
    public async Task SetMemberVolume_of_a_follower_goes_through_the_leader()
    {
        await _service.SetMemberVolumeAsync("LEAD", "FOLL", 30);

        await _leaderController.Received(1).SendCommandAsync("multiroom:SlaveVolume:192.168.0.70:30", Arg.Any<CancellationToken>());
        await _followerController.DidNotReceiveWithAnyArgs().SetVolumeAsync(default);
    }

    [Fact]
    public async Task SetMemberVolume_of_the_leader_uses_set_volume()
    {
        await _service.SetMemberVolumeAsync("LEAD", "LEAD", 55);

        await _leaderController.Received(1).SetVolumeAsync(55, Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task SetGroupVolume_fans_out_to_every_member()
    {
        await _service.SetGroupVolumeAsync("LEAD", 30);

        await _leaderController.Received(1).SetVolumeAsync(30, Arg.Any<CancellationToken>());
        await _leaderController.Received(1).SendCommandAsync("multiroom:SlaveVolume:192.168.0.70:30", Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task SetMemberMute_goes_to_the_member_itself()
    {
        await _service.SetMemberMuteAsync("FOLL", true);

        await _followerController.Received(1).SetMuteAsync(true, Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task SaveGroup_posts_the_new_record_first_in_the_list()
    {
        string? payload = null;
        _leaderController.PostCommandAsync("multiroom:savenamegrouplist", Arg.Do<string>(p => payload = p), Arg.Any<CancellationToken>()).Returns("OK");

        var saved = await _service.SaveGroupAsync("LEAD", "Downstairs", ["LEAD", "FOLL"]);

        saved.Name.Should().Be("Downstairs");
        saved.MemberIds.Should().Equal("FOLL");
        saved.IsActive.Should().BeFalse();
        var record = JsonNode.Parse(payload!)!["grouplist"]![0]!;
        record["group_id"]!.GetValue<string>().Should().Be(saved.GroupId);
        record["slavelist"]![0]!["ipv4"]!.GetValue<string>().Should().Be("192.168.0.70");
    }

    [Fact]
    public async Task DeleteSavedGroup_saves_the_list_without_it()
    {
        _leaderReplies["multiroom:getnamegrouplist"] = """{"grouplist":[{"group_name":"A","group_id":"g1","slavelist":[]},{"group_name":"B","group_id":"g2","slavelist":[]}],"current_group_id":""}""";
        string? payload = null;
        _leaderController.PostCommandAsync("multiroom:savenamegrouplist", Arg.Do<string>(p => payload = p), Arg.Any<CancellationToken>()).Returns("OK");

        await _service.DeleteSavedGroupAsync("LEAD", "g1");

        var list = JsonNode.Parse(payload!)!["grouplist"]!.AsArray();
        list.Should().ContainSingle();
        list[0]!["group_id"]!.GetValue<string>().Should().Be("g2");
    }

    [Fact]
    public async Task DeactivateGroup_posts_group_id_minus_one()
    {
        await _service.DeactivateGroupAsync("LEAD");

        await _leaderController.Received(1).PostCommandAsync("multiroom:setcurrentnamegroup", """{"group_id":"-1"}""", Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task ActivateGroup_posts_the_payload_and_verifies_the_slave_list()
    {
        _leaderReplies["multiroom:getnamegrouplist"] = """{"grouplist":[{"group_name":"A","group_id":"g1","slavelist":[{"name":"Kitchen","uuid":"FOLL"}]}],"current_group_id":""}""";
        _leaderReplies["multiroom:getSlaveList"] = """{"slaves":1,"slave_list":[{"uuid":"FOLL","name":"Kitchen","ip":"192.168.0.70"}]}""";

        await _service.ActivateGroupAsync("LEAD", "g1");

        await _leaderController.Received(1).PostCommandAsync(
            "multiroom:setcurrentnamegroup",
            Arg.Is<string>(p => p.Contains("\"group_id\":\"g1\"") && p.Contains("\"ipv4\":\"192.168.0.70\"")),
            Arg.Any<CancellationToken>());
    }

    [Fact]
    public async Task Ungroup_fails_when_the_slave_list_never_empties()
    {
        _leaderReplies["multiroom:getSlaveList"] = """{"slaves":1,"slave_list":[{"uuid":"FOLL"}]}""";

        var act = () => _service.UngroupAsync("LEAD");

        await act.Should().ThrowAsync<InvalidOperationException>();
    }

    [Fact]
    public async Task Ungroup_succeeds_once_the_slave_list_is_empty()
    {
        await _service.UngroupAsync("LEAD");

        await _leaderController.Received(1).SendCommandAsync("multiroom:Ungroup", Arg.Any<CancellationToken>());
    }
}
