namespace AudioStar.Sources.YtDlp;

public static class YtDlpCookies
{
    public static IReadOnlyList<string> Arguments(string? source)
    {
        var value = source?.Trim();
        if (string.IsNullOrEmpty(value))
        {
            return [];
        }
        var isFile = value.Contains('\\') || value.Contains('/') || value.EndsWith(".txt", StringComparison.OrdinalIgnoreCase) || File.Exists(value);
        return isFile ? ["--cookies", value] : ["--cookies-from-browser", value.ToLowerInvariant()];
    }
}
