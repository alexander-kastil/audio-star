using AudioStar.Core;
using Microsoft.Extensions.Logging;

namespace AudioStar.Devices.Settings;

internal sealed class DeviceSettingsService(ISpeakerHub hub, ILogger<DeviceSettingsService> logger) : IDeviceSettingsService
{
    private readonly IReadOnlyList<SettingSpec> _specs = SettingsCatalog.Build();

    private IReadOnlyList<DeviceSettingDefinition>? _definitions;

    public IReadOnlyList<DeviceSettingDefinition> Definitions => _definitions ??= _specs.Select(s => s.Definition).ToList();

    public async Task<IReadOnlyDictionary<string, string?>> ReadAsync(SpeakerInfo speaker, string category, CancellationToken cancellationToken = default)
    {
        var execution = Execution(speaker, cancellationToken);
        var specs = _specs.Where(s => s.Definition.Category == category).ToList();
        var commands = specs
            .SelectMany(s => new[] { s.ReadCommand, s.GateCommand })
            .Where(c => c is not null)
            .Select(c => c!)
            .Distinct()
            .ToList();
        var replies = new Dictionary<string, string?>();
        foreach (var batch in await Task.WhenAll(commands.Select(c => FetchAsync(execution, c))))
        {
            replies[batch.Command] = batch.Reply;
        }

        var result = new Dictionary<string, string?>();
        foreach (var spec in specs)
        {
            if (spec.GateCommand is not null && !SettingParsers.GateAccepts(replies[spec.GateCommand]))
            {
                continue;
            }

            if (spec.ReadCommand is null)
            {
                result[spec.Definition.Key] = null;
                continue;
            }

            var reply = replies[spec.ReadCommand];
            if (SpeakerReply.IsFailure(reply))
            {
                continue;
            }

            var value = spec.Parse!(reply!);
            if (value is not null)
            {
                result[spec.Definition.Key] = spec.Definition.Kind == SettingKind.Action ? null : value;
            }
        }

        return result;
    }

    public async Task<IReadOnlyList<SettingChoice>> GetChoicesAsync(SpeakerInfo speaker, string key, CancellationToken cancellationToken = default)
    {
        var spec = Find(key);
        if (spec.Choices is null)
        {
            return spec.Definition.Choices ?? [];
        }

        return await spec.Choices(Execution(speaker, cancellationToken));
    }

    public Task WriteAsync(SpeakerInfo speaker, string key, string value, CancellationToken cancellationToken = default)
    {
        var spec = Find(key);
        if (spec.Definition.Kind == SettingKind.Action || spec.Execute is null)
        {
            throw new InvalidOperationException($"Setting {key} cannot be written.");
        }

        return spec.Execute(Execution(speaker, cancellationToken), value);
    }

    public Task InvokeAsync(SpeakerInfo speaker, string key, string? argument = null, CancellationToken cancellationToken = default)
    {
        var spec = Find(key);
        if (spec.Definition.Kind != SettingKind.Action || spec.Execute is null)
        {
            throw new InvalidOperationException($"Setting {key} is not an action.");
        }

        return spec.Execute(Execution(speaker, cancellationToken), argument);
    }

    private async Task<(string Command, string? Reply)> FetchAsync(SettingExecution execution, string command)
    {
        try
        {
            return (command, await execution.Controller.SendCommandAsync(command, execution.CancellationToken));
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            logger.LogDebug(ex, "{Speaker} does not answer {Command}", execution.Speaker.Name, command);
            return (command, null);
        }
    }

    private SettingExecution Execution(SpeakerInfo speaker, CancellationToken cancellationToken)
    {
        var session = hub.Find(speaker.Id) ?? throw new InvalidOperationException($"Speaker {speaker.Name} is not connected.");
        return new SettingExecution(speaker, session.Controller, cancellationToken);
    }

    private SettingSpec Find(string key)
    {
        return _specs.FirstOrDefault(s => s.Definition.Key == key) ?? throw new KeyNotFoundException($"Unknown setting {key}.");
    }
}
