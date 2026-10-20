using System.Windows;
using AudioStar.Desktop.ViewModels;
using AudioStar.Desktop.Views;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Win32;

namespace AudioStar.Desktop.Services;

public interface IDialogService
{
    bool Confirm(string message, string title = "Audio Star");
    string? PickFolder();
    Task ShowGroupEditorAsync(string? leaderId);
    string? ShowPlaylistSettings(string title, string url);
}

public sealed class DialogService(IServiceProvider services) : IDialogService
{
    private static Window? Owner => Application.Current.MainWindow is { IsVisible: true } window ? window : null;

    public bool Confirm(string message, string title = "Audio Star")
    {
        var result = Owner is { } owner
            ? MessageBox.Show(owner, message, title, MessageBoxButton.OKCancel, MessageBoxImage.Question)
            : MessageBox.Show(message, title, MessageBoxButton.OKCancel, MessageBoxImage.Question);
        return result == MessageBoxResult.OK;
    }

    public string? PickFolder()
    {
        var dialog = new OpenFolderDialog { Title = "Choose a music folder" };
        var accepted = Owner is { } owner ? dialog.ShowDialog(owner) : dialog.ShowDialog();
        return accepted == true ? dialog.FolderName : null;
    }

    public async Task ShowGroupEditorAsync(string? leaderId)
    {
        var viewModel = services.GetRequiredService<GroupEditorViewModel>();
        await viewModel.LoadAsync(leaderId);
        var window = new GroupEditorWindow { DataContext = viewModel, Owner = Owner };
        window.ShowDialog();
        viewModel.Dispose();
    }

    public string? ShowPlaylistSettings(string title, string url)
    {
        var viewModel = new PlaylistSettingsViewModel(title, url);
        var window = new PlaylistSettingsWindow { DataContext = viewModel, Owner = Owner };
        return window.ShowDialog() == true ? viewModel.Url : null;
    }
}
