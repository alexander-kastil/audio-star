using System.Collections.Concurrent;

namespace AudioStar.Speakers.Events;

internal sealed class SpeakerEventRouter
{
    private const int PendingLimit = 20;
    private static readonly TimeSpan PendingLifetime = TimeSpan.FromSeconds(10);

    private readonly ConcurrentDictionary<string, Action<string>> _handlers = new(StringComparer.OrdinalIgnoreCase);
    private readonly ConcurrentDictionary<string, List<(DateTime At, string Body)>> _pending = new(StringComparer.OrdinalIgnoreCase);

    public void Register(string sid, Action<string> handler)
    {
        _handlers[sid] = handler;
        if (_pending.TryRemove(sid, out var buffered))
        {
            List<(DateTime At, string Body)> items;
            lock (buffered)
            {
                items = [.. buffered];
            }
            foreach (var (at, body) in items)
            {
                if (DateTime.UtcNow - at <= PendingLifetime)
                {
                    handler(body);
                }
            }
        }
    }

    public void Unregister(string sid)
    {
        _handlers.TryRemove(sid, out _);
    }

    public void Dispatch(string sid, string lastChange)
    {
        if (_handlers.TryGetValue(sid, out var handler))
        {
            handler(lastChange);
            return;
        }
        Purge();
        var list = _pending.GetOrAdd(sid, _ => []);
        lock (list)
        {
            if (list.Count < PendingLimit)
            {
                list.Add((DateTime.UtcNow, lastChange));
            }
        }
    }

    private void Purge()
    {
        foreach (var (sid, list) in _pending)
        {
            bool expired;
            lock (list)
            {
                list.RemoveAll(i => DateTime.UtcNow - i.At > PendingLifetime);
                expired = list.Count == 0;
            }
            if (expired)
            {
                _pending.TryRemove(sid, out _);
            }
        }
    }
}
