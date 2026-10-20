using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AudioStar.Desktop.ViewModels;

public sealed partial class MemberVolumeViewModel : ObservableObject
{
    private readonly string _leaderId;
    private readonly IGroupService _groups;
    private readonly IToastService _toast;
    private readonly Debouncer _debouncer = new(TimeSpan.FromMilliseconds(180));
    private bool _applying;

    public MemberVolumeViewModel(string leaderId, GroupMember member, IGroupService groups, IToastService toast)
    {
        _leaderId = leaderId;
        _groups = groups;
        _toast = toast;
        MemberId = member.SpeakerId;
        Name = member.IsLeader ? $"{member.Name} (leader)" : member.Name;
        _applying = true;
        Volume = member.Volume;
        Muted = member.Muted;
        _applying = false;
    }

    public string MemberId { get; }

    public string Name { get; }

    [ObservableProperty]
    private double _volume;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(MuteGlyph))]
    private bool _muted;

    public string MuteGlyph => Muted ? "" : "";

    partial void OnVolumeChanged(double value)
    {
        if (_applying)
        {
            return;
        }
        var level = (int)Math.Round(value);
        _ = Guard(() => _debouncer.RunAsync(token => _groups.SetMemberVolumeAsync(_leaderId, MemberId, level, token)));
    }

    [RelayCommand]
    private async Task ToggleMuteAsync()
    {
        var target = !Muted;
        await _groups.SetMemberMuteAsync(MemberId, target);
        Muted = target;
    }

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
