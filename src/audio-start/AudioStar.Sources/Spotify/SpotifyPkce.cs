using System.Security.Cryptography;
using System.Text;

namespace AudioStar.Sources.Spotify;

internal static class SpotifyPkce
{
    public static string CreateVerifier() => Base64Url(RandomNumberGenerator.GetBytes(64));

    public static string CreateState() => Base64Url(RandomNumberGenerator.GetBytes(16));

    public static string CreateChallenge(string verifier) => Base64Url(SHA256.HashData(Encoding.ASCII.GetBytes(verifier)));

    public static string Base64Url(byte[] bytes) =>
        Convert.ToBase64String(bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_');
}
