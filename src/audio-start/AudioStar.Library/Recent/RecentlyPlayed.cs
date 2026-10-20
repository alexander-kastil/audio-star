using System.Text.Json;
using AudioStar.Core;
using AudioStar.Library.Data;
using Microsoft.Data.Sqlite;
using Microsoft.Extensions.DependencyInjection;

namespace AudioStar.Library.Recent;

internal sealed class RecentlyPlayed(Database database, IServiceProvider services) : IRecentlyPlayed
{
    public const int MaxItems = 200;

    private static readonly JsonSerializerOptions Json = new(JsonSerializerDefaults.Web);

    public event EventHandler? Changed;

    public async Task AddAsync(string kind, string sourceId, string title, string? subtitle, Uri? artworkUri, string payloadJson, CancellationToken cancellationToken = default)
    {
        await using var connection = await database.OpenAsync(cancellationToken);
        await using var transaction = (SqliteTransaction)await connection.BeginTransactionAsync(cancellationToken);
        await Execute(connection, transaction, "DELETE FROM recent_items WHERE kind = $kind AND source_id = $source AND title = $title", cancellationToken,
            ("$kind", kind), ("$source", sourceId), ("$title", title));
        await Execute(connection, transaction, "INSERT INTO recent_items (kind, source_id, title, subtitle, artwork_uri, played_at, payload_json) VALUES ($kind, $source, $title, $subtitle, $artwork, $playedAt, $payload)", cancellationToken,
            ("$kind", kind), ("$source", sourceId), ("$title", title), ("$subtitle", subtitle), ("$artwork", artworkUri?.AbsoluteUri), ("$playedAt", DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()), ("$payload", payloadJson));
        await Execute(connection, transaction, $"DELETE FROM recent_items WHERE id NOT IN (SELECT id FROM recent_items ORDER BY played_at DESC, id DESC LIMIT {MaxItems})", cancellationToken);
        await transaction.CommitAsync(cancellationToken);
        Changed?.Invoke(this, EventArgs.Empty);
    }

    public async Task<IReadOnlyList<RecentItem>> GetAsync(int limit = 100, CancellationToken cancellationToken = default)
    {
        await using var connection = await database.OpenAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT id, kind, source_id, title, subtitle, artwork_uri, played_at, payload_json FROM recent_items ORDER BY played_at DESC, id DESC LIMIT $limit";
        command.Parameters.AddWithValue("$limit", Math.Clamp(limit, 1, MaxItems));
        var result = new List<RecentItem>();
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        while (await reader.ReadAsync(cancellationToken))
        {
            result.Add(new RecentItem(
                reader.GetInt64(0),
                reader.GetString(1),
                reader.GetString(2),
                reader.GetString(3),
                reader.IsDBNull(4) ? null : reader.GetString(4),
                !reader.IsDBNull(5) && Uri.TryCreate(reader.GetString(5), UriKind.Absolute, out var artwork) ? artwork : null,
                DateTimeOffset.FromUnixTimeMilliseconds(reader.GetInt64(6)),
                reader.GetString(7)));
        }
        return result;
    }

    public async Task RemoveAsync(long id, CancellationToken cancellationToken = default)
    {
        await using var connection = await database.OpenAsync(cancellationToken);
        await Execute(connection, null, "DELETE FROM recent_items WHERE id = $id", cancellationToken, ("$id", id));
        Changed?.Invoke(this, EventArgs.Empty);
    }

    public async Task ReplayAsync(ISpeakerSession speaker, RecentItem item, CancellationToken cancellationToken = default)
    {
        switch (item.Kind)
        {
            case RecentKinds.Request:
                var request = JsonSerializer.Deserialize<PlayRequest>(item.PayloadJson, Json) ?? throw new InvalidOperationException("The saved play request is empty.");
                await speaker.Controller.PlayAsync(request, cancellationToken);
                break;
            case RecentKinds.SourcePlaylist:
                var playlist = JsonSerializer.Deserialize<SourcePlaylist>(item.PayloadJson, Json) ?? throw new InvalidOperationException("The saved playlist is empty.");
                var source = services.GetServices<IMusicSource>().FirstOrDefault(s => s.Id.Equals(item.SourceId, StringComparison.OrdinalIgnoreCase) || s.Id.Equals(playlist.SourceId, StringComparison.OrdinalIgnoreCase))
                    ?? throw new InvalidOperationException($"The source '{item.SourceId}' is not available.");
                await source.PlayAsync(speaker, playlist, 0, cancellationToken);
                break;
            default:
                throw new InvalidOperationException($"Unknown recent item kind '{item.Kind}'.");
        }
    }

    private static async Task Execute(SqliteConnection connection, SqliteTransaction? transaction, string sql, CancellationToken cancellationToken, params (string Name, object? Value)[] parameters)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = sql;
        foreach (var (name, value) in parameters)
        {
            command.Parameters.AddWithValue(name, value ?? DBNull.Value);
        }
        await command.ExecuteNonQueryAsync(cancellationToken);
    }
}
