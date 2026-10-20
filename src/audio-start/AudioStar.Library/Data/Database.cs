using System.Reflection;
using Microsoft.Data.Sqlite;

namespace AudioStar.Library.Data;

internal sealed record DeltaScript(int Version, string Name, string Sql);

internal static class DeltaScripts
{
    public const string Prefix = "AudioStar.Library.Deltas.";

    public static IReadOnlyList<DeltaScript> LoadEmbedded(Assembly assembly)
    {
        var scripts = new List<(string Name, string Sql)>();
        foreach (var resource in assembly.GetManifestResourceNames().Where(n => n.StartsWith(Prefix, StringComparison.Ordinal) && n.EndsWith(".sql", StringComparison.OrdinalIgnoreCase)))
        {
            using var stream = assembly.GetManifestResourceStream(resource)!;
            using var reader = new StreamReader(stream);
            scripts.Add((resource[Prefix.Length..], reader.ReadToEnd()));
        }
        return Order(scripts);
    }

    public static IReadOnlyList<DeltaScript> Order(IEnumerable<(string Name, string Sql)> scripts)
    {
        var parsed = scripts.Select(s => new DeltaScript(ParseVersion(s.Name), s.Name, s.Sql)).OrderBy(s => s.Version).ToList();
        var duplicate = parsed.GroupBy(s => s.Version).FirstOrDefault(g => g.Count() > 1);
        if (duplicate is not null)
        {
            throw new InvalidOperationException($"Two delta scripts share version {duplicate.Key}.");
        }
        return parsed;
    }

    public static int ParseVersion(string name)
    {
        var digits = new string(name.TakeWhile(char.IsDigit).ToArray());
        if (digits.Length == 0)
        {
            throw new InvalidOperationException($"Delta script '{name}' does not start with a version number.");
        }
        return int.Parse(digits);
    }

    public static async Task<int> ApplyAsync(SqliteConnection connection, IReadOnlyList<DeltaScript> scripts, CancellationToken cancellationToken)
    {
        int current;
        await using (var read = connection.CreateCommand())
        {
            read.CommandText = "PRAGMA user_version";
            current = Convert.ToInt32(await read.ExecuteScalarAsync(cancellationToken));
        }
        foreach (var script in scripts.Where(s => s.Version > current))
        {
            await using var transaction = (SqliteTransaction)await connection.BeginTransactionAsync(cancellationToken);
            await using var command = connection.CreateCommand();
            command.Transaction = transaction;
            command.CommandText = script.Sql + $"\nPRAGMA user_version = {script.Version};";
            await command.ExecuteNonQueryAsync(cancellationToken);
            await transaction.CommitAsync(cancellationToken);
            current = script.Version;
        }
        return current;
    }
}

internal sealed class Database(string path)
{
    private readonly SemaphoreSlim _gate = new(1, 1);
    private bool _ready;

    public string Path { get; } = path;

    public async Task<SqliteConnection> OpenAsync(CancellationToken cancellationToken = default)
    {
        await EnsureReadyAsync(cancellationToken);
        return await OpenRawAsync(cancellationToken);
    }

    private async Task EnsureReadyAsync(CancellationToken cancellationToken)
    {
        if (_ready)
        {
            return;
        }
        await _gate.WaitAsync(cancellationToken);
        try
        {
            if (_ready)
            {
                return;
            }
            Directory.CreateDirectory(System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(Path))!);
            await using var connection = await OpenRawAsync(cancellationToken);
            await using (var wal = connection.CreateCommand())
            {
                wal.CommandText = "PRAGMA journal_mode = WAL";
                await wal.ExecuteNonQueryAsync(cancellationToken);
            }
            await DeltaScripts.ApplyAsync(connection, DeltaScripts.LoadEmbedded(typeof(Database).Assembly), cancellationToken);
            _ready = true;
        }
        finally
        {
            _gate.Release();
        }
    }

    private async Task<SqliteConnection> OpenRawAsync(CancellationToken cancellationToken)
    {
        var connection = new SqliteConnection(new SqliteConnectionStringBuilder { DataSource = Path, Pooling = true }.ToString());
        await connection.OpenAsync(cancellationToken);
        return connection;
    }
}
