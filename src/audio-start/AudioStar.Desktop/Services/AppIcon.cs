using System.Drawing.Drawing2D;
using System.Runtime.InteropServices;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using Drawing = System.Drawing;

namespace AudioStar.Desktop.Services;

public static class AppIcon
{
    [DllImport("user32.dll")]
    private static extern bool DestroyIcon(IntPtr handle);

    public static Drawing.Icon CreateIcon()
    {
        using var bitmap = Render(32);
        var handle = bitmap.GetHicon();
        try
        {
            using var temporary = Drawing.Icon.FromHandle(handle);
            return (Drawing.Icon)temporary.Clone();
        }
        finally
        {
            DestroyIcon(handle);
        }
    }

    public static ImageSource CreateImageSource()
    {
        using var icon = CreateIcon();
        var source = Imaging.CreateBitmapSourceFromHIcon(icon.Handle, System.Windows.Int32Rect.Empty, BitmapSizeOptions.FromEmptyOptions());
        source.Freeze();
        return source;
    }

    private static Drawing.Bitmap Render(int size)
    {
        var bitmap = new Drawing.Bitmap(size, size);
        using var graphics = Drawing.Graphics.FromImage(bitmap);
        graphics.SmoothingMode = SmoothingMode.AntiAlias;
        graphics.Clear(Drawing.Color.Transparent);
        using var background = new Drawing.SolidBrush(Drawing.Color.FromArgb(255, 32, 32, 40));
        using var path = RoundedRectangle(new Drawing.RectangleF(0, 0, size, size), size * 0.22f);
        graphics.FillPath(background, path);
        var center = size / 2f;
        var outer = size * 0.40f;
        var inner = outer * 0.42f;
        var points = new Drawing.PointF[10];
        for (var i = 0; i < 10; i++)
        {
            var radius = i % 2 == 0 ? outer : inner;
            var angle = -Math.PI / 2 + i * Math.PI / 5;
            points[i] = new Drawing.PointF(center + (float)(radius * Math.Cos(angle)), center + (float)(radius * Math.Sin(angle)));
        }
        using var star = new Drawing.SolidBrush(Drawing.Color.FromArgb(255, 255, 196, 61));
        graphics.FillPolygon(star, points);
        return bitmap;
    }

    private static GraphicsPath RoundedRectangle(Drawing.RectangleF bounds, float radius)
    {
        var diameter = radius * 2;
        var path = new GraphicsPath();
        path.AddArc(bounds.X, bounds.Y, diameter, diameter, 180, 90);
        path.AddArc(bounds.Right - diameter, bounds.Y, diameter, diameter, 270, 90);
        path.AddArc(bounds.Right - diameter, bounds.Bottom - diameter, diameter, diameter, 0, 90);
        path.AddArc(bounds.X, bounds.Bottom - diameter, diameter, diameter, 90, 90);
        path.CloseFigure();
        return path;
    }
}
