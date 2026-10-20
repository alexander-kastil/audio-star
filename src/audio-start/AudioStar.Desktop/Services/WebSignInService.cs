using System.Windows;
using AudioStar.Core;
using AudioStar.Desktop.Views;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.Wpf;

namespace AudioStar.Desktop.Services;

public sealed class WebSignInService : IWebSignIn
{
    private const string RuntimeMissing = "Sign-in needs the Microsoft Edge WebView2 Runtime. Install it from https://developer.microsoft.com/microsoft-edge/webview2 and try again.";

    private static string UserDataFolder => Path.Combine(AppPaths.CacheDirectory, "WebView2");

    private static Window? Owner => Application.Current.MainWindow is { IsVisible: true } window ? window : null;

    public async Task<WebSignInResult?> SignInAsync(WebSignInRequest request, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        var dispatcher = Application.Current.Dispatcher;
        var window = await await dispatcher.InvokeAsync(async () =>
        {
            var environment = await CreateEnvironmentAsync();
            var created = new WebSignInWindow(request, environment, Owner);
            created.Show();
            created.Activate();
            return created;
        });
        using var registration = cancellationToken.Register(() => dispatcher.BeginInvoke(window.Cancel));
        return await window.Completion;
    }

    public async Task SignOutAsync(Uri siteUri, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();
        await await Application.Current.Dispatcher.InvokeAsync(() => DeleteCookiesAsync(siteUri));
    }

    private static async Task<CoreWebView2Environment> CreateEnvironmentAsync()
    {
        try
        {
            Directory.CreateDirectory(UserDataFolder);
            return await CoreWebView2Environment.CreateAsync(null, UserDataFolder);
        }
        catch (WebView2RuntimeNotFoundException ex)
        {
            throw new InvalidOperationException(RuntimeMissing, ex);
        }
    }

    // The profile is only reachable through a browser instance, so a 1 px window outside the screen hosts one.
    private static async Task DeleteCookiesAsync(Uri siteUri)
    {
        var environment = await CreateEnvironmentAsync();
        var host = new Window
        {
            Width = 1,
            Height = 1,
            Left = -10000,
            Top = -10000,
            WindowStyle = WindowStyle.None,
            ShowInTaskbar = false,
            ShowActivated = false
        };
        var browser = new WebView2();
        host.Content = browser;
        host.Show();
        try
        {
            await browser.EnsureCoreWebView2Async(environment);
            var manager = browser.CoreWebView2.CookieManager;
            var suffix = "." + siteUri.Host;
            foreach (var cookie in await manager.GetCookiesAsync(null))
            {
                var domain = cookie.Domain.TrimStart('.');
                if (domain.Equals(siteUri.Host, StringComparison.OrdinalIgnoreCase) || domain.EndsWith(suffix, StringComparison.OrdinalIgnoreCase))
                {
                    manager.DeleteCookie(cookie);
                }
            }
        }
        finally
        {
            browser.Dispose();
            host.Close();
        }
    }
}
