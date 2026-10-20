using AudioStar.Core;
using Microsoft.Data.Sqlite;

namespace AudioStar.Library.Data;

internal sealed record TrackWrite(LibraryTrack Track, long Size, long ModifiedTicks);

internal sealed record KnownFile(long Size, long ModifiedTicks);

internal interface ITrackCatalog
{
    Task<IReadOnlyList<LibraryAlbum>> GetAlbumsAsync(string? search, CancellationToken cancellationToken);
    Task<IReadOnlyList<LibraryArtist>> GetArtistsAsync(string? search, CancellationToken cancellationToken);
    Task<IReadOnlyList<LibraryGenre>> GetGenresAsync(CancellationToken cancellationToken);
    Task<IReadOnlyList<LibraryTrack>> GetTracksAsync(LibraryQuery query, CancellationToken cancellationToken);
    Task<int> CountTracksAsync(LibraryQuery query, CancellationToken cancellationToken);
    Task<LibraryTrack?> GetTrackAsync(long id, CancellationToken cancellationToken);
    Task<IReadOnlyList<LibraryTrack>> GetTracksUnderAsync(string directory, CancellationToken cancellationToken);
}

internal sealed class TrackStore(Database database) : ITrackCatalog
{
    private const string AlbumExpr = "COALESCE(NULLIF(album, ''), 'Unknown Album')";
    private const string AlbumArtistExpr = "COALESCE(NULLIF(album_artist, ''), NULLIF(artist, ''), 'Unknown Artist')";
    private const string ArtistExpr = "COALESCE(NULLIF(artist, ''), NULLIF(album_artist, ''), 'Unknown Artist')";
    private const string TrackColumns = "id, path, title, artist, album_artist, album, genre, track_number, disc_number, year, duration_ms, has_cover";
    private const string TrackOrder = $"{AlbumArtistExpr} COLLATE NOCASE, {AlbumExpr} COLLATE NOCASE, COALESCE(disc_number, 0), COALESCE(track_number, 0), title COLLATE NOCASE";

    public async Task<IReadOnlyDictionary<string, KnownFile>> GetIndexAsync(CancellationToken cancellationToken)
    {
        await using var connection = await database.OpenAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT path, size, modified_ticks FROM tracks";
        var result = new Dictionary<string, KnownFile>(StringComparer.OrdinalIgnoreCase);
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        while (await reader.ReadAsync(cancellationToken))
        {
            result[reader.GetString(0)] = new KnownFile(reader.GetInt64(1), reader.GetInt64(2));
        }
        return result;
    }

    public async Task UpsertAsync(IReadOnlyList<TrackWrite> writes, CancellationToken cancellationToken)
    {
        if (writes.Count == 0)
        {
            return;
        }
        await using var connection = await database.OpenAsync(cancellationToken);
        await using var transaction = (SqliteTransaction)await connection.BeginTransactionAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = """
            INSERT INTO tracks (path, size, modified_ticks, title, artist, album_artist, album, genre, track_number, disc_number, year, duration_ms, has_cover)
            VALUES ($path, $size, $ticks, $title, $artist, $albumArtist, $album, $genre, $trackNumber, $discNumber, $year, $duration, $hasCover)
            ON CONFLICT(path) DO UPDATE SET
                size = excluded.size, modified_ticks = excluded.modified_ticks, title = excluded.title, artist = excluded.artist,
                album_artist = excluded.album_artist, album = excluded.album, genre = excluded.genre, track_number = excluded.track_number,
                disc_number = excluded.disc_number, year = excluded.year, duration_ms = excluded.duration_ms, has_cover = excluded.has_cover
            """;
        var path = command.Parameters.Add("$path", SqliteType.Text);
        var size = command.Parameters.Add("$size", SqliteType.Integer);
        var ticks = command.Parameters.Add("$ticks", SqliteType.Integer);
        var title = command.Parameters.Add("$title", SqliteType.Text);
        var artist = command.Parameters.Add("$artist", SqliteType.Text);
        var albumArtist = command.Parameters.Add("$albumArtist", SqliteType.Text);
        var album = command.Parameters.Add("$album", SqliteType.Text);
        var genre = command.Parameters.Add("$genre", SqliteType.Text);
        var trackNumber = command.Parameters.Add("$trackNumber", SqliteType.Integer);
        var discNumber = command.Parameters.Add("$discNumber", SqliteType.Integer);
        var year = command.Parameters.Add("$year", SqliteType.Integer);
        var duration = command.Parameters.Add("$duration", SqliteType.Integer);
        var hasCover = command.Parameters.Add("$hasCover", SqliteType.Integer);
        foreach (var write in writes)
        {
            var t = write.Track;
            path.Value = t.Path;
            size.Value = write.Size;
            ticks.Value = write.ModifiedTicks;
            title.Value = t.Title;
            artist.Value = (object?)t.Artist ?? DBNull.Value;
            albumArtist.Value = (object?)t.AlbumArtist ?? DBNull.Value;
            album.Value = (object?)t.Album ?? DBNull.Value;
            genre.Value = (object?)t.Genre ?? DBNull.Value;
            trackNumber.Value = (object?)t.TrackNumber ?? DBNull.Value;
            discNumber.Value = (object?)t.DiscNumber ?? DBNull.Value;
            year.Value = (object?)t.Year ?? DBNull.Value;
            duration.Value = (long)t.Duration.TotalMilliseconds;
            hasCover.Value = t.HasCover ? 1 : 0;
            await command.ExecuteNonQueryAsync(cancellationToken);
        }
        await transaction.CommitAsync(cancellationToken);
    }

