using System.Collections.Concurrent;
using AudioStar.Core;
using Microsoft.Extensions.Logging;

namespace AudioStar.Sources.YtDlp;

public abstract class YtDlpStreamResolver(IYtDlp ytDlp, ILogger logger) : IStreamResolver
{
    private static readonly TimeSpan ExpiryMargin = TimeSpan.FromMinutes(10);
    private static readonly TimeSpan DefaultLifetime = TimeSpan.FromMinutes(20);
    private static readonly TimeSpan Timeout = TimeSpan.FromSeconds(90);

    private readonly ConcurrentDictionary<string, (ResolvedStream Stream, DateTimeOffset ValidUntil)> _cache = new();
    private readonly ConcurrentDictionary<string, SemaphoreSlim> _locks = new();

    public abstract string SourceId { get; }

    protected abstract string BuildUrl(string itemId);

    protected virtual IReadOnlyList<string> ExtraArguments() => [];

    public async Task<ResolvedStream> ResolveAsync(string itemId, CancellationToken cancellationToken = default)
    {
        if (TryGetCached(itemId, out var cached))
        {
            return cached;
        }
        var gate = _locks.GetOrAdd(itemId, _ => new SemaphoreSlim(1, 1));
        await gate.WaitAsync(cancellationToken);
        try
        {
            if (TryGetCached(itemId, out cached))
            {
                return cached;
            }
            var arguments = new List<string> { "-J", "--no-playlist", "--no-warnings" };
            arguments.AddRange(ExtraArguments());
            arguments.Add(BuildUrl(itemId));
            using var result = await ytDlp.GetJsonAsync(arguments, Timeout, cancellationToken);
            var selected = AudioFormatSelector.Select(result.Root)
                ?? throw new YtDlpException("No playable audio format was found for this item.", result.StdErr);
            var now = DateTimeOffset.UtcNow;
            var validUntil = selected.ExpiresAt is { } expires ? expires - ExpiryMargin : now + DefaultLifetime;
            if (validUntil > now)
            {
                _cache[itemId] = (selected.Stream, validUntil);
            }
            logger.LogInformation("Resolved {SourceId} {ItemId} as {ContentType}, transcode {Transcode}", SourceId, itemId, selected.Stream.ContentType, selected.Stream.RequiresTranscode);
            return selected.Stream;
        }
        finally
        {
            gate.Release();
        }
    }

    private bool TryGetCached(string itemId, out ResolvedStream stream)
    {
        if (_cache.TryGetValue(itemId, out var entry) && entry.ValidUntil > DateTimeOffset.UtcNow)
        {
            stream = entry.Stream;
            return true;
        }
        stream = null!;
        return false;
    }
}
