using System.Text.Json.Nodes;

namespace AudioStar.Devices.Groups;

internal sealed record GroupSlave(string Uuid, string Name, string? Ip);

internal sealed record SlaveStatus(string Uuid, string Name, string? Ip, int? Volume, bool? Muted);

internal sealed record SavedGroupList(IReadOnlyList<JsonObject> Records, string CurrentGroupId);

internal static class GroupRecords
{
    public const string InactiveGroupId = "-1";

    public static JsonObject Create(string groupId, string name, long updateTime, IEnumerable<GroupSlave> slaves)
    {
        var record = new JsonObject
        {
            ["group_name"] = name,
            ["fullName"] = name,
            ["group_id"] = groupId,
            ["group_type"] = 0,
            ["update_time"] = updateTime.ToString(System.Globalization.CultureInfo.InvariantCulture),
            ["channel"] = 0,
        };
        record["slavelist"] = SlaveArray(slaves);
        return record;
    }

    public static JsonObject Update(JsonObject existing, string name, long updateTime, IEnumerable<GroupSlave> slaves)
    {
        var record = (JsonObject)existing.DeepClone();
        record["group_name"] = name;
        record["fullName"] = name;
        record["update_time"] = updateTime.ToString(System.Globalization.CultureInfo.InvariantCulture);
        record["slavelist"] = SlaveArray(slaves);
        return record;
    }

    public static string SerializeList(IEnumerable<JsonObject> records)
    {
        var list = new JsonArray();
        foreach (var record in records)
        {
            list.Add(record.DeepClone());
        }

        return new JsonObject { ["grouplist"] = list }.ToJsonString();
    }

    public static string ActivationPayload(JsonObject record, Func<string, string?> resolveIp)
    {
        var name = GroupName(record);
        var slaves = new JsonArray();
        foreach (var slave in Slaves(record))
        {
            var entry = new JsonObject { ["uuid"] = slave.Uuid };
            var ip = resolveIp(slave.Uuid) ?? slave.Ip;
            if (!string.IsNullOrEmpty(ip))
            {
                entry["ipv4"] = ip;
            }

            slaves.Add(entry);
        }

        return new JsonObject
        {
            ["group_id"] = GroupId(record),
            ["group_name"] = name,
            ["fullName"] = Text(record, "fullName") ?? Text(record, "full_name") ?? Text(record, "groupFullName") ?? name,
            ["slavelist"] = slaves,
        }.ToJsonString();
    }

    public static string DeactivationPayload()
    {
        return new JsonObject { ["group_id"] = InactiveGroupId }.ToJsonString();
    }

    public static SavedGroupList ParseList(string? reply)
    {
        var root = SpeakerReply.TryParse(reply) as JsonObject;
        var records = new List<JsonObject>();
        if (root?["grouplist"] is JsonArray array)
        {
            records.AddRange(array.OfType<JsonObject>());
        }

        var current = SpeakerReply.Scalar(root?["current_group_id"]) ?? string.Empty;
        return new SavedGroupList(records, current);
    }

    public static string GroupId(JsonObject record)
    {
        return Text(record, "group_id") ?? string.Empty;
    }

    public static string GroupName(JsonObject record)
    {
        return Text(record, "group_name") ?? Text(record, "fullName") ?? string.Empty;
    }

    public static IReadOnlyList<GroupSlave> Slaves(JsonObject record)
    {
        var result = new List<GroupSlave>();
        if (record["slavelist"] is not JsonArray array)
        {
            return result;
        }

        foreach (var node in array.OfType<JsonObject>())
        {
            var uuid = Text(node, "uuid");
            if (string.IsNullOrEmpty(uuid))
            {
                continue;
            }

            result.Add(new GroupSlave(uuid, Text(node, "name") ?? string.Empty, Text(node, "ipv4") ?? Text(node, "ip")));
        }

        return result;
    }

    public static IReadOnlyList<SlaveStatus> ParseSlaveList(string? reply)
    {
        var result = new List<SlaveStatus>();
        var root = SpeakerReply.TryParse(reply) as JsonObject;
        if (root?["slave_list"] is not JsonArray array)
        {
            return result;
        }

        foreach (var node in array.OfType<JsonObject>())
        {
            var uuid = Text(node, "uuid");
            if (string.IsNullOrEmpty(uuid))
            {
                continue;
            }

            var volume = Text(node, "volume") ?? Text(node, "vol");
            var mute = Text(node, "mute");
            result.Add(new SlaveStatus(
                uuid,
                Text(node, "name") ?? string.Empty,
                Text(node, "ip") ?? Text(node, "ipv4"),
                int.TryParse(volume, out var parsedVolume) ? parsedVolume : null,
                mute is null ? null : mute != "0"));
        }

        return result;
    }

    private static JsonArray SlaveArray(IEnumerable<GroupSlave> slaves)
    {
        var array = new JsonArray();
        foreach (var slave in slaves)
        {
            var entry = new JsonObject { ["name"] = slave.Name, ["uuid"] = slave.Uuid };
            if (!string.IsNullOrEmpty(slave.Ip))
            {
                entry["ipv4"] = slave.Ip;
            }

            array.Add(entry);
        }

        return array;
    }

    private static string? Text(JsonObject node, string key)
    {
        return SpeakerReply.Scalar(node[key]);
    }
}
