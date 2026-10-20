namespace AudioStar.Speakers.Playback;

internal static class MimeTypes
{
    public const string Default = "audio/mpeg";

    public static string For(Uri streamUri)
    {
        var extension = Path.GetExtension(streamUri.AbsolutePath).ToLowerInvariant();
        return extension switch
        {
            ".mp3" => "audio/mpeg",
            ".flac" => "audio/flac",
            ".m4a" or ".mp4" or ".m4b" => "audio/mp4",
            ".aac" => "audio/aac",
            ".wav" => "audio/wav",
            ".aif" or ".aiff" => "audio/aiff",
            ".ogg" or ".oga" or ".opus" => "audio/ogg",
            ".wma" => "audio/x-ms-wma",
            ".m3u8" => "application/vnd.apple.mpegurl",
            _ => Default
        };
    }

    public static string ProtocolInfo(Uri streamUri)
    {
        var mime = For(streamUri);
        return mime == Default
            ? $"http-get:*:{mime}:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;"
            : $"http-get:*:{mime}:DLNA.ORG_OP=01;";
    }
}
