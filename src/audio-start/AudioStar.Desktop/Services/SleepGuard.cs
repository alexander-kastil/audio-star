using System.Runtime.InteropServices;
using AudioStar.Core;

namespace AudioStar.Desktop.Services;

public sealed class SleepGuard(ISettingsStore settings, IUiDispatcher dispatcher) : IDisposable
{
    private const uint EsContinuous = 0x80000000;
    private const uint EsSystemRequired = 0x00000001;

    [DllImport("kernel32.dll")]
    private static extern uint SetThreadExecutionState(uint flags);

    public void Start()
    {
        settings.Changed += OnSettingsChanged;
        Apply();
    }

    private void OnSettingsChanged(object? sender, EventArgs e) => dispatcher.Post(Apply);

    private void Apply() =>
        SetThreadExecutionState(settings.Current.PreventSleep ? EsContinuous | EsSystemRequired : EsContinuous);

    public void Dispose()
    {
        settings.Changed -= OnSettingsChanged;
        SetThreadExecutionState(EsContinuous);
    }
}
