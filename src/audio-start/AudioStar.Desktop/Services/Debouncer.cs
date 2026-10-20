namespace AudioStar.Desktop.Services;

public sealed class Debouncer(TimeSpan delay)
{
    private CancellationTokenSource? _cts;

    public async Task RunAsync(Func<CancellationToken, Task> action)
    {
        _cts?.Cancel();
        var cts = new CancellationTokenSource();
        _cts = cts;
        try
        {
            await Task.Delay(delay, cts.Token);
            await action(cts.Token);
        }
        catch (OperationCanceledException) when (cts.IsCancellationRequested)
        {
        }
    }

    public void Cancel() => _cts?.Cancel();
}
