using System.Buffers.Binary;

namespace AudioStar.Library.Media;

internal static class WavStream
{
    public const int SampleRate = 44100;
    public const int Channels = 2;
    public const int BytesPerFrame = 4;
    public const int ByteRate = SampleRate * BytesPerFrame;
    public const int HeaderLength = 44;

    public static long DataLength(TimeSpan duration) =>
        (long)Math.Round(duration.TotalSeconds * SampleRate) * BytesPerFrame;

    public static long TotalLength(TimeSpan duration) => HeaderLength + DataLength(duration);

    public static byte[] Header(long dataLength)
    {
        var header = new byte[HeaderLength];
        "RIFF"u8.CopyTo(header.AsSpan(0));
        BinaryPrimitives.WriteUInt32LittleEndian(header.AsSpan(4), (uint)(HeaderLength + dataLength - 8));
        "WAVE"u8.CopyTo(header.AsSpan(8));
        "fmt "u8.CopyTo(header.AsSpan(12));
        BinaryPrimitives.WriteUInt32LittleEndian(header.AsSpan(16), 16);
        BinaryPrimitives.WriteUInt16LittleEndian(header.AsSpan(20), 1);
        BinaryPrimitives.WriteUInt16LittleEndian(header.AsSpan(22), Channels);
        BinaryPrimitives.WriteUInt32LittleEndian(header.AsSpan(24), SampleRate);
        BinaryPrimitives.WriteUInt32LittleEndian(header.AsSpan(28), ByteRate);
        BinaryPrimitives.WriteUInt16LittleEndian(header.AsSpan(32), BytesPerFrame);
        BinaryPrimitives.WriteUInt16LittleEndian(header.AsSpan(34), 16);
        "data"u8.CopyTo(header.AsSpan(36));
        BinaryPrimitives.WriteUInt32LittleEndian(header.AsSpan(40), (uint)dataLength);
        return header;
    }

    public static (long SkipBytes, double StartSeconds) SeekFor(long rangeStart)
    {
        var offset = Math.Max(rangeStart, HeaderLength) - HeaderLength;
        var skip = offset % BytesPerFrame;
        return (skip, (offset - skip) / (double)ByteRate);
    }
}
