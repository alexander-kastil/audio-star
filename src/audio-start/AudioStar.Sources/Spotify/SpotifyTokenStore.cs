using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using AudioStar.Core;

namespace AudioStar.Sources.Spotify;

internal sealed class SpotifyTokenStore(string? path = null)
{
    private static readonly byte[] Entropy = Encoding.UTF8.GetBytes("AudioStar.Spotify.RefreshToken");

    private readonly string _path = path ?? Path.Combine(AppPaths.DataDirectory, "spotify-token.bin");

    internal sealed record Stored(string ClientId, string RefreshToken);

    public string? Load(string clientId)
    {
        if (!OperatingSystem.IsWindows() || !File.Exists(_path))
        {
            return null;
        }
        try
        {
            var plain = ProtectedData.Unprotect(File.ReadAllBytes(_path), Entropy, DataProtectionScope.CurrentUser);
            var stored = JsonSerializer.Deserialize<Stored>(plain);
            return stored is not null && stored.ClientId == clientId ? stored.RefreshToken : null;
        }
        catch (Exception exception) when (exception is CryptographicException or JsonException or IOException)
        {
            return null;
        }
    }

    public void Save(string clientId, string refreshToken)
    {
        if (!OperatingSystem.IsWindows())
        {
            throw new PlatformNotSupportedException("The Spotify token is stored with Windows DPAPI.");
        }
        Directory.CreateDirectory(Path.GetDirectoryName(_path)!);
        var plain = JsonSerializer.SerializeToUtf8Bytes(new Stored(clientId, refreshToken));
        File.WriteAllBytes(_path, ProtectedData.Protect(plain, Entropy, DataProtectionScope.CurrentUser));
    }

    public void Delete()
    {
        if (File.Exists(_path))
        {
            File.Delete(_path);
        }
    }
}
