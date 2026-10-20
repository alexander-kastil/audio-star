using AudioStar.Core;

namespace AudioStar.Library.Music;

internal static class TagReader
{
    private static readonly string[] CoverNames = ["folder.jpg", "cover.jpg", "folder.png", "cover.png"];

    public static string? FindFolderCover(string audioPath)
    {
        var directory = Path.GetDirectoryName(audioPath);
        if (directory is null)
        {
            return null;
        }
        return CoverNames.Select(n => Path.Combine(directory, n)).FirstOrDefault(System.IO.File.Exists);
    }

    public static LibraryTrack Read(string path)
    {
        var fallbackTitle = Path.GetFileNameWithoutExtension(path);
        var folderCover = FindFolderCover(path) is not null;
        try
        {
            using var file = TagLib.File.Create(path);
            var tag = file.Tag;
            var title = string.IsNullOrWhiteSpace(tag.Title) ? fallbackTitle : tag.Title.Trim();
            return new LibraryTrack(
                0,
                path,
                title,
                Clean(tag.FirstPerformer),
                Clean(tag.FirstAlbumArtist),
                Clean(tag.Album),
                Clean(tag.FirstGenre),
                tag.Track > 0 ? (int)tag.Track : null,
                tag.Disc > 0 ? (int)tag.Disc : null,
                tag.Year > 0 ? (int)tag.Year : null,
                file.Properties?.Duration ?? TimeSpan.Zero,
                tag.Pictures.Length > 0 || folderCover);
        }
        catch (Exception ex) when (ex is TagLib.CorruptFileException or TagLib.UnsupportedFormatException or IOException or UnauthorizedAccessException)
        {
            return new LibraryTrack(0, path, fallbackTitle, null, null, null, null, null, null, null, TimeSpan.Zero, folderCover);
        }
    }

    private static string? Clean(string? value) => string.IsNullOrWhiteSpace(value) ? null : value.Trim();
}
