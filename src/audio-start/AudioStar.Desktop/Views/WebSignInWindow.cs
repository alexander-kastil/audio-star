using System.Text.RegularExpressions;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Threading;
using AudioStar.Core;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.Wpf;

namespace AudioStar.Desktop.Views;

// The in-app browser popup: a WebView2 page that finishes on a redirect or on a cookie, see WebSignInRequest.
public sealed class WebSignInWindow : Window
{
    private readonly WebSignInRequest _request;
    private readonly CoreWebView2Environment _environment;
    private readonly WebView2 _browser = new();
    private readonly DispatcherTimer _timer = new() { Interval = TimeSpan.FromSeconds(1) };
    private readonly TaskCompletionSource<WebSignInResult?> _completion = new(TaskCreationOptions.RunContinuationsAsynchronously);
    private readonly Regex? _addressPattern;
    private bool _checking;

    public WebSignInWindow(WebSignInRequest request, CoreWebView2Environment environment, Window? owner)
    {
        _request = request;
        _environment = environment;
        _addressPattern = string.IsNullOrEmpty(request.AddressPattern) ? null : new Regex(request.AddressPattern, RegexOptions.IgnoreCase);
        Title = request.Title;
        Owner = owner;
        // soundcloud.com keeps its wide layout below 1000 px, so the popup is as wide as the monitor allows.
        var area = SystemParameters.WorkArea;
        if (owner is not null && PresentationSource.FromVisual(owner) is { } source)
        {
            var bounds = System.Windows.Forms.Screen.FromHandle(new System.Windows.Interop.WindowInteropHelper(owner).Handle).WorkingArea;
            var scale = source.CompositionTarget.TransformFromDevice;
            area = new Rect(bounds.Left * scale.M11, bounds.Top * scale.M22, bounds.Width * scale.M11, bounds.Height * scale.M22);
        }
        Width = Math.Min(1000, area.Width * 0.95);
        Height = Math.Min(800, area.Height * 0.95);
        WindowStartupLocation = WindowStartupLocation.CenterOwner;
        SetResourceReference(BackgroundProperty, "AppBackgroundBrush");
        Content = BuildContent();
        _timer.Tick += async (_, _) => await CheckCookieAsync();
        Loaded += async (_, _) => await InitializeAsync();
        Closed += (_, _) =>
        {
            _timer.Stop();
            _browser.Dispose();
            _completion.TrySetResult(null);
        };
    }

    public Task<WebSignInResult?> Completion => _completion.Task;

    public void Complete(WebSignInResult result)
    {
        if (_completion.TrySetResult(result))
        {
            Dispatcher.BeginInvoke(Close);
        }
    }

    public void Cancel()
    {
        if (_completion.TrySetCanceled())
        {
            Dispatcher.BeginInvoke(Close);
        }
    }

    private async Task InitializeAsync()
    {
        try
        {
            await _browser.EnsureCoreWebView2Async(_environment);
            _browser.CoreWebView2.NavigationStarting += OnNavigationStarting;
            // Single-page sites change the address through history navigation, which NavigationStarting does not report.
            _browser.CoreWebView2.SourceChanged += (_, _) => CheckAddress(_browser.CoreWebView2.Source);
            _browser.CoreWebView2.HistoryChanged += (_, _) => CheckAddress(_browser.CoreWebView2.Source);
            _browser.CoreWebView2.NavigationCompleted += async (_, _) => await CheckCookieAsync();
            _browser.Source = _request.StartUri;
            _timer.Start();
            await CheckCookieAsync();
        }
        catch (Exception ex)
        {
            if (_completion.TrySetException(ex))
            {
                Close();
            }
        }
    }

    private void OnNavigationStarting(object? sender, CoreWebView2NavigationStartingEventArgs e)
    {
        CheckAddress(e.Uri);
        if (_request.RedirectUri is { } redirect && e.Uri.StartsWith(redirect.AbsoluteUri, StringComparison.OrdinalIgnoreCase))
        {
            e.Cancel = true;
            Complete(new WebSignInResult(new Uri(e.Uri), null));
        }
    }

    private void CheckAddress(string? address)
    {
        if (_addressPattern is not null && !string.IsNullOrEmpty(address) && _addressPattern.IsMatch(address) && Uri.TryCreate(address, UriKind.Absolute, out var uri))
        {
            Complete(new WebSignInResult(uri, null));
        }
    }

    private UIElement BuildContent()
    {
        if (string.IsNullOrWhiteSpace(_request.Instructions) && string.IsNullOrEmpty(_request.CopyText))
        {
            return _browser;
        }
        var strip = new StackPanel { Margin = new Thickness(16, 12, 16, 12) };
        if (!string.IsNullOrWhiteSpace(_request.Instructions))
        {
            var text = new TextBlock { Text = _request.Instructions, TextWrapping = TextWrapping.Wrap };
            text.SetResourceReference(TextBlock.ForegroundProperty, "AppTextBrush");
            strip.Children.Add(text);
        }
        if (!string.IsNullOrEmpty(_request.CopyText))
        {
            var copy = new System.Windows.Controls.Button { Content = "Copy", Margin = new Thickness(8, 0, 0, 0), VerticalAlignment = VerticalAlignment.Center };
            var box = new System.Windows.Controls.TextBox { Text = _request.CopyText, IsReadOnly = true, VerticalContentAlignment = VerticalAlignment.Center };
            System.Windows.Automation.AutomationProperties.SetName(box, "Value to copy");
            copy.Click += (_, _) =>
            {
                try
                {
                    System.Windows.Clipboard.SetText(_request.CopyText);
                    copy.Content = "Copied";
                }
                catch (Exception)
                {
                    // The clipboard is held by another process; the value stays selectable in the box.
                }
            };
            var row = new DockPanel { Margin = new Thickness(0, string.IsNullOrWhiteSpace(_request.Instructions) ? 0 : 8, 0, 0), LastChildFill = true };
            DockPanel.SetDock(copy, Dock.Right);
            row.Children.Add(copy);
            row.Children.Add(box);
            strip.Children.Add(row);
        }
        var border = new Border { BorderThickness = new Thickness(0, 0, 0, 1), Child = strip };
        border.SetResourceReference(Border.BorderBrushProperty, "AppStrokeBrush");
        border.SetResourceReference(Border.BackgroundProperty, "AppCardBrush");
        var grid = new Grid();
        grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
        grid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
        Grid.SetRow(_browser, 1);
        grid.Children.Add(border);
        grid.Children.Add(_browser);
        return grid;
    }

    private async Task CheckCookieAsync()
    {
        if (_browser.CoreWebView2 is not null)
        {
            CheckAddress(_browser.CoreWebView2.Source);
        }
        if (_checking || _request.CookieUri is not { } site || string.IsNullOrEmpty(_request.CookieName) || _browser.CoreWebView2 is null)
        {
            return;
        }
        _checking = true;
        try
        {
            var cookies = await _browser.CoreWebView2.CookieManager.GetCookiesAsync(site.AbsoluteUri);
            var cookie = cookies.FirstOrDefault(c => c.Name == _request.CookieName && !string.IsNullOrEmpty(c.Value));
            if (cookie is not null)
            {
                Complete(new WebSignInResult(null, cookie.Value));
            }
        }
        catch (Exception)
        {
            // The browser is closing or still starting; the timer checks again.
        }
        finally
        {
            _checking = false;
        }
    }
}
