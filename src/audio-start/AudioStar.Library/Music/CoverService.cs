using System.Security.Cryptography;
using System.Text;
using AudioStar.Core;

namespace AudioStar.Library.Music;

internal sealed record CoverFile(string Path, string ContentType);

internal sealed class CoverService
{
    private readonly string _directory = Path.Combine(AppPaths.CacheDirectory, "covers");

    public async Task<CoverFile?> GetAsync(string audioPath, CancellationToken cancellationToken)
    {
        var modified = System.IO.File.GetLastWriteTimeUtc(audioPath).Ticks;
        var key = Convert.ToHexString(SHA1.HashData(Encoding.UTF8.GetBytes(audioPath.ToLowerInvariant() + "|" + modified))).ToLowerInvariant();
        Directory.CreateDirectory(_directory);
        var existing = Directory.EnumerateFiles(_directory, key + ".*").FirstOrDefault();
        if (existing is not null)
        {
            return new CoverFile(existing, TypeForExtension(Path.GetExtension(existing)));
        }
        var embedded = await Task.Run(() => ReadEmbedded(audioPath), cancellationToken);
        if (embedded is not null)
        {
            var target = Path.Combine(_directory, key + embedded.Value.Extension);
            await System.IO.File.WriteAllBytesAsync(target, embedded.Value.Data, cancellationToken);
            return new CoverFile(target, TypeForExtension(embedded.Value.Extension));
        }
        var folderCover = TagReader.FindFolderCover(audioPath);
        return folderCover is null ? null : new CoverFile(folderCover, TypeForExtension(Path.GetExtension(folderCover)));
    }

    private static (byte[] Data, string Extension)? ReadEmbedded(string audioPath)
    {
        try
        {
            using var file = TagLib.File.Create(audioPath);
            var picture = file.Tag.Pictures.FirstOrDefault(p => p.Type == TagLib.PictureType.FrontCover) ?? file.Tag.Pictures.FirstOrDefault();
            if (picture is null || picture.Data.Count == 0)
            {
                return null;
            }
            var extension = picture.MimeType?.Contains("png", StringComparison.OrdinalIgnoreCase) == true ? ".png" : ".jpg";
            return (picture.Data.Data, extension);
        }
        catch (Exception ex) when (ex is TagLib.CorruptFileException or TagLib.UnsupportedFormatException or IOException or UnauthorizedAccessException)
        {
            return null;
        }
    }

    private static string TypeForExtension(string extension) => extension.Equals(".png", StringComparison.OrdinalIgnoreCase) ? "image/png" : "image/jpeg";
}
