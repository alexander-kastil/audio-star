namespace AudioStar.Core;

// What the in-app sign-in window opens and when it is done: RedirectUri, CookieUri with CookieName, or AddressPattern.
public sealed record WebSignInRequest(string Title, Uri StartUri)
{
    // Done when the window navigates to a URL starting with this; that navigation is cancelled and its URL returned.
    public Uri? RedirectUri { get; init; }

    // Done when the cookie CookieName is set for CookieUri; its value is returned.
    public Uri? CookieUri { get; init; }
    public string? CookieName { get; init; }

    // Done when the window's address matches this regular expression, in-page (history) navigation included; that address is returned in RedirectedTo.
    public string? AddressPattern { get; init; }

    // Shown above the page. CopyText, when set, is shown with a Copy button that puts it on the clipboard.
    public string? Instructions { get; init; }
    public string? CopyText { get; init; }
}

public sealed record WebSignInResult(Uri? RedirectedTo, string? CookieValue);

public interface IWebSignIn
{
    // Opens the in-app browser window; completes when the request is done, or with null when the user closes the window.
    Task<WebSignInResult?> SignInAsync(WebSignInRequest request, CancellationToken cancellationToken = default);

    // Deletes the window's cookies for this site, so the next sign-in starts signed out.
    Task SignOutAsync(Uri siteUri, CancellationToken cancellationToken = default);
}
