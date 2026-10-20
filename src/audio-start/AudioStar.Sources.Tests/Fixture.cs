using System.Text.Json;

namespace AudioStar.Sources.Tests;

internal static class Fixture
{
    public static JsonDocument Load(string name) =>
        JsonDocument.Parse(File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "Fixtures", name)));

    public static JsonDocument Parse(string json) => JsonDocument.Parse(json);
}
