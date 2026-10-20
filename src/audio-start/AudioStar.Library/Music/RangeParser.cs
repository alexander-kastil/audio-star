namespace AudioStar.Library.Music;

internal enum RangeOutcome { Full, Partial, NotSatisfiable }

internal static class RangeParser
{
    public static RangeOutcome Parse(string? header, long length, out long start, out long end)
    {
        start = 0;
        end = length - 1;
        if (string.IsNullOrWhiteSpace(header) || !header.StartsWith("bytes=", StringComparison.OrdinalIgnoreCase))
        {
            return RangeOutcome.Full;
        }
        var spec = header["bytes=".Length..].Trim();
        var dash = spec.IndexOf('-');
        if (spec.Contains(',') || dash < 0)
        {
            return RangeOutcome.Full;
        }
        var first = spec[..dash].Trim();
        var last = spec[(dash + 1)..].Trim();
        if (first.Length == 0)
        {
            if (!long.TryParse(last, out var suffix) || suffix < 0)
            {
                return RangeOutcome.Full;
            }
            if (suffix == 0 || length == 0)
            {
                return RangeOutcome.NotSatisfiable;
            }
            start = Math.Max(0, length - suffix);
            return RangeOutcome.Partial;
        }
        if (!long.TryParse(first, out var from) || from < 0)
        {
            return RangeOutcome.Full;
        }
        var to = length - 1;
        if (last.Length > 0 && (!long.TryParse(last, out to) || to < from))
        {
            return RangeOutcome.Full;
        }
        if (from >= length)
        {
            return RangeOutcome.NotSatisfiable;
        }
        start = from;
        end = Math.Min(to, length - 1);
        return RangeOutcome.Partial;
    }
}
