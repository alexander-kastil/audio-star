using System.Text.Json.Nodes;
using AudioStar.Devices.Groups;
using FluentAssertions;

namespace AudioStar.Devices.Tests;

public class GroupRecordsTests
{
    private static readonly GroupSlave[] Slaves =
    [
        new("AAA111", "Kitchen", "192.168.0.70"),
        new("BBB222", "Office", null),
    ];

    [Fact]
    public void Create_writes_the_record_shape_of_wiim_home()
    {
        var record = GroupRecords.Create("g1", "Downstairs", 1760000000, Slaves);

        record["group_name"]!.GetValue<string>().Should().Be("Downstairs");
        record["fullName"]!.GetValue<string>().Should().Be("Downstairs");
        record["group_id"]!.GetValue<string>().Should().Be("g1");
        record["group_type"]!.GetValue<int>().Should().Be(0);
        record["update_time"]!.GetValue<string>().Should().Be("1760000000");
        record["channel"]!.GetValue<int>().Should().Be(0);
        var slaves = record["slavelist"]!.AsArray();
        slaves.Should().HaveCount(2);
        slaves[0]!["uuid"]!.GetValue<string>().Should().Be("AAA111");
        slaves[0]!["name"]!.GetValue<string>().Should().Be("Kitchen");
        slaves[0]!["ipv4"]!.GetValue<string>().Should().Be("192.168.0.70");
        slaves[1]!.AsObject().ContainsKey("ipv4").Should().BeFalse();
    }

    [Fact]
    public void Update_keeps_unknown_keys_of_the_device()
    {
        var existing = JsonNode.Parse("""{"group_name":"Old","group_id":"g1","vendor_flag":7,"slavelist":[]}""")!.AsObject();

        var record = GroupRecords.Update(existing, "New", 5, Slaves);

        record["vendor_flag"]!.GetValue<int>().Should().Be(7);
        record["group_name"]!.GetValue<string>().Should().Be("New");
        existing["group_name"]!.GetValue<string>().Should().Be("Old");
    }

    [Fact]
    public void SerializeList_wraps_records_in_grouplist()
    {
        var json = GroupRecords.SerializeList([GroupRecords.Create("g1", "A", 1, Slaves)]);

        var root = JsonNode.Parse(json)!.AsObject();
        root["grouplist"]!.AsArray().Should().HaveCount(1);
        root.Count.Should().Be(1);
    }

    [Fact]
    public void SerializeList_of_nothing_is_an_empty_list()
    {
        GroupRecords.SerializeList([]).Should().Be("""{"grouplist":[]}""");
    }

    [Fact]
    public void ActivationPayload_excludes_the_master_and_prefers_the_live_ip()
    {
        var record = GroupRecords.Create("g1", "Downstairs", 1, Slaves);

        var payload = JsonNode.Parse(GroupRecords.ActivationPayload(record, uuid => uuid == "BBB222" ? "192.168.0.71" : null))!;

        payload["group_id"]!.GetValue<string>().Should().Be("g1");
        payload["group_name"]!.GetValue<string>().Should().Be("Downstairs");
        payload["fullName"]!.GetValue<string>().Should().Be("Downstairs");
        var slaves = payload["slavelist"]!.AsArray();
        slaves[0]!["uuid"]!.GetValue<string>().Should().Be("AAA111");
        slaves[0]!["ipv4"]!.GetValue<string>().Should().Be("192.168.0.70");
        slaves[1]!["ipv4"]!.GetValue<string>().Should().Be("192.168.0.71");
        slaves[0]!.AsObject().ContainsKey("name").Should().BeFalse();
    }

    [Fact]
    public void DeactivationPayload_is_group_id_minus_one()
    {
        GroupRecords.DeactivationPayload().Should().Be("""{"group_id":"-1"}""");
    }

    [Fact]
    public void ParseList_reads_the_live_empty_reply()
    {
        var list = GroupRecords.ParseList("""{ "grouplist": [ ], "current_group_id": "" }""");

        list.Records.Should().BeEmpty();
        list.CurrentGroupId.Should().BeEmpty();
    }

    [Fact]
    public void ParseList_reads_records_and_current_group()
    {
        var reply = """{"grouplist":[{"group_name":"A","group_id":"g1","slavelist":[{"name":"K","uuid":"AAA111","ipv4":"192.168.0.70"}]}],"current_group_id":"g1"}""";

        var list = GroupRecords.ParseList(reply);

        list.CurrentGroupId.Should().Be("g1");
        GroupRecords.GroupId(list.Records[0]).Should().Be("g1");
        GroupRecords.Slaves(list.Records[0]).Should().ContainSingle().Which.Uuid.Should().Be("AAA111");
    }

    [Theory]
    [InlineData("Failed")]
    [InlineData("")]
    [InlineData("not json")]
    public void ParseList_tolerates_failures(string reply)
    {
        GroupRecords.ParseList(reply).Records.Should().BeEmpty();
    }

    [Fact]
    public void ParseSlaveList_reads_the_live_empty_reply()
    {
        GroupRecords.ParseSlaveList("""{ "slaves": 0, "wmrm_version": "4.3", "surround": 0, "group_type": -1 }""").Should().BeEmpty();
    }

    [Fact]
    public void ParseSlaveList_reads_slave_entries()
    {
        var reply = """{"slaves":2,"wmrm_version":"4.3","slave_list":[{"name":"Kitchen","uuid":"AAA111","ip":"192.168.0.70","volume":35,"mute":"0"},{"name":"Office","uuid":"BBB222","ip":"192.168.0.71","volume":"20","mute":"1"}]}""";

        var slaves = GroupRecords.ParseSlaveList(reply);

        slaves.Should().HaveCount(2);
        slaves[0].Should().Be(new SlaveStatus("AAA111", "Kitchen", "192.168.0.70", 35, false));
        slaves[1].Should().Be(new SlaveStatus("BBB222", "Office", "192.168.0.71", 20, true));
    }
}
