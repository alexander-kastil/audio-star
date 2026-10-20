using System.Globalization;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Input;
using System.Windows.Media;

namespace AudioStar.Desktop.Resources;

public static class Interaction
{
    public static readonly DependencyProperty FullTextToolTipProperty = DependencyProperty.RegisterAttached(
        "FullTextToolTip", typeof(bool), typeof(Interaction), new PropertyMetadata(false, OnFullTextToolTipChanged));

    public static bool GetFullTextToolTip(DependencyObject element) => (bool)element.GetValue(FullTextToolTipProperty);

    public static void SetFullTextToolTip(DependencyObject element, bool value) => element.SetValue(FullTextToolTipProperty, value);

    private static void OnFullTextToolTipChanged(DependencyObject sender, DependencyPropertyChangedEventArgs e)
    {
        if (sender is not TextBlock text)
        {
            return;
        }
        text.ToolTipOpening -= OnFullTextToolTipOpening;
        if (e.NewValue is true)
        {
            text.SetBinding(FrameworkElement.ToolTipProperty, new Binding(nameof(TextBlock.Text)) { RelativeSource = RelativeSource.Self });
            text.ToolTipOpening += OnFullTextToolTipOpening;
        }
    }

    private static void OnFullTextToolTipOpening(object sender, ToolTipEventArgs e)
    {
        if (sender is TextBlock text && !IsTrimmed(text))
        {
            e.Handled = true;
        }
    }

    private static bool IsTrimmed(TextBlock text)
    {
        if (string.IsNullOrEmpty(text.Text))
        {
            return false;
        }
        var formatted = new FormattedText(text.Text, CultureInfo.CurrentCulture, text.FlowDirection,
            new Typeface(text.FontFamily, text.FontStyle, text.FontWeight, text.FontStretch), text.FontSize, Brushes.Black,
            VisualTreeHelper.GetDpi(text).PixelsPerDip);
        if (text.TextWrapping != TextWrapping.NoWrap)
        {
            // Wrapped text is cut off by its height, not its width.
            formatted.MaxTextWidth = Math.Max(1, text.ActualWidth);
            if (!double.IsNaN(text.LineHeight))
            {
                formatted.LineHeight = text.LineHeight;
            }
            return formatted.Height > text.ActualHeight + 0.5;
        }
        return formatted.WidthIncludingTrailingWhitespace > text.ActualWidth + 0.5;
    }

    public static readonly DependencyProperty DoubleClickCommandProperty = DependencyProperty.RegisterAttached(
        "DoubleClickCommand", typeof(ICommand), typeof(Interaction), new PropertyMetadata(null, OnCommandChanged));

    public static readonly DependencyProperty DoubleClickParameterProperty = DependencyProperty.RegisterAttached(
        "DoubleClickParameter", typeof(object), typeof(Interaction), new PropertyMetadata(null));

    public static ICommand? GetDoubleClickCommand(DependencyObject element) => (ICommand?)element.GetValue(DoubleClickCommandProperty);

    public static void SetDoubleClickCommand(DependencyObject element, ICommand? value) => element.SetValue(DoubleClickCommandProperty, value);

    public static object? GetDoubleClickParameter(DependencyObject element) => element.GetValue(DoubleClickParameterProperty);

    public static void SetDoubleClickParameter(DependencyObject element, object? value) => element.SetValue(DoubleClickParameterProperty, value);

    private static void OnCommandChanged(DependencyObject sender, DependencyPropertyChangedEventArgs e)
    {
        if (sender is not Control control)
        {
            return;
        }
        control.MouseDoubleClick -= OnDoubleClick;
        if (e.NewValue is not null)
        {
            control.MouseDoubleClick += OnDoubleClick;
        }
    }

    private static void OnDoubleClick(object sender, MouseButtonEventArgs e)
    {
        if (e.ChangedButton != MouseButton.Left || sender is not DependencyObject element)
        {
            return;
        }
        var command = GetDoubleClickCommand(element);
        var parameter = GetDoubleClickParameter(element) ?? (element as FrameworkElement)?.DataContext;
        if (command?.CanExecute(parameter) == true)
        {
            command.Execute(parameter);
            e.Handled = true;
        }
    }
}
