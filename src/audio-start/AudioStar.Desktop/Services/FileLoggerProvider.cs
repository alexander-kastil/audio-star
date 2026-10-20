using AudioStar.Core;
using Microsoft.Extensions.Logging;

namespace AudioStar.Desktop.Services;

public sealed class FileLoggerProvider : ILoggerProvider
{
    private readonly object _gate = new();

    public ILogger CreateLogger(string categoryName) => new FileLogger(categoryName, this);

    private void Write(string line)
    {
        try
        {
            lock (_gate)
            {
                Directory.CreateDirectory(AppPaths.LogDirectory);
                File.AppendAllText(Path.Combine(AppPaths.LogDirectory, $"audiostar-{DateTime.Now:yyyyMMdd}.log"), line + Environment.NewLine);
            }
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
        {
        }
    }

    public void Dispose()
    {
    }

    private sealed class FileLogger(string category, FileLoggerProvider provider) : ILogger
    {
        public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;

        public bool IsEnabled(LogLevel logLevel) => logLevel >= LogLevel.Information;

        public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, Exception? exception, Func<TState, Exception?, string> formatter)
        {
            if (!IsEnabled(logLevel))
            {
                return;
            }
            var line = $"{DateTime.Now:HH:mm:ss.fff} {logLevel,-11} {category}: {formatter(state, exception)}";
            if (exception is not null)
            {
                line += Environment.NewLine + exception;
            }
            provider.Write(line);
        }
    }
}
