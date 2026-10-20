using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;

namespace AudioStar.Desktop.Views;

public partial class CoverArt : UserControl
{
    public static readonly DependencyProperty SourceProperty = DependencyProperty.Register(
        nameof(Source), typeof(Uri), typeof(CoverArt), new PropertyMetadata(null, OnSourceChanged));

    public static readonly DependencyProperty CornerRadiusProperty = DependencyProperty.Register(
        nameof(CornerRadius), typeof(double), typeof(CoverArt), new PropertyMetadata(6.0));

    public CoverArt()
    {
        InitializeComponent();
    }

    public Uri? Source
    {
        get => (Uri?)GetValue(SourceProperty);
        set => SetValue(SourceProperty, value);
    }

    public double CornerRadius
    {
        get => (double)GetValue(CornerRadiusProperty);
        set => SetValue(CornerRadiusProperty, value);
    }

    private static void OnSourceChanged(DependencyObject sender, DependencyPropertyChangedEventArgs e)
    {
        var control = (CoverArt)sender;
        control.Picture.Source = Load(e.NewValue as Uri);
    }

    private static BitmapImage? Load(Uri? uri)
    {
        if (uri is null || !uri.IsAbsoluteUri)
        {
            return null;
        }
        try
        {
            var image = new BitmapImage();
            image.BeginInit();
            image.UriSource = uri;
            image.DecodePixelWidth = 512;
            image.CreateOptions = BitmapCreateOptions.IgnoreColorProfile;
            image.EndInit();
            return image;
        }
        catch (Exception ex) when (ex is NotSupportedException or IOException or InvalidOperationException)
        {
            return null;
        }
    }

    private void OnSizeChanged(object sender, SizeChangedEventArgs e)
    {
        Clip = new RectangleGeometry(new Rect(0, 0, e.NewSize.Width, e.NewSize.Height), CornerRadius, CornerRadius);
        Glyph.FontSize = Math.Max(12, Math.Min(e.NewSize.Width, e.NewSize.Height) * 0.4);
    }
}
