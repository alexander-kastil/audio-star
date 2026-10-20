using System.Text.Json;

namespace AudioStar.Speakers.Discovery;

internal sealed record CachedSpeaker(string Id, string Name, string Ip, int Port);

internal sealed class SpeakerCache(string path, ILogger<SpeakerCache> logger)
{
    private static readonly JsonSerializerOptions Options = new() { WriteIndented = true };
    private readonly SemaphoreSlim _gate = new(1, 1);

    public SpeakerCache(ILogger<SpeakerCache> logger)
        : this(Path.Combine(AppPaths.CacheDirectory, "speakers.json"), logger)
    {
    }

    public async Task<IReadOnlyList<CachedSpeaker>> LoadAsync(CancellationToken cancellationToken)
    {
        await _gate.WaitAsync(cancellationToken);
        try
        {
            return await ReadAsync(cancellationToken);
        }
        finally
        {
            _gate.Release();
        }
    }

    public async Task UpsertAsync(CachedSpeaker speaker, CancellationToken cancellationToken)
    {
        await _gate.WaitAsync(cancellationToken);
        try
        {
            var rows = (await ReadAsync(cancellationToken)).Where(r => r.Id != speaker.Id).Append(speaker).ToList();
            await WriteAsync(rows, cancellationToken);
        }
        finally
        {
            _gate.Release();
        }
    }

    public async Task RemoveAsync(string id, CancellationToken cancellationToken)
    {
        await _gate.WaitAsync(cancellationToken);
        try
        {
            var rows = await ReadAsync(cancellationToken);
            if (rows.Any(r => r.Id == id))
            {
                await WriteAsync(rows.Where(r => r.Id != id).ToList(), cancellationToken);
            }
        }
        finally
        {
            _gate.Release();
        }
    }

    private async Task<IReadOnlyList<CachedSpeaker>> ReadAsync(CancellationToken cancellationToken)
    {
        if (!File.Exists(path))
        {
            return [];
        }
        try
        {
            await using var stream = File.OpenRead(path);
            return await JsonSerializer.DeserializeAsync<List<CachedSpeaker>>(stream, Options, cancellationToken) ?? [];
        }
        catch (Exception ex) when (ex is JsonException or IOException)
        {
            logger.LogDebug(ex, "Speaker cache unreadable");
            return [];
        }
    }

    private async Task WriteAsync(List<CachedSpeaker> rows, CancellationToken cancellationToken)
    {
        try
        {
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            var temp = path + ".tmp";
            await File.WriteAllTextAsync(temp, JsonSerializer.Serialize(rows, Options), cancellationToken);
            File.Move(temp, path, overwrite: true);
        }
        catch (IOException ex)
        {
            logger.LogDebug(ex, "Speaker cache not written");
        }
    }
}
