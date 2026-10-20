using AudioStar.Desktop.Services;

namespace AudioStar.Desktop.ViewModels;

public sealed class NowPlayingViewModel(IToastService toast, PlayerViewModel player) : PageViewModel(toast)
{
    public override string Title => "Now playing";

    public PlayerViewModel Player { get; } = player;
}
