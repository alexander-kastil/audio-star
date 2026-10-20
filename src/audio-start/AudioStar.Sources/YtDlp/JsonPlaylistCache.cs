using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Logging;

namespace AudioStar.Sources.YtDlp;

public sealed class JsonPlaylistCache(string directory, ILogger<JsonPlaylistCache> logger) : IPlaylistCache
{
    private readonly SemaphoreSlim _writeLock = new(1, 1);

    public async Task<CachedPlaylist?> GetAsync(string sourceId, string playlistId, CancellationToken cancellationToken = default)
    {
        var path = PathFor(sourceId, playlistId);
        try
        {
            if (!File.Exists(path))
            {
                return null;
            }
            await using var stream = File.OpenRead(path);
            return await JsonSerializer.DeserializeAsync<CachedPlaylist>(stream, cancellationToken: cancellationToken);
        }
        catch (Exception exception) when (exception is JsonException or IOException or UnauthorizedAccessException or NotSupportedException)
        {
            logger.LogWarning("Playlist cache file {Path} could not be read: {Message}", path, exception.Message);
            return null;
        }
    }

    public async Task SaveAsync(CachedPlaylist entry, CancellationToken cancellationToken = default)
    {
        var path = PathFor(entry.Playlist.SourceId, entry.Playlist.Id);
        await _writeLock.WaitAsync(cancellationToken);
        try
        {
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            var temp = $"{path}.tmp";
            await File.WriteAllTextAsync(temp, JsonSerializer.Serialize(entry), cancellationToken);
            File.Move(temp, path, true);
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
        {
            logger.LogWarning("Playlist cache file {Path} could not be written: {Message}", path, exception.Message);
        }
        finally
        {
            _writeLock.Release();
        }
    }

    public async Task RemoveAsync(string sourceId, string playlistId, CancellationToken cancellationToken = default)
    {
        var path = PathFor(sourceId, playlistId);
        await _writeLock.WaitAsync(cancellationToken);
        try
        {
            File.Delete(path);
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
        {
            logger.LogWarning("Playlist cache file {Path} could not be deleted: {Message}", path, exception.Message);
        }
        finally
        {
            _writeLock.Release();
        }
    }

    private string PathFor(string sourceId, string playlistId) =>
        Path.Combine(directory, sourceId, $"{Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(playlistId)))}.json");
}
