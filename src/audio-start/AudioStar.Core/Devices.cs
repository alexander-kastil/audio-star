namespace AudioStar.Core;

public sealed record GroupMember(string SpeakerId, string Name, string IpAddress, int Volume, bool Muted, bool IsLeader);

public sealed record SpeakerGroup(string LeaderId, string? GroupId, string Name, IReadOnlyList<GroupMember> Members);

public sealed record SavedGroup(string GroupId, string Name, string LeaderId, IReadOnlyList<string> MemberIds, bool IsActive);

public interface IGroupService
{
    Task<IReadOnlyList<SpeakerGroup>> GetActiveGroupsAsync(CancellationToken cancellationToken = default);
    Task<IReadOnlyList<SavedGroup>> GetSavedGroupsAsync(string leaderId, CancellationToken cancellationToken = default);
    Task<SavedGroup> SaveGroupAsync(string leaderId, string name, IReadOnlyList<string> memberIds, string? groupId = null, CancellationToken cancellationToken = default);
    Task DeleteSavedGroupAsync(string leaderId, string groupId, CancellationToken cancellationToken = default);
    Task ActivateGroupAsync(string leaderId, string groupId, CancellationToken cancellationToken = default);
    Task DeactivateGroupAsync(string leaderId, CancellationToken cancellationToken = default);
    Task UngroupAsync(string leaderId, CancellationToken cancellationToken = default);
    Task SetGroupVolumeAsync(string leaderId, int volume, CancellationToken cancellationToken = default);
    Task SetMemberVolumeAsync(string leaderId, string memberId, int volume, CancellationToken cancellationToken = default);
    Task SetMemberMuteAsync(string memberId, bool muted, CancellationToken cancellationToken = default);
}

public static class SettingCategories
{
    public const string Device = "Device";
    public const string Network = "Network";
    public const string Sound = "Sound";
    public const string Input = "Input";
    public const string Output = "Output";
    public const string Hardware = "Hardware";
    public const string Bluetooth = "Bluetooth";
    public const string Voice = "Voice";
    public const string AudioCast = "AudioCast";
}

public enum SettingKind { Toggle, Choice, Number, Text, Action }

public sealed record SettingChoice(string Value, string Label);

public sealed record DeviceSettingDefinition(
    string Key,
    string Category,
    string Label,
    SettingKind Kind,
    IReadOnlyList<SettingChoice>? Choices = null,
    int? Min = null,
    int? Max = null,
    string? ConfirmText = null,
    bool DynamicChoices = false);

public interface IDeviceSettingsService
{
    IReadOnlyList<DeviceSettingDefinition> Definitions { get; }
    Task<IReadOnlyDictionary<string, string?>> ReadAsync(SpeakerInfo speaker, string category, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<SettingChoice>> GetChoicesAsync(SpeakerInfo speaker, string key, CancellationToken cancellationToken = default);
    Task WriteAsync(SpeakerInfo speaker, string key, string value, CancellationToken cancellationToken = default);
    Task InvokeAsync(SpeakerInfo speaker, string key, string? argument = null, CancellationToken cancellationToken = default);
}
