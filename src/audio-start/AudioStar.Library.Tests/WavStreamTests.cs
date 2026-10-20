using System.Buffers.Binary;
using AudioStar.Library.Media;
using FluentAssertions;

namespace AudioStar.Library.Tests;

public class WavStreamTests
{
    [Fact]
    public void Lengths_AreFrameAlignedAndIncludeTheHeader()
    {
        var duration = TimeSpan.FromSeconds(445.982);

        WavStream.DataLength(duration).Should().Be(19667806L * 4);
        (WavStream.DataLength(duration) % 4).Should().Be(0);
        WavStream.TotalLength(duration).Should().Be(44 + WavStream.DataLength(duration));
    }

    [Fact]
    public void Header_IsAValidPcmWaveHeader()
    {
        const long dataLength = 1_764_000;

        var header = WavStream.Header(dataLength);

        header.Should().HaveCount(44);
        System.Text.Encoding.ASCII.GetString(header, 0, 4).Should().Be("RIFF");
        BinaryPrimitives.ReadUInt32LittleEndian(header.AsSpan(4)).Should().Be((uint)(44 + dataLength - 8));
        System.Text.Encoding.ASCII.GetString(header, 8, 8).Should().Be("WAVEfmt ");
        BinaryPrimitives.ReadUInt32LittleEndian(header.AsSpan(16)).Should().Be(16);
        BinaryPrimitives.ReadUInt16LittleEndian(header.AsSpan(20)).Should().Be(1);
        BinaryPrimitives.ReadUInt16LittleEndian(header.AsSpan(22)).Should().Be(2);
        BinaryPrimitives.ReadUInt32LittleEndian(header.AsSpan(24)).Should().Be(44100);
        BinaryPrimitives.ReadUInt32LittleEndian(header.AsSpan(28)).Should().Be(176400);
        BinaryPrimitives.ReadUInt16LittleEndian(header.AsSpan(32)).Should().Be(4);
        BinaryPrimitives.ReadUInt16LittleEndian(header.AsSpan(34)).Should().Be(16);
        System.Text.Encoding.ASCII.GetString(header, 36, 4).Should().Be("data");
        BinaryPrimitives.ReadUInt32LittleEndian(header.AsSpan(40)).Should().Be((uint)dataLength);
    }

    [Theory]
    [InlineData(0, 0, 0.0)]
    [InlineData(43, 0, 0.0)]
    [InlineData(44, 0, 0.0)]
    [InlineData(47, 3, 0.0)]
    [InlineData(44 + 176400, 0, 1.0)]
    [InlineData(44 + 176400 + 6, 2, 176404 / 176400.0)]
    [InlineData(44 + 176400 * 60, 0, 60.0)]
    public void SeekFor_MapsAByteOffsetToTime(long rangeStart, long expectedSkip, double expectedSeconds)
    {
        var (skip, seconds) = WavStream.SeekFor(rangeStart);

        skip.Should().Be(expectedSkip);
        seconds.Should().BeApproximately(expectedSeconds, 1e-9);
    }
}
