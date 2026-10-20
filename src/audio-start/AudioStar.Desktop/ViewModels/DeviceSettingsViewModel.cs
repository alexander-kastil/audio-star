using System.Collections.ObjectModel;
using System.Globalization;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AudioStar.Desktop.ViewModels;

public sealed partial class SettingItemViewModel : ObservableObject
{
    private static readonly string[] TrueValues = ["1", "true", "on", "enable", "enabled", "yes"];

    private readonly Func<string, Task> _write;
    private readonly Func<Task> _invoke;
    private readonly IDialogService _dialogs;
    private readonly IToastService _toast;
    private readonly Debouncer _debouncer = new(TimeSpan.FromMilliseconds(350));
    private bool _loading = true;

    public SettingItemViewModel(
        DeviceSettingDefinition definition,
        string? value,
        IReadOnlyList<SettingChoice> choices,
        Func<string, Task> write,
        Func<Task> invoke,
        IDialogService dialogs,
        IToastService toast)
    {
        Definition = definition;
        _write = write;
        _invoke = invoke;
        _dialogs = dialogs;
        _toast = toast;
        Minimum = definition.Min ?? 0;
        Maximum = definition.Max ?? 100;
        switch (definition.Kind)
        {
            case SettingKind.Toggle:
                ToggleValue = value is not null && TrueValues.Contains(value.Trim(), StringComparer.OrdinalIgnoreCase);
                break;
            case SettingKind.Choice:
                foreach (var choice in choices)
                {
                    Choices.Add(choice);
                }
                if (value is not null && Choices.All(c => c.Value != value))
                {
                    Choices.Add(new SettingChoice(value, value));
                }
                SelectedChoice = Choices.FirstOrDefault(c => c.Value == value);
                break;
            case SettingKind.Number:
                NumberValue = double.TryParse(value, NumberStyles.Float, CultureInfo.InvariantCulture, out var number)
                    ? Math.Clamp(number, Minimum, Maximum)
                    : Minimum;
                break;
            case SettingKind.Text:
                TextValue = value ?? "";
                break;
        }
        _loading = false;
    }

    public DeviceSettingDefinition Definition { get; }

    public string Label => Definition.Label;

    public bool IsToggle => Definition.Kind == SettingKind.Toggle;

    public bool IsChoice => Definition.Kind == SettingKind.Choice;

    public bool IsNumber => Definition.Kind == SettingKind.Number;

    public bool IsText => Definition.Kind == SettingKind.Text;

    public bool IsAction => Definition.Kind == SettingKind.Action;

    public double Minimum { get; }

    public double Maximum { get; }

    public ObservableCollection<SettingChoice> Choices { get; } = [];

    [ObservableProperty]
    private bool _toggleValue;

    [ObservableProperty]
    private SettingChoice? _selectedChoice;

    [ObservableProperty]
    private double _numberValue;

    [ObservableProperty]
    private string _textValue = "";

    partial void OnToggleValueChanged(bool value)
    {
        if (!_loading)
        {
            _ = Guard(() => _write(value ? "1" : "0"));
        }
    }

    partial void OnSelectedChoiceChanged(SettingChoice? value)
    {
        if (!_loading && value is not null)
        {
            _ = Guard(() => _write(value.Value));
        }
    }

    partial void OnNumberValueChanged(double value)
    {
        if (!_loading)
        {
            var text = Math.Round(value).ToString(CultureInfo.InvariantCulture);
            _ = Guard(() => _debouncer.RunAsync(_ => _write(text)));
        }
    }

    [RelayCommand]
    private Task ApplyTextAsync() => Guard(() => _write(TextValue));

    [RelayCommand]
    private Task RunAsync() => Guard(async () =>
    {
        if (!string.IsNullOrWhiteSpace(Definition.ConfirmText) && !_dialogs.Confirm(Definition.ConfirmText))
        {
            return;
        }
        await _invoke();
        _toast.Show($"{Definition.Label}: done.");
    });

    private async Task Guard(Func<Task> work)
    {
        try
        {
            await work();
        }
        catch (OperationCanceledException)
        {
        }
        catch (Exception ex)
        {
            _toast.ShowError(ex);
        }
    }
}

public sealed class InputRow(AudioInput input, Func<AudioInput, Task> switchTo)
{
    public AudioInput Input { get; } = input;

    public string Title => Input.Title;

    public IAsyncRelayCommand SwitchCommand { get; } = new AsyncRelayCommand(() => switchTo(input));
}

public sealed class SettingsCategoryViewModel(string category)
{
    public string Category { get; } = category;

    public string Header { get; } = category == SettingCategories.AudioCast ? "Audio cast" : category;

    public ObservableCollection<SettingItemViewModel> Items { get; } = [];

    public ObservableCollection<InputRow> Inputs { get; } = [];

    public bool HasInputs => Inputs.Count > 0;
}

