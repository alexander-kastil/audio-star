using System.Text.Json.Nodes;
using AudioStar.Core;
using Microsoft.Extensions.Logging;

namespace AudioStar.Devices.Groups;

internal sealed class GroupService(ISpeakerHub hub, ILogger<GroupService> logger) : IGroupService
{
    private const int VerifyAttempts = 10;

    public TimeSpan VerifyInterval { get; init; } = TimeSpan.FromMilliseconds(600);

    public async Task<IReadOnlyList<SpeakerGroup>> GetActiveGroupsAsync(CancellationToken cancellationToken = default)
    {
        var leaders = hub.Speakers.Where(s => s.FollowerIds.Count > 0).ToList();
        var groups = new List<SpeakerGroup>();
        foreach (var leader in leaders)
        {
            var members = new List<GroupMember> { ToMember(leader, true) };
            foreach (var followerId in leader.FollowerIds)
            {
                if (hub.Find(followerId) is { } follower)
                {
                    members.Add(ToMember(follower, false));
                }
            }

            var (groupId, name) = await ResolveGroupAsync(leader, cancellationToken);
            groups.Add(new SpeakerGroup(leader.Info.Id, groupId, name ?? $"{leader.Info.Name} +{leader.FollowerIds.Count}", members));
        }

        return groups;
    }

    public async Task<IReadOnlyList<SavedGroup>> GetSavedGroupsAsync(string leaderId, CancellationToken cancellationToken = default)
    {
        var leader = Require(leaderId);
        var list = await ReadListAsync(leader, cancellationToken);
        return list.Records.Select(r => ToSaved(leaderId, r, list.CurrentGroupId)).ToList();
    }

    public async Task<SavedGroup> SaveGroupAsync(string leaderId, string name, IReadOnlyList<string> memberIds, string? groupId = null, CancellationToken cancellationToken = default)
    {
        var leader = Require(leaderId);
        var list = await ReadListAsync(leader, cancellationToken);
        var records = list.Records.ToList();
        var existingIndex = groupId is null ? -1 : records.FindIndex(r => GroupRecords.GroupId(r) == groupId);
        var existing = existingIndex >= 0 ? records[existingIndex] : null;
        var slaves = BuildSlaves(leaderId, memberIds, existing);
        var updateTime = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        JsonObject record;
        if (existing is not null)
        {
            record = GroupRecords.Update(existing, name, updateTime, slaves);
            records[existingIndex] = record;
        }
        else
        {
            record = GroupRecords.Create(groupId ?? Guid.NewGuid().ToString("N"), name, updateTime, slaves);
            records.Insert(0, record);
        }

        await PostAsync(leader, "multiroom:savenamegrouplist", GroupRecords.SerializeList(records), cancellationToken);
        return ToSaved(leaderId, record, list.CurrentGroupId);
    }

    public async Task DeleteSavedGroupAsync(string leaderId, string groupId, CancellationToken cancellationToken = default)
    {
        var leader = Require(leaderId);
        var list = await ReadListAsync(leader, cancellationToken);
        var remaining = list.Records.Where(r => GroupRecords.GroupId(r) != groupId).ToList();
        await PostAsync(leader, "multiroom:savenamegrouplist", GroupRecords.SerializeList(remaining), cancellationToken);
    }

    public async Task ActivateGroupAsync(string leaderId, string groupId, CancellationToken cancellationToken = default)
    {
        var leader = Require(leaderId);
        var list = await ReadListAsync(leader, cancellationToken);
        var record = list.Records.FirstOrDefault(r => GroupRecords.GroupId(r) == groupId)
            ?? throw new InvalidOperationException($"Saved group {groupId} does not exist on {leader.Info.Name}.");
        var payload = GroupRecords.ActivationPayload(record, uuid => hub.Find(uuid)?.Info.IpAddress);
        await PostAsync(leader, "multiroom:setcurrentnamegroup", payload, cancellationToken);
        var expected = GroupRecords.Slaves(record).Select(s => s.Uuid).Where(u => hub.Find(u) is not null);
        await VerifyMembershipAsync(leader, expected, cancellationToken);
    }

    public async Task DeactivateGroupAsync(string leaderId, CancellationToken cancellationToken = default)
    {
        var leader = Require(leaderId);
        await PostAsync(leader, "multiroom:setcurrentnamegroup", GroupRecords.DeactivationPayload(), cancellationToken);
    }

    public async Task UngroupAsync(string leaderId, CancellationToken cancellationToken = default)
    {
        var leader = Require(leaderId);
        var reply = await leader.Controller.SendCommandAsync("multiroom:Ungroup", cancellationToken);
        if (SpeakerReply.IsFailure(reply))
        {
            throw new InvalidOperationException($"{leader.Info.Name} rejected multiroom:Ungroup: {reply}");
        }

        await VerifyMembershipAsync(leader, [], cancellationToken);
    }

    public async Task SetGroupVolumeAsync(string leaderId, int volume, CancellationToken cancellationToken = default)
    {
        var leader = Require(leaderId);
        var tasks = new List<Task> { leader.Controller.SetVolumeAsync(Clamp(volume), cancellationToken) };
        foreach (var followerId in leader.FollowerIds)
        {
            tasks.Add(SetFollowerVolumeAsync(leader, followerId, volume, cancellationToken));
        }

        await Task.WhenAll(tasks);
    }

