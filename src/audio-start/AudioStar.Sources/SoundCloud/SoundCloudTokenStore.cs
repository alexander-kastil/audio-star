using System.Security.Cryptography;
using System.Text;
using AudioStar.Core;

namespace AudioStar.Sources.SoundCloud;

internal sealed class SoundCloudTokenStore(string? path = null)
{
    private static readonly byte[] Entropy = Encoding.UTF8.GetBytes("AudioStar.SoundCloud.WebToken");

    private readonly string _path = path ?? Path.Combine(AppPaths.DataDirectory, "soundcloud-token.bin");

    public string? Load()
    {
        if (!OperatingSystem.IsWindows() || !File.Exists(_path))
        {
            return null;
        }
        try
        {
            var plain = ProtectedData.Unprotect(File.ReadAllBytes(_path), Entropy, DataProtectionScope.CurrentUser);
            return Encoding.UTF8.GetString(plain) is { Length: > 0 } token ? token : null;
        }
        catch (Exception exception) when (exception is CryptographicException or IOException)
        {
            return null;
        }
    }

    public void Save(string token)
    {
        if (!OperatingSystem.IsWindows())
        {
            throw new PlatformNotSupportedException("The SoundCloud token is stored with Windows DPAPI.");
        }
        Directory.CreateDirectory(Path.GetDirectoryName(_path)!);
        File.WriteAllBytes(_path, ProtectedData.Protect(Encoding.UTF8.GetBytes(token), Entropy, DataProtectionScope.CurrentUser));
    }

    public void Delete()
    {
        if (File.Exists(_path))
        {
            File.Delete(_path);
        }
    }
}