public sealed partial class DeviceSettingsViewModel : SpeakerPageViewModel
{
    private static readonly string[] Order =
    [
        SettingCategories.Device,
        SettingCategories.Network,
        SettingCategories.Sound,
        SettingCategories.Input,
        SettingCategories.Output,
        SettingCategories.Hardware,
        SettingCategories.Bluetooth,
        SettingCategories.Voice,
        SettingCategories.AudioCast
    ];

    private readonly IDeviceSettingsService _settings;
    private readonly IDialogService _dialogs;

    public DeviceSettingsViewModel(IToastService toast, ICurrentSpeaker speakers, IDeviceSettingsService settings, IDialogService dialogs)
        : base(toast, speakers)
    {
        _settings = settings;
        _dialogs = dialogs;
    }

    public override string Title => "Device settings";

    public ObservableCollection<SettingsCategoryViewModel> Categories { get; } = [];

    [ObservableProperty]
    private SettingsCategoryViewModel? _selectedCategory;

    [ObservableProperty]
    private string _speakerName = "";

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(IsEmpty))]
    private bool _loaded;

    public bool IsEmpty => Loaded && Categories.Count == 0;

    public string EmptyText => Speaker is null
        ? "Select a speaker to see its settings."
        : "This speaker returned no settings.";

    public override async Task LoadAsync()
    {
        var speaker = Speaker;
        Categories.Clear();
        SelectedCategory = null;
        SpeakerName = speaker?.Info.Name ?? "";
        OnPropertyChanged(nameof(EmptyText));
        if (speaker is null)
        {
            Loaded = true;
            OnPropertyChanged(nameof(IsEmpty));
            return;
        }
        var info = speaker.Info;
        var categories = _settings.Definitions
            .Select(d => d.Category)
            .Distinct()
            .OrderBy(c => Array.IndexOf(Order, c) is var i && i >= 0 ? i : int.MaxValue)
            .ToList();
        var loaders = categories.Select(category => LoadCategoryAsync(speaker, info, category)).ToList();
        var loaded = await Task.WhenAll(loaders);
        if (!ReferenceEquals(Speaker, speaker))
        {
            return;
        }
        foreach (var category in loaded.Where(c => c is not null && (c.Items.Count > 0 || c.Inputs.Count > 0)))
        {
            Categories.Add(category!);
        }
        SelectedCategory = Categories.FirstOrDefault();
        Loaded = true;
        OnPropertyChanged(nameof(IsEmpty));
    }

    private async Task<SettingsCategoryViewModel?> LoadCategoryAsync(ISpeakerSession speaker, SpeakerInfo info, string category)
    {
        var result = new SettingsCategoryViewModel(category);
        try
        {
            var values = await _settings.ReadAsync(info, category);
            var definitions = _settings.Definitions.Where(d => d.Category == category).ToList();
            foreach (var definition in definitions)
            {
                if (!values.TryGetValue(definition.Key, out var value))
                {
                    continue;
                }
                var choices = await ResolveChoicesAsync(info, definition);
                result.Items.Add(Create(info, definition, value, choices));
            }
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            Toast.ShowError($"Could not read {result.Header} settings: {ex.Message}");
        }
        if (category == SettingCategories.Input)
        {
            await LoadInputsAsync(speaker, result);
        }
        return result;
    }

    private async Task LoadInputsAsync(ISpeakerSession speaker, SettingsCategoryViewModel category)
    {
        try
        {
            var inputs = await speaker.Controller.GetInputsAsync();
            foreach (var input in inputs)
            {
                category.Inputs.Add(new InputRow(input, async selected =>
                {
                    try
                    {
                        await speaker.Controller.SwitchInputAsync(selected.Mode);
                        Toast.Show($"Switched to {selected.Title}.");
                    }
                    catch (Exception ex) when (ex is not OperationCanceledException)
                    {
                        Toast.ShowError(ex);
                    }
                }));
            }
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            Toast.ShowError($"Could not read the inputs: {ex.Message}");
        }
    }

    private async Task<IReadOnlyList<SettingChoice>> ResolveChoicesAsync(SpeakerInfo info, DeviceSettingDefinition definition)
    {
        if (definition.Kind != SettingKind.Choice)
        {
            return [];
        }
        if (!definition.DynamicChoices)
        {
            return definition.Choices ?? [];
        }
        try
        {
            return await _settings.GetChoicesAsync(info, definition.Key);
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            Toast.ShowError($"Could not load the choices for {definition.Label}: {ex.Message}");
            return definition.Choices ?? [];
        }
    }

    private SettingItemViewModel Create(SpeakerInfo info, DeviceSettingDefinition definition, string? value, IReadOnlyList<SettingChoice> choices) =>
        new(
            definition,
            value,
            choices,
            text => _settings.WriteAsync(info, definition.Key, text),
            () => _settings.InvokeAsync(info, definition.Key),
            _dialogs,
            Toast);
}
