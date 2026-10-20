using AudioStar.Core;
using Forms = System.Windows.Forms;

namespace AudioStar.Desktop.Services;

public sealed class TrayService : IDisposable
{
    private const string Name = "Audio Star";
    private const int MaxTooltipLength = 63;

    private readonly ICurrentSpeaker _speakers;
    private readonly IUiDispatcher _dispatcher;
    private readonly IToastService _toast;
    private readonly Forms.NotifyIcon _icon;
    private readonly System.Drawing.Icon _image;
    private readonly Forms.ToolStripMenuItem _playItem;
    private ISpeakerSession? _observed;

    public TrayService(Action open, Action settings, Action quit, ICurrentSpeaker speakers, IUiDispatcher dispatcher, IToastService toast)
    {
        _speakers = speakers;
        _dispatcher = dispatcher;
        _toast = toast;

        _playItem = new Forms.ToolStripMenuItem("Play", null, async (_, _) => await TogglePlaybackAsync());
        var autostartItem = new Forms.ToolStripMenuItem("Start with Windows (minimized)")
        {
            CheckOnClick = true,
            Checked = Autostart.IsEnabled
        };
        autostartItem.CheckedChanged += (_, _) => Autostart.SetEnabled(autostartItem.Checked);

        var menu = new Forms.ContextMenuStrip();
        menu.Items.Add("Open", null, (_, _) => open());
        menu.Items.Add(_playItem);
        menu.Items.Add(autostartItem);
        menu.Items.Add("Settings...", null, (_, _) => settings());
        menu.Items.Add(new Forms.ToolStripSeparator());
        menu.Items.Add("Quit", null, (_, _) => quit());
        menu.Opening += (_, _) =>
        {
            var state = _speakers.Current?.State.State;
            _playItem.Text = IsPlaying(state) ? "Pause" : "Play";
            _playItem.Enabled = _speakers.Current is not null;
            autostartItem.Checked = Autostart.IsEnabled;
        };

        _image = AppIcon.CreateIcon();
        _icon = new Forms.NotifyIcon
        {
            Icon = _image,
            Text = Name,
            ContextMenuStrip = menu,
            Visible = true
        };
        _icon.MouseClick += (_, e) =>
        {
            if (e.Button == Forms.MouseButtons.Left)
            {
                open();
            }
        };

        _speakers.CurrentChanged += OnCurrentChanged;
        Observe(_speakers.Current);
    }

    private static bool IsPlaying(TransportState? state) => state is TransportState.Playing or TransportState.Transitioning;

    private async Task TogglePlaybackAsync()
    {
        var speaker = _speakers.Current;
        if (speaker is null)
        {
            return;
        }
        try
        {
            if (IsPlaying(speaker.State.State))
            {
                await speaker.Controller.PauseAsync();
            }
            else
            {
                await speaker.Controller.PlayAsync();
            }
        }
        catch (Exception ex)
        {
            _toast.ShowError(ex);
        }
    }

    private void OnCurrentChanged(object? sender, EventArgs e) => _dispatcher.Post(() => Observe(_speakers.Current));

    private void Observe(ISpeakerSession? speaker)
    {
        if (_observed is not null)
        {
            _observed.StateChanged -= OnStateChanged;
        }
        _observed = speaker;
        if (_observed is not null)
        {
            _observed.StateChanged += OnStateChanged;
        }
        UpdateTooltip(speaker?.State);
    }

    private void OnStateChanged(object? sender, PlaybackState state) => _dispatcher.Post(() => UpdateTooltip(state));

    private void UpdateTooltip(PlaybackState? state)
    {
        var title = state?.Track?.Title;
        var text = IsPlaying(state?.State) && !string.IsNullOrWhiteSpace(title) ? $"{Name}: {title}" : Name;
        _icon.Text = text.Length > MaxTooltipLength ? text[..MaxTooltipLength] : text;
    }

    public void Dispose()
    {
        _speakers.CurrentChanged -= OnCurrentChanged;
        if (_observed is not null)
        {
            _observed.StateChanged -= OnStateChanged;
        }
        _icon.Visible = false;
        _icon.Dispose();
        _image.Dispose();
    }
}
