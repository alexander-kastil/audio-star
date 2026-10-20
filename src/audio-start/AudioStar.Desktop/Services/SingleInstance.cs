using System.IO.Pipes;

namespace AudioStar.Desktop.Services;

public sealed class SingleInstance : IDisposable
{
    private const string MutexName = @"Local\AudioStar.SingleInstance";
    private const string PipeName = "AudioStar.Activate";

    private readonly CancellationTokenSource _cts = new();
    private Mutex? _mutex;

    public bool TryAcquire()
    {
        _mutex = new Mutex(true, MutexName, out var created);
        if (!created)
        {
            _mutex.Dispose();
            _mutex = null;
        }
        return created;
    }

    public static void SignalExisting()
    {
        try
        {
            using var client = new NamedPipeClientStream(".", PipeName, PipeDirection.Out);
            client.Connect(3000);
            client.WriteByte(1);
            client.Flush();
        }
        catch (Exception ex) when (ex is TimeoutException or IOException)
        {
        }
    }

    public void ListenForActivation(Action onActivate)
    {
        _ = Task.Run(async () =>
        {
            while (!_cts.IsCancellationRequested)
            {
                try
                {
                    await using var server = new NamedPipeServerStream(PipeName, PipeDirection.In, 1, PipeTransmissionMode.Byte, PipeOptions.Asynchronous);
                    await server.WaitForConnectionAsync(_cts.Token);
                    var buffer = new byte[1];
                    await server.ReadExactlyAsync(buffer, _cts.Token);
                    onActivate();
                }
                catch (OperationCanceledException)
                {
                    return;
                }
                catch (IOException)
                {
                    await Task.Delay(250);
                }
            }
        });
    }

    public void Dispose()
    {
        _cts.Cancel();
        _cts.Dispose();
        _mutex?.Dispose();
    }
}
