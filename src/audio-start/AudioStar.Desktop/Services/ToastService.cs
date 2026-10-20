using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace AudioStar.Desktop.Services;

public sealed partial class ToastItem(string message, bool isError, Action<ToastItem> dismiss) : ObservableObject
{
    public string Message { get; } = message;

    public bool IsError { get; } = isError;

    [RelayCommand]
    private void Dismiss() => dismiss(this);
}

public interface IToastService
{
    ObservableCollection<ToastItem> Toasts { get; }
    void Show(string message);
    void ShowError(string message);
    void ShowError(Exception exception);
}

public sealed class ToastService(IUiDispatcher dispatcher, Microsoft.Extensions.Logging.ILogger<ToastService> logger) : IToastService
{
    private static readonly TimeSpan Lifetime = TimeSpan.FromSeconds(7);
    private const int MaxVisible = 4;

    public ObservableCollection<ToastItem> Toasts { get; } = [];

    public void Show(string message) => Add(message, false);

    public void ShowError(string message) => Add(message, true);

    public void ShowError(Exception exception)
    {
        Microsoft.Extensions.Logging.LoggerExtensions.LogWarning(logger, exception, "Shown to the user: {Message}", Describe(exception));
        Add(Describe(exception), true);
    }

    private static string Describe(Exception exception)
    {
        var inner = exception is AggregateException aggregate && aggregate.InnerExceptions.Count > 0
            ? aggregate.InnerExceptions[0]
            : exception;
        return string.IsNullOrWhiteSpace(inner.Message) ? inner.GetType().Name : inner.Message;
    }

    private void Add(string message, bool isError)
    {
        dispatcher.Post(() =>
        {
            if (Toasts.Any(t => t.Message == message))
            {
                return;
            }
            var toast = new ToastItem(message, isError, Remove);
            Toasts.Add(toast);
            while (Toasts.Count > MaxVisible)
            {
                Toasts.RemoveAt(0);
            }
            _ = ExpireAsync(toast);
        });
    }

    private async Task ExpireAsync(ToastItem toast)
    {
        await Task.Delay(Lifetime);
        dispatcher.Post(() => Remove(toast));
    }

    private void Remove(ToastItem toast) => Toasts.Remove(toast);
}
