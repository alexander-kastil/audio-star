using System.Text;

namespace AudioStar.Library.Music;

internal static class PathCodec
{
    public static string Encode(string path) => Convert.ToHexString(Encoding.UTF8.GetBytes(path)).ToLowerInvariant();

    public static bool TryDecode(string? hex, out string path)
    {
        path = "";
        if (string.IsNullOrEmpty(hex) || hex.Length % 2 != 0 || !hex.All(Uri.IsHexDigit))
        {
            return false;
        }
        try
        {
            path = new UTF8Encoding(false, true).GetString(Convert.FromHexString(hex));
            return path.Length > 0;
        }
        catch (ArgumentException)
        {
            return false;
        }
    }

    public static bool IsUnder(string folder, string path)
    {
        var root = Path.GetFullPath(folder).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
        return Path.GetFullPath(path).StartsWith(root, StringComparison.OrdinalIgnoreCase);
    }
}
