namespace AudioStar.Speakers;

internal static class PcIdentity
{
    private static readonly Lazy<string> Id = new(Load);

    public static string Value => Id.Value;

    private static string Load()
    {
        var path = Path.Combine(AppPaths.DataDirectory, "speakers-pc-id.txt");
        try
        {
            if (File.Exists(path))
            {
                var existing = File.ReadAllText(path).Trim();
                if (existing.Length > 0)
                {
                    return existing;
                }
            }
            var created = Guid.NewGuid().ToString();
            Directory.CreateDirectory(AppPaths.DataDirectory);
            File.WriteAllText(path, created);
            return created;
        }
        catch (IOException)
        {
            return Guid.NewGuid().ToString();
        }
    }
}
