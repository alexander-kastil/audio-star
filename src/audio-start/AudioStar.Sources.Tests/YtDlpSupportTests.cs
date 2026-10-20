using AudioStar.Sources.YtDlp;
using FluentAssertions;

namespace AudioStar.Sources.Tests;

public class YtDlpSupportTests
{
    [Theory]
    [InlineData("firefox", "--cookies-from-browser", "firefox")]
    [InlineData("Edge", "--cookies-from-browser", "edge")]
    [InlineData(@"C:\Users\me\cookies.txt", "--cookies", @"C:\Users\me\cookies.txt")]
    [InlineData("cookies.txt", "--cookies", "cookies.txt")]
    public void Cookies_ChooseBrowserOrFile(string source, string flag, string value)
    {
        YtDlpCookies.Arguments(source).Should().Equal(flag, value);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData(null)]
    public void Cookies_EmptySource_AddsNothing(string? source)
    {
        YtDlpCookies.Arguments(source).Should().BeEmpty();
    }

    [Fact]
    public void Describe_ChromiumCookieFailure_SuggestsFirefoxOrCookiesTxt()
    {
        var message = YtDlpErrors.Describe("ERROR: Failed to decrypt with DPAPI. See https://github.com/yt-dlp/yt-dlp/issues/10927");

        message.Should().Contain("Firefox").And.Contain("cookies.txt");
    }

    [Fact]
    public void Describe_OutdatedExtractor_AsksForUpdate()
    {
        var message = YtDlpErrors.Describe("WARNING: [youtube:tab] Unsupported lockup view model content type \"LOCKUP_CONTENT_TYPE_VIDEO\"");

        message.Should().Contain("Update");
    }

    [Fact]
    public void Describe_GenericError_ReturnsLastErrorLineWithoutPrefix()
    {
        var message = YtDlpErrors.Describe("WARNING: x\nERROR: [youtube:tab] PL1: YouTube said: The playlist does not exist.\n");

        message.Should().Be("[youtube:tab] PL1: YouTube said: The playlist does not exist.");
    }
}
