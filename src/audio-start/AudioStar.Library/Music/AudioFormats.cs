namespace AudioStar.Library.Music;

internal static class AudioFormats
{
    private static readonly Dictionary<string, string> ContentTypes = new(StringComparer.OrdinalIgnoreCase)
    {
        [".mp3"] = "audio/mpeg",
        [".flac"] = "audio/flac",
        [".m4a"] = "audio/mp4",
        [".aac"] = "audio/aac",
        [".alac"] = "audio/mp4",
        [".ogg"] = "audio/ogg",
        [".opus"] = "audio/ogg",
        [".wav"] = "audio/wav",
        [".aiff"] = "audio/aiff",
        [".aif"] = "audio/aiff",
        [".ape"] = "audio/x-ape",
        [".wma"] = "audio/x-ms-wma",
        [".dsf"] = "audio/x-dsf",
        [".dff"] = "audio/x-dff"
    };

    public static bool IsSupported(string path) => ContentTypes.ContainsKey(Path.GetExtension(path));

    public static string ContentTypeFor(string path) => ContentTypes.GetValueOrDefault(Path.GetExtension(path), "application/octet-stream");
}
