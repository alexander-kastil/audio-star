namespace AudioStar.Speakers.Discovery;

internal static class SpeakerIdentity
{
    public static string Normalize(string? raw)
    {
        if (string.IsNullOrWhiteSpace(raw))
        {
            return "";
        }
        var value = raw.Trim();
        if (value.StartsWith("uuid:", StringComparison.OrdinalIgnoreCase))
        {
            value = value[5..];
        }
        var firstDash = value.IndexOf('-', StringComparison.Ordinal);
        if (firstDash > 0 && value.Length > firstDash)
        {
            value = value[..^firstDash];
        }
        value = value.Replace("-", "", StringComparison.Ordinal);
        if (value.Length == 32)
        {
            value = value[..24];
        }
        return value.ToUpperInvariant();
    }
}
