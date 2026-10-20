namespace AudioStar.Sources.YtDlp;

internal static class YtDlpRedaction
{
    public const string Mask = "***";

    public static string Redact(IReadOnlyList<string> arguments, string text)
    {
        for (var i = 0; i < arguments.Count - 1; i++)
        {
            if (arguments[i] is "--password" or "-p" && arguments[i + 1].Length > 0)
            {
                text = text.Replace(arguments[i + 1], Mask, StringComparison.Ordinal);
            }
        }
        return text;
    }
}
