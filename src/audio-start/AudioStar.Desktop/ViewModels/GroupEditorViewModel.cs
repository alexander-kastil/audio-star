using System.Collections.ObjectModel;
using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AudioStar.Desktop.ViewModels;

public sealed partial class MemberChoice(ISpeakerSession session) : ObservableObject
{
    public ISpeakerSession Session { get; } = session;

    public string Name => Session.Info.Name;

    [ObservableProperty]
    private bool _isSelected;
}

public sealed partial class GroupEditorViewModel(
    ICurrentSpeaker speakers,
    IGroupService groups,
    IToastService toast,
    IDialogService dialogs) : ObservableObject, IDisposable
{
    private bool _loading;

    public ObservableCollection<ISpeakerSession> Leaders => speakers.Speakers;

    public ObservableCollection<SavedGroup> SavedGroups { get; } = [];

    public ObservableCollection<MemberChoice> Candidates { get; } = [];

    public ObservableCollection<MemberVolumeViewModel> ActiveMembers { get; } = [];

    [ObservableProperty]
    private ISpeakerSession? _selectedLeader;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(HasSavedSelection))]
    private SavedGroup? _selectedSaved;

    [ObservableProperty]
    private string _groupName = "";

    [ObservableProperty]
    private string _activeSummary = "No active group";

    [ObservableProperty]
    private bool _isBusy;

    public bool HasSavedSelection => SelectedSaved is not null;

    public bool NoActiveMembers => ActiveMembers.Count == 0;

    public async Task LoadAsync(string? leaderId)
    {
        _loading = true;
        SelectedLeader = speakers.Speakers.FirstOrDefault(s => s.Info.Id == leaderId)
            ?? speakers.Current
            ?? speakers.Speakers.FirstOrDefault();
        _loading = false;
        await RefreshAsync(null);
    }

    partial void OnSelectedLeaderChanged(ISpeakerSession? value)
    {
        if (!_loading)
        {
            _ = Guard(() => RefreshAsync(null));
        }
    }

    partial void OnSelectedSavedChanged(SavedGroup? value)
    {
        if (_loading)
        {
            return;
        }
        ApplySaved(value);
    }

    private void ApplySaved(SavedGroup? saved)
    {
        GroupName = saved?.Name ?? "";
        foreach (var candidate in Candidates)
        {
            candidate.IsSelected = saved is not null && saved.MemberIds.Contains(candidate.Session.Info.Id);
        }
    }

    private async Task RefreshAsync(string? selectGroupId)
    {
        var leader = SelectedLeader;
        _loading = true;
        try
        {
            SavedGroups.Clear();
            Candidates.Clear();
            ActiveMembers.Clear();
            ActiveSummary = "No active group";
            if (leader is null)
            {
                return;
            }
            foreach (var session in speakers.Speakers.Where(s => s.Info.Id != leader.Info.Id))
            {
                Candidates.Add(new MemberChoice(session));
            }
            var saved = await groups.GetSavedGroupsAsync(leader.Info.Id);
            foreach (var group in saved)
            {
                SavedGroups.Add(group);
            }
            var active = (await groups.GetActiveGroupsAsync()).FirstOrDefault(g => g.LeaderId == leader.Info.Id && g.Members.Count > 1);
            if (active is not null)
            {
                ActiveSummary = string.IsNullOrWhiteSpace(active.Name) ? "Active group" : $"Active group: {active.Name}";
                foreach (var member in active.Members)
                {
                    ActiveMembers.Add(new MemberVolumeViewModel(leader.Info.Id, member, groups, toast));
                }
            }
            SelectedSaved = SavedGroups.FirstOrDefault(g => g.GroupId == selectGroupId)
                ?? (selectGroupId is null ? SavedGroups.FirstOrDefault(g => g.IsActive) : null);
            ApplySaved(SelectedSaved);
        }
        finally
        {
            _loading = false;
            OnPropertyChanged(nameof(NoActiveMembers));
        }
    }

    [RelayCommand]
    private void NewGroup()
    {
        SelectedSaved = null;
        ApplySaved(null);
    }

    [RelayCommand]
    private Task SaveAsync() => Busy(async () =>
    {
        var leader = SelectedLeader ?? throw new InvalidOperationException("Pick a leader speaker.");
        var name = GroupName.Trim();
        if (name.Length == 0)
        {
            throw new InvalidOperationException("Enter a group name.");
        }
        var members = Candidates.Where(c => c.IsSelected).Select(c => c.Session.Info.Id).ToList();
        if (members.Count == 0)
        {
            throw new InvalidOperationException("Pick at least one member.");
        }
        var saved = await groups.SaveGroupAsync(leader.Info.Id, name, members, SelectedSaved?.GroupId);
        await RefreshAsync(saved.GroupId);
        toast.Show($"Saved group {saved.Name}.");
    });

    [RelayCommand]
    private Task ActivateAsync() => Busy(async () =>
    {
        var leader = SelectedLeader ?? throw new InvalidOperationException("Pick a leader speaker.");
        var saved = SelectedSaved ?? throw new InvalidOperationException("Select a saved group to activate.");
        await groups.ActivateGroupAsync(leader.Info.Id, saved.GroupId);
        await RefreshAsync(saved.GroupId);
    });

    [RelayCommand]
    private Task UngroupAsync() => Busy(async () =>
    {
        var leader = SelectedLeader ?? throw new InvalidOperationException("Pick a leader speaker.");
        await groups.UngroupAsync(leader.Info.Id);
        await RefreshAsync(SelectedSaved?.GroupId);
    });

    [RelayCommand]
    private Task DeleteAsync() => Busy(async () =>
    {
        var leader = SelectedLeader ?? throw new InvalidOperationException("Pick a leader speaker.");
        var saved = SelectedSaved ?? throw new InvalidOperationException("Select a saved group to delete.");
        if (!dialogs.Confirm($"Delete the saved group {saved.Name}?"))
        {
            return;
        }
        await groups.DeleteSavedGroupAsync(leader.Info.Id, saved.GroupId);
        await RefreshAsync(null);
    });

    private async Task Busy(Func<Task> work)
    {
        IsBusy = true;
        try
        {
            await Guard(work);
        }
        finally
        {
            IsBusy = false;
        }
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
            toast.ShowError(ex);
        }
    }

    public void Dispose()
    {
    }
}
