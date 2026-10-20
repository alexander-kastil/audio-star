namespace AudioStar.Sources.YtDlp;

public sealed class YtDlpException(string message, string stdErr = "") : Exception(message)
{
    public string StdErr { get; } = stdErr;
}

public static class YtDlpErrors
{
    public const string CookieHint = "yt-dlp cannot read the browser cookies (Chromium browsers on Windows encrypt them). Choose Firefox, or export a cookies.txt and set its path instead.";
    public const string OutdatedHint = "yt-dlp is too old for the current YouTube pages. Update it with yt-dlp -U or choco upgrade yt-dlp.";

    public static bool IsOutdated(string stdErr) =>
        stdErr.Contains("Unsupported lockup view model", StringComparison.OrdinalIgnoreCase);

    public static string Describe(string stdErr)
    {
        if (string.IsNullOrWhiteSpace(stdErr))
        {
            return "yt-dlp returned no data.";
        }
        if (IsOutdated(stdErr))
        {
            return OutdatedHint;
        }
        if (stdErr.Contains("Failed to decrypt", StringComparison.OrdinalIgnoreCase)
            || stdErr.Contains("DPAPI", StringComparison.OrdinalIgnoreCase)
            || stdErr.Contains("Could not copy", StringComparison.OrdinalIgnoreCase))
        {
            return CookieHint;
        }
        if (stdErr.Contains("cookies database", StringComparison.OrdinalIgnoreCase) && stdErr.Contains("could not find", StringComparison.OrdinalIgnoreCase))
        {
            return "yt-dlp could not find the browser profile that holds the cookies. Check the browser name or use a cookies.txt export.";
        }
        var lines = stdErr.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        var line = lines.LastOrDefault(l => l.StartsWith("ERROR:", StringComparison.OrdinalIgnoreCase)) ?? lines.Last();
        line = line.StartsWith("ERROR:", StringComparison.OrdinalIgnoreCase) ? line[6..].Trim() : line;
        return line.Length > 300 ? line[..300] : line;
    }
}
