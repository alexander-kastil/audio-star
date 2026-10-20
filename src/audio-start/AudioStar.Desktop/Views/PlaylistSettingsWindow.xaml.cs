using System.Windows;

namespace AudioStar.Desktop.Views;

public partial class PlaylistSettingsWindow : Window
{
    public PlaylistSettingsWindow()
    {
        InitializeComponent();
    }

    private void Save_Click(object sender, RoutedEventArgs e) => DialogResult = true;
}