    public Task SetMemberVolumeAsync(string leaderId, string memberId, int volume, CancellationToken cancellationToken = default)
    {
        var leader = Require(leaderId);
        return string.Equals(leaderId, memberId, StringComparison.OrdinalIgnoreCase)
            ? leader.Controller.SetVolumeAsync(Clamp(volume), cancellationToken)
            : SetFollowerVolumeAsync(leader, memberId, volume, cancellationToken);
    }

    public Task SetMemberMuteAsync(string memberId, bool muted, CancellationToken cancellationToken = default)
    {
        return Require(memberId).Controller.SetMuteAsync(muted, cancellationToken);
    }

    private async Task SetFollowerVolumeAsync(ISpeakerSession leader, string followerId, int volume, CancellationToken cancellationToken)
    {
        var follower = Require(followerId);
        var command = $"multiroom:SlaveVolume:{follower.Info.IpAddress}:{Clamp(volume)}";
        var reply = await leader.Controller.SendCommandAsync(command, cancellationToken);
        if (SpeakerReply.IsFailure(reply))
        {
            logger.LogWarning("{Leader} rejected {Command}: {Reply}", leader.Info.Name, command, reply);
        }
    }

    private async Task VerifyMembershipAsync(ISpeakerSession leader, IEnumerable<string> expectedIds, CancellationToken cancellationToken)
    {
        var expected = expectedIds.Select(id => id.ToUpperInvariant()).ToHashSet();
        for (var attempt = 0; attempt < VerifyAttempts; attempt++)
        {
            var reply = await leader.Controller.SendCommandAsync("multiroom:getSlaveList", cancellationToken);
            var actual = GroupRecords.ParseSlaveList(reply).Select(s => s.Uuid.ToUpperInvariant()).ToHashSet();
            if (actual.SetEquals(expected))
            {
                return;
            }

            await Task.Delay(VerifyInterval, cancellationToken);
        }

        throw new InvalidOperationException($"The group membership of {leader.Info.Name} did not reach the expected state.");
    }

    private async Task<(string? GroupId, string? Name)> ResolveGroupAsync(ISpeakerSession leader, CancellationToken cancellationToken)
    {
        try
        {
            var list = await ReadListAsync(leader, cancellationToken);
            if (list.CurrentGroupId.Length == 0 || list.CurrentGroupId == GroupRecords.InactiveGroupId)
            {
                return (null, null);
            }

            var record = list.Records.FirstOrDefault(r => GroupRecords.GroupId(r) == list.CurrentGroupId);
            return (list.CurrentGroupId, record is null ? null : GroupRecords.GroupName(record));
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            logger.LogDebug(ex, "Could not read the saved group list of {Leader}", leader.Info.Name);
            return (null, null);
        }
    }

    private async Task<SavedGroupList> ReadListAsync(ISpeakerSession leader, CancellationToken cancellationToken)
    {
        var reply = await leader.Controller.SendCommandAsync("multiroom:getnamegrouplist", cancellationToken);
        return GroupRecords.ParseList(reply);
    }

    private async Task PostAsync(ISpeakerSession leader, string command, string payload, CancellationToken cancellationToken)
    {
        var reply = await leader.Controller.PostCommandAsync(command, payload, cancellationToken);
        if (SpeakerReply.IsFailure(reply))
        {
            throw new InvalidOperationException($"{leader.Info.Name} rejected {command}: {reply}");
        }
    }

    private List<GroupSlave> BuildSlaves(string leaderId, IReadOnlyList<string> memberIds, JsonObject? existing)
    {
        var known = existing is null ? [] : GroupRecords.Slaves(existing).ToDictionary(s => s.Uuid, StringComparer.OrdinalIgnoreCase);
        var slaves = new List<GroupSlave>();
        foreach (var id in memberIds.Where(id => !string.Equals(id, leaderId, StringComparison.OrdinalIgnoreCase)).Distinct(StringComparer.OrdinalIgnoreCase))
        {
            if (hub.Find(id) is { } session)
            {
                slaves.Add(new GroupSlave(session.Info.Id, session.Info.Name, session.Info.IpAddress));
            }
            else if (known.TryGetValue(id, out var previous))
            {
                slaves.Add(previous);
            }
            else
            {
                throw new InvalidOperationException($"Speaker {id} is not known.");
            }
        }

        return slaves;
    }

    private static SavedGroup ToSaved(string leaderId, JsonObject record, string currentGroupId)
    {
        var id = GroupRecords.GroupId(record);
        var members = GroupRecords.Slaves(record).Select(s => s.Uuid).ToList();
        return new SavedGroup(id, GroupRecords.GroupName(record), leaderId, members, id.Length > 0 && id == currentGroupId);
    }

    private static GroupMember ToMember(ISpeakerSession session, bool isLeader)
    {
        return new GroupMember(session.Info.Id, session.Info.Name, session.Info.IpAddress, session.State.Volume, session.State.Muted, isLeader);
    }

    private ISpeakerSession Require(string speakerId)
    {
        return hub.Find(speakerId) ?? throw new InvalidOperationException($"Speaker {speakerId} is not known.");
    }

    private static int Clamp(int volume)
    {
        return Math.Clamp(volume, 0, 100);
    }
}