    public async Task DeleteAsync(IReadOnlyList<string> paths, CancellationToken cancellationToken)
    {
        if (paths.Count == 0)
        {
            return;
        }
        await using var connection = await database.OpenAsync(cancellationToken);
        await using var transaction = (SqliteTransaction)await connection.BeginTransactionAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = "DELETE FROM tracks WHERE path = $path";
        var path = command.Parameters.Add("$path", SqliteType.Text);
        foreach (var item in paths)
        {
            path.Value = item;
            await command.ExecuteNonQueryAsync(cancellationToken);
        }
        await transaction.CommitAsync(cancellationToken);
    }

    public async Task<bool> IsKnownPathAsync(string path, CancellationToken cancellationToken)
    {
        await using var connection = await database.OpenAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT 1 FROM tracks WHERE path = $path LIMIT 1";
        command.Parameters.AddWithValue("$path", path);
        return await command.ExecuteScalarAsync(cancellationToken) is not null;
    }

    public async Task<IReadOnlyList<LibraryAlbum>> GetAlbumsAsync(string? search, CancellationToken cancellationToken)
    {
        await using var connection = await database.OpenAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        var where = new List<string>();
        AddSearch(command, where, search);
        command.CommandText = $"""
            SELECT {AlbumExpr} AS album_name, {AlbumArtistExpr} AS artist_name, COUNT(*), MIN(NULLIF(year, 0)), MIN(CASE WHEN has_cover = 1 THEN path END)
            FROM tracks {WhereClause(where)}
            GROUP BY album_name COLLATE NOCASE, artist_name COLLATE NOCASE
            ORDER BY album_name COLLATE NOCASE, artist_name COLLATE NOCASE
            """;
        var result = new List<LibraryAlbum>();
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        while (await reader.ReadAsync(cancellationToken))
        {
            result.Add(new LibraryAlbum(reader.GetString(0), reader.GetString(1), reader.GetInt32(2), reader.IsDBNull(3) ? null : reader.GetInt32(3), reader.IsDBNull(4) ? null : reader.GetString(4)));
        }
        return result;
    }

    public async Task<IReadOnlyList<LibraryArtist>> GetArtistsAsync(string? search, CancellationToken cancellationToken)
    {
        await using var connection = await database.OpenAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        var where = new List<string>();
        AddSearch(command, where, search);
        command.CommandText = $"""
            SELECT {ArtistExpr} AS artist_name, COUNT(DISTINCT {AlbumExpr} COLLATE NOCASE), COUNT(*)
            FROM tracks {WhereClause(where)}
            GROUP BY artist_name COLLATE NOCASE
            ORDER BY artist_name COLLATE NOCASE
            """;
        var result = new List<LibraryArtist>();
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        while (await reader.ReadAsync(cancellationToken))
        {
            result.Add(new LibraryArtist(reader.GetString(0), reader.GetInt32(1), reader.GetInt32(2)));
        }
        return result;
    }

    public async Task<IReadOnlyList<LibraryGenre>> GetGenresAsync(CancellationToken cancellationToken)
    {
        await using var connection = await database.OpenAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT genre, COUNT(*) FROM tracks WHERE genre IS NOT NULL AND genre <> '' GROUP BY genre COLLATE NOCASE ORDER BY genre COLLATE NOCASE";
        var result = new List<LibraryGenre>();
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        while (await reader.ReadAsync(cancellationToken))
        {
            result.Add(new LibraryGenre(reader.GetString(0), reader.GetInt32(1)));
        }
        return result;
    }

