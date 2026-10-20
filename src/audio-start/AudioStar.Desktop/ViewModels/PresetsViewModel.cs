using System.Collections.ObjectModel;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AudioStar.Desktop.ViewModels;

public sealed class PresetRow(Preset preset)
{
    public Preset Preset { get; } = preset;

    public int Number => Preset.Number;

    public bool IsEmpty => Preset.IsEmpty;

    public bool HasContent => !Preset.IsEmpty;

    public string Name => Preset.IsEmpty ? "Empty" : string.IsNullOrWhiteSpace(Preset.Name) ? $"Preset {Preset.Number}" : Preset.Name;

    public string? Source => Preset.IsEmpty ? null : Preset.Source;

    public Uri? PictureUri => Preset.PictureUri;
}

public sealed partial class PresetsViewModel(IToastService toast, ICurrentSpeaker speakers, IDialogService dialogs)
    : SpeakerPageViewModel(toast, speakers)
{
    public override string Title => "Presets";

    public ObservableCollection<PresetRow> Rows { get; } = [];

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(IsEmpty))]
    private bool _loaded;

    public bool IsEmpty => Loaded && Rows.Count == 0;

    public override async Task LoadAsync()
    {
        Rows.Clear();
        if (Speaker is not null)
        {
            var presets = await Speaker.Controller.GetPresetsAsync();
            foreach (var preset in presets.OrderBy(p => p.Number))
            {
                Rows.Add(new PresetRow(preset));
            }
        }
        Loaded = true;
        OnPropertyChanged(nameof(IsEmpty));
    }

    [RelayCommand]
    private Task PlayAsync(PresetRow? row) => row is null || Speaker is null
        ? Task.CompletedTask
        : GuardAsync(() => Speaker.Controller.PlayPresetAsync(row.Number));

    [RelayCommand]
    private Task SaveCurrentAsync(PresetRow? row) => row is null || Speaker is null
        ? Task.CompletedTask
        : GuardAsync(async () =>
        {
            if (!row.IsEmpty && !dialogs.Confirm($"Replace preset {row.Number} with what is playing now?"))
            {
                return;
            }
            await Speaker.Controller.SaveCurrentAsPresetAsync(row.Number);
            await LoadAsync();
        });

    [RelayCommand]
    private Task DeleteAsync(PresetRow? row) => row is null || Speaker is null
        ? Task.CompletedTask
        : GuardAsync(async () =>
        {
            if (!dialogs.Confirm($"Delete preset {row.Number}?"))
            {
                return;
            }
            await Speaker.Controller.DeletePresetAsync(row.Number);
            await LoadAsync();
        });
}
