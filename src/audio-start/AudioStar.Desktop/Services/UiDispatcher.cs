using System.Windows;
using System.Windows.Threading;

namespace AudioStar.Desktop.Services;

public interface IUiDispatcher
{
    bool CheckAccess();
    void Post(Action action);
    Task InvokeAsync(Action action);
}

public sealed class UiDispatcher : IUiDispatcher
{
    private Dispatcher Dispatcher => Application.Current.Dispatcher;

    public bool CheckAccess() => Dispatcher.CheckAccess();

    public void Post(Action action)
    {
        if (Dispatcher.HasShutdownStarted)
        {
            return;
        }
        Dispatcher.BeginInvoke(action);
    }

    public Task InvokeAsync(Action action)
    {
        if (Dispatcher.CheckAccess())
        {
            action();
            return Task.CompletedTask;
        }
        return Dispatcher.InvokeAsync(action).Task;
    }
}
