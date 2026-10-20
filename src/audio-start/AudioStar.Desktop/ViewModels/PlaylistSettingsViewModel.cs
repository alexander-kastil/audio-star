using CommunityToolkit.Mvvm.ComponentModel;

namespace AudioStar.Desktop.ViewModels;

public sealed partial class PlaylistSettingsViewModel(string title, string url) : ObservableObject
{
    public string Title { get; } = title;

    [ObservableProperty]
    private string _url = url;
}
