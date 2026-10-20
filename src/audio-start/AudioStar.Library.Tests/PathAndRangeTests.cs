using AudioStar.Library.Media;
using AudioStar.Library.Music;
using FluentAssertions;

namespace AudioStar.Library.Tests;

public class PathAndRangeTests
{
    [Fact]
    public void Encode_ProducesLowercaseHexOfUtf8Bytes()
    {
        PathCodec.Encode(@"C:\Müsik\a.mp3").Should().Be("433a5c4dc3bc73696b5c612e6d7033");
    }

    [Theory]
    [InlineData(@"D:\Music\Café\Träck 01.flac")]
    [InlineData(@"C:\a.mp3")]
    public void Decode_RoundTripsEncode(string path)
    {
        PathCodec.TryDecode(PathCodec.Encode(path), out var decoded).Should().BeTrue();
        decoded.Should().Be(path);
    }

    [Theory]
    [InlineData("")]
    [InlineData("abc")]
    [InlineData("zz")]
    [InlineData("ff")]
    public void Decode_RejectsInvalidInput(string hex)
    {
        PathCodec.TryDecode(hex, out _).Should().BeFalse();
    }

    [Fact]
    public void IsUnder_MatchesFolderBoundaries()
    {
        PathCodec.IsUnder(@"D:\Music", @"D:\Music\a\b.mp3").Should().BeTrue();
        PathCodec.IsUnder(@"D:\Music\", @"d:\music\b.mp3").Should().BeTrue();
        PathCodec.IsUnder(@"D:\Music", @"D:\MusicOther\b.mp3").Should().BeFalse();
        PathCodec.IsUnder(@"D:\Music", @"D:\Music\..\Secret\b.mp3").Should().BeFalse();
    }

    [Fact]
    public void Range_WithoutHeader_IsFull()
    {
        RangeParser.Parse(null, 1000, out var start, out var end).Should().Be(RangeOutcome.Full);
        (start, end).Should().Be((0L, 999L));
    }

    [Theory]
    [InlineData("bytes=0-99", 0, 99)]
    [InlineData("bytes=500-", 500, 999)]
    [InlineData("bytes=-100", 900, 999)]
    [InlineData("bytes=900-5000", 900, 999)]
    [InlineData("bytes=-5000", 0, 999)]
    public void Range_ParsesPartial(string header, long expectedStart, long expectedEnd)
    {
        RangeParser.Parse(header, 1000, out var start, out var end).Should().Be(RangeOutcome.Partial);
        (start, end).Should().Be((expectedStart, expectedEnd));
    }

    [Theory]
    [InlineData("bytes=1000-")]
    [InlineData("bytes=2000-3000")]
    [InlineData("bytes=-0")]
    public void Range_BeyondLength_IsNotSatisfiable(string header)
    {
        RangeParser.Parse(header, 1000, out _, out _).Should().Be(RangeOutcome.NotSatisfiable);
    }

    [Theory]
    [InlineData("items=0-5")]
    [InlineData("bytes=abc")]
    [InlineData("bytes=0-5,10-20")]
    [InlineData("bytes=50-10")]
    public void Range_Malformed_IsIgnored(string header)
    {
        RangeParser.Parse(header, 1000, out _, out _).Should().Be(RangeOutcome.Full);
    }

    [Theory]
    [InlineData("/stream/youtube/abc123", "youtube", "abc123")]
    [InlineData("/stream/youtube/a%2Fb%20c?x=1", "youtube", "a/b c")]
    [InlineData("/stream/soundcloud/a%2520b", "soundcloud", "a%20b")]
    public void StreamTarget_UnescapesFromRawTarget(string raw, string source, string item)
    {
        StreamEndpoint.ParseTarget(raw).Should().Be((source, item));
    }

    [Theory]
    [InlineData("/stream/youtube")]
    [InlineData("/media/music/aa")]
    [InlineData("/stream/youtube/a/b")]
    public void StreamTarget_RejectsOtherShapes(string raw)
    {
        StreamEndpoint.ParseTarget(raw).Should().BeNull();
    }

    [Theory]
    [InlineData("a.flac", "audio/flac")]
    [InlineData("a.MP3", "audio/mpeg")]
    [InlineData("a.m4a", "audio/mp4")]
    [InlineData("a.txt", "application/octet-stream")]
    public void ContentType_FollowsExtension(string file, string expected)
    {
        AudioFormats.ContentTypeFor(file).Should().Be(expected);
    }
}
