using AudioStar.Library.Data;
using FluentAssertions;
using Microsoft.Data.Sqlite;

namespace AudioStar.Library.Tests;

public class DeltaScriptTests
{
    [Fact]
    public void Order_SortsByNumericVersion()
    {
        var ordered = DeltaScripts.Order([("0010_c.sql", "c"), ("0002_b.sql", "b"), ("0001_a.sql", "a")]);

        ordered.Select(s => s.Version).Should().Equal(1, 2, 10);
    }

    [Fact]
    public void Order_RejectsDuplicateVersions()
    {
        var act = () => DeltaScripts.Order([("0001_a.sql", "a"), ("0001_b.sql", "b")]);

        act.Should().Throw<InvalidOperationException>();
    }

    [Fact]
    public void Order_RejectsNamesWithoutVersion()
    {
        var act = () => DeltaScripts.Order([("create.sql", "a")]);

        act.Should().Throw<InvalidOperationException>();
    }

    [Fact]
    public void Embedded_ScriptsAreSequentialFromOne()
    {
        var scripts = DeltaScripts.LoadEmbedded(typeof(Database).Assembly);

        scripts.Should().NotBeEmpty();
        scripts.Select(s => s.Version).Should().Equal(Enumerable.Range(1, scripts.Count));
    }

    [Fact]
    public async Task Apply_SetsUserVersionAndIsIdempotent()
    {
        var path = Path.Combine(Path.GetTempPath(), $"audiostar-test-{Guid.NewGuid():N}.db");
        try
        {
            var scripts = DeltaScripts.LoadEmbedded(typeof(Database).Assembly);
            await using (var connection = new SqliteConnection($"Data Source={path};Pooling=False"))
            {
                await connection.OpenAsync();
                (await DeltaScripts.ApplyAsync(connection, scripts, CancellationToken.None)).Should().Be(scripts[^1].Version);
                (await DeltaScripts.ApplyAsync(connection, scripts, CancellationToken.None)).Should().Be(scripts[^1].Version);
            }
        }
        finally
        {
            SqliteConnection.ClearAllPools();
            File.Delete(path);
        }
    }
}
