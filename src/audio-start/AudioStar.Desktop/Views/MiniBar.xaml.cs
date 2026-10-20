using System.Windows.Controls;
using System.Windows.Input;
using AudioStar.Desktop.ViewModels;

namespace AudioStar.Desktop.Views;

public partial class MiniBar : UserControl
{
    public MiniBar()
    {
        InitializeComponent();
        SeekSlider.PreviewMouseLeftButtonDown += (_, _) => (DataContext as PlayerViewModel)?.BeginSeek();
        SeekSlider.AddHandler(PreviewMouseLeftButtonUpEvent, new MouseButtonEventHandler(OnSeekReleased), true);
        SeekSlider.LostMouseCapture += OnSeekCaptureLost;
    }

    private async void OnSeekReleased(object sender, MouseButtonEventArgs e)
    {
        if (DataContext is PlayerViewModel player && player.IsSeeking)
        {
            await System.Windows.Threading.Dispatcher.Yield();
            await player.CommitSeekAsync(SeekSlider.Value);
        }
    }

    private void OnSeekCaptureLost(object sender, MouseEventArgs e)
    {
        if (DataContext is PlayerViewModel { IsSeeking: true } player && Mouse.LeftButton == MouseButtonState.Released)
        {
            _ = player.CommitSeekAsync(SeekSlider.Value);
        }
    }
}