    public async Task<IReadOnlyList<LibraryTrack>> GetTracksAsync(LibraryQuery query, CancellationToken cancellationToken)
    {
        await using var connection = await database.OpenAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        var where = BuildTrackFilter(command, query);
        command.CommandText = $"SELECT {TrackColumns} FROM tracks {WhereClause(where)} ORDER BY {TrackOrder} LIMIT $limit OFFSET $offset";
        command.Parameters.AddWithValue("$limit", query.Limit <= 0 ? -1 : query.Limit);
        command.Parameters.AddWithValue("$offset", Math.Max(0, query.Offset));
        return await ReadTracksAsync(command, cancellationToken);
    }

    public async Task<int> CountTracksAsync(LibraryQuery query, CancellationToken cancellationToken)
    {
        await using var connection = await database.OpenAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        var where = BuildTrackFilter(command, query);
        command.CommandText = $"SELECT COUNT(*) FROM tracks {WhereClause(where)}";
        return Convert.ToInt32(await command.ExecuteScalarAsync(cancellationToken));
    }

    public async Task<LibraryTrack?> GetTrackAsync(long id, CancellationToken cancellationToken)
    {
        await using var connection = await database.OpenAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        command.CommandText = $"SELECT {TrackColumns} FROM tracks WHERE id = $id";
        command.Parameters.AddWithValue("$id", id);
        return (await ReadTracksAsync(command, cancellationToken)).FirstOrDefault();
    }

    public async Task<IReadOnlyList<LibraryTrack>> GetTracksUnderAsync(string directory, CancellationToken cancellationToken)
    {
        await using var connection = await database.OpenAsync(cancellationToken);
        await using var command = connection.CreateCommand();
        var prefix = directory.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
        command.CommandText = $"SELECT {TrackColumns} FROM tracks WHERE path LIKE $prefix ESCAPE '\\' ORDER BY title COLLATE NOCASE";
        command.Parameters.AddWithValue("$prefix", EscapeLike(prefix) + "%");
        return await ReadTracksAsync(command, cancellationToken);
    }

    private static List<string> BuildTrackFilter(SqliteCommand command, LibraryQuery query)
    {
        var where = new List<string>();
        AddSearch(command, where, query.Search);
        if (!string.IsNullOrEmpty(query.Artist))
        {
            where.Add($"({AlbumArtistExpr} = $artist COLLATE NOCASE OR {ArtistExpr} = $artist COLLATE NOCASE)");
            command.Parameters.AddWithValue("$artist", query.Artist);
        }
        if (!string.IsNullOrEmpty(query.Album))
        {
            where.Add($"{AlbumExpr} = $album COLLATE NOCASE");
            command.Parameters.AddWithValue("$album", query.Album);
        }
        if (!string.IsNullOrEmpty(query.Genre))
        {
            where.Add("genre = $genre COLLATE NOCASE");
            command.Parameters.AddWithValue("$genre", query.Genre);
        }
        return where;
    }

    private static void AddSearch(SqliteCommand command, List<string> where, string? search)
    {
        if (string.IsNullOrWhiteSpace(search))
        {
            return;
        }
        where.Add("(title LIKE $search ESCAPE '\\' OR artist LIKE $search ESCAPE '\\' OR album_artist LIKE $search ESCAPE '\\' OR album LIKE $search ESCAPE '\\')");
        command.Parameters.AddWithValue("$search", "%" + EscapeLike(search.Trim()) + "%");
    }

    internal static string EscapeLike(string value) => value.Replace("\\", "\\\\").Replace("%", "\\%").Replace("_", "\\_");

    private static string WhereClause(List<string> where) => where.Count == 0 ? "" : "WHERE " + string.Join(" AND ", where);

    private static async Task<IReadOnlyList<LibraryTrack>> ReadTracksAsync(SqliteCommand command, CancellationToken cancellationToken)
    {
        var result = new List<LibraryTrack>();
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        while (await reader.ReadAsync(cancellationToken))
        {
            result.Add(new LibraryTrack(
                reader.GetInt64(0),
                reader.GetString(1),
                reader.GetString(2),
                NullableString(reader, 3),
                NullableString(reader, 4),
                NullableString(reader, 5),
                NullableString(reader, 6),
                NullableInt(reader, 7),
                NullableInt(reader, 8),
                NullableInt(reader, 9),
                TimeSpan.FromMilliseconds(reader.GetInt64(10)),
                reader.GetInt32(11) != 0));
        }
        return result;
    }

    private static string? NullableString(SqliteDataReader reader, int ordinal) => reader.IsDBNull(ordinal) ? null : reader.GetString(ordinal);

    private static int? NullableInt(SqliteDataReader reader, int ordinal) => reader.IsDBNull(ordinal) ? null : reader.GetInt32(ordinal);
}
