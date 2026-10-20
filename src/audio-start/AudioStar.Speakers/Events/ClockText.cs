using System.Globalization;

namespace AudioStar.Speakers.Events;

internal static class ClockText
{
    public static TimeSpan Parse(string? text)
    {
        if (string.IsNullOrWhiteSpace(text))
        {
            return TimeSpan.Zero;
        }
        var parts = text.Trim().Split(':');
        if (parts.Length < 2 || parts.Length > 3)
        {
            return TimeSpan.Zero;
        }
        var numbers = new double[3];
        var offset = 3 - parts.Length;
        for (var i = 0; i < parts.Length; i++)
        {
            if (!double.TryParse(parts[i], NumberStyles.Float, CultureInfo.InvariantCulture, out var number) || number < 0)
            {
                return TimeSpan.Zero;
            }
            numbers[i + offset] = number;
        }
        return TimeSpan.FromHours(numbers[0]) + TimeSpan.FromMinutes(numbers[1]) + TimeSpan.FromSeconds(numbers[2]);
    }

    public static string Format(TimeSpan position)
    {
        var clamped = position < TimeSpan.Zero ? TimeSpan.Zero : position;
        return $"{(int)clamped.TotalHours:00}:{clamped.Minutes:00}:{clamped.Seconds:00}";
    }

    public static TimeSpan ParseDidlDuration(string? text)
    {
        if (string.IsNullOrWhiteSpace(text))
        {
            return TimeSpan.Zero;
        }
        if (text.Contains(':', StringComparison.Ordinal))
        {
            return Parse(text);
        }
        return long.TryParse(text, NumberStyles.Integer, CultureInfo.InvariantCulture, out var milliseconds) && milliseconds > 0
            ? TimeSpan.FromMilliseconds(milliseconds)
            : TimeSpan.Zero;
    }
}
