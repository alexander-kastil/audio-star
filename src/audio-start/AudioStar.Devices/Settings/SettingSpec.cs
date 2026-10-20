using AudioStar.Core;

namespace AudioStar.Devices.Settings;

internal sealed record SettingExecution(SpeakerInfo Speaker, ISpeakerController Controller, CancellationToken CancellationToken)
{
    public async Task<string> SendAsync(string command)
    {
        var reply = await Controller.SendCommandAsync(command, CancellationToken);
        if (SpeakerReply.IsFailure(reply))
        {
            throw new InvalidOperationException($"{Speaker.Name} rejected {command.Split(':')[0]}: {reply}");
        }

        return reply;
    }
}

internal delegate Task SettingExecutor(SettingExecution execution, string? value);

internal delegate Task<IReadOnlyList<SettingChoice>> SettingChoiceSource(SettingExecution execution);

internal sealed record SettingSpec(
    DeviceSettingDefinition Definition,
    string? ReadCommand = null,
    Func<string, string?>? Parse = null,
    string? GateCommand = null,
    SettingExecutor? Execute = null,
    SettingChoiceSource? Choices = null);
