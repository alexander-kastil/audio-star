using AudioStar.Core;
using AudioStar.Desktop.Services;
using CommunityToolkit.Mvvm.ComponentModel;

namespace AudioStar.Desktop.ViewModels;

public abstract partial class PageViewModel(IToastService toast) : ObservableObject, IDisposable
{
    [ObservableProperty]
    private bool _isBusy;

    public abstract string Title { get; }

    protected IToastService Toast => toast;

    public virtual Task LoadAsync() => Task.CompletedTask;

    public Task InitializeAsync() => LoadGuardedAsync(LoadAsync);

    protected async Task GuardAsync(Func<Task> work)
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

    protected async Task LoadGuardedAsync(Func<Task> work)
    {
        IsBusy = true;
        try
        {
            await GuardAsync(work);
        }
        finally
        {
            IsBusy = false;
        }
    }

    public virtual void Dispose()
    {
    }
}

public abstract class SpeakerPageViewModel : PageViewModel
{
    protected SpeakerPageViewModel(IToastService toast, ICurrentSpeaker speakers) : base(toast)
    {
        Speakers = speakers;
        speakers.CurrentChanged += OnSpeakerChanged;
    }

    protected ICurrentSpeaker Speakers { get; }

    protected ISpeakerSession? Speaker => Speakers.Current;

    protected virtual void OnSpeakerSwitched()
    {
        _ = InitializeAsync();
    }

    private void OnSpeakerChanged(object? sender, EventArgs e) => OnSpeakerSwitched();

    public override void Dispose()
    {
        Speakers.CurrentChanged -= OnSpeakerChanged;
        base.Dispose();
    }
}
