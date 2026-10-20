using System.Windows;
using System.Windows.Controls;

namespace AudioStar.Desktop.Resources;

public sealed class AdaptiveGrid : Panel
{
    public static readonly DependencyProperty MinItemWidthProperty = DependencyProperty.Register(
        nameof(MinItemWidth), typeof(double), typeof(AdaptiveGrid), new FrameworkPropertyMetadata(160.0, FrameworkPropertyMetadataOptions.AffectsMeasure));

    public static readonly DependencyProperty MaxItemWidthProperty = DependencyProperty.Register(
        nameof(MaxItemWidth), typeof(double), typeof(AdaptiveGrid), new FrameworkPropertyMetadata(320.0, FrameworkPropertyMetadataOptions.AffectsMeasure));

    public static readonly DependencyProperty SpacingProperty = DependencyProperty.Register(
        nameof(Spacing), typeof(double), typeof(AdaptiveGrid), new FrameworkPropertyMetadata(12.0, FrameworkPropertyMetadataOptions.AffectsMeasure));

    public double MinItemWidth
    {
        get => (double)GetValue(MinItemWidthProperty);
        set => SetValue(MinItemWidthProperty, value);
    }

    public double MaxItemWidth
    {
        get => (double)GetValue(MaxItemWidthProperty);
        set => SetValue(MaxItemWidthProperty, value);
    }

    public double Spacing
    {
        get => (double)GetValue(SpacingProperty);
        set => SetValue(SpacingProperty, value);
    }

    protected override Size MeasureOverride(Size availableSize)
    {
        var (columns, itemWidth) = Columns(availableSize.Width);
        var height = 0.0;
        var rowHeight = 0.0;
        for (var i = 0; i < InternalChildren.Count; i++)
        {
            var child = InternalChildren[i];
            child.Measure(new Size(itemWidth, double.PositiveInfinity));
            rowHeight = Math.Max(rowHeight, child.DesiredSize.Height);
            if ((i + 1) % columns == 0 || i == InternalChildren.Count - 1)
            {
                height += rowHeight + (i < InternalChildren.Count - 1 ? Spacing : 0);
                rowHeight = 0;
            }
        }
        var used = columns * itemWidth + (columns - 1) * Spacing;
        return new Size(double.IsInfinity(availableSize.Width) ? used : availableSize.Width, height);
    }

    protected override Size ArrangeOverride(Size finalSize)
    {
        var (columns, itemWidth) = Columns(finalSize.Width);
        var y = 0.0;
        for (var start = 0; start < InternalChildren.Count; start += columns)
        {
            var end = Math.Min(start + columns, InternalChildren.Count);
            var rowHeight = 0.0;
            for (var i = start; i < end; i++)
            {
                rowHeight = Math.Max(rowHeight, InternalChildren[i].DesiredSize.Height);
            }
            for (var i = start; i < end; i++)
            {
                InternalChildren[i].Arrange(new Rect((i - start) * (itemWidth + Spacing), y, itemWidth, rowHeight));
            }
            y += rowHeight + Spacing;
        }
        return finalSize;
    }

    private (int Columns, double ItemWidth) Columns(double width)
    {
        var count = Math.Max(1, InternalChildren.Count);
        if (double.IsInfinity(width) || double.IsNaN(width))
        {
            return (count, MinItemWidth);
        }
        var fit = Math.Max(1, (int)((width + Spacing) / (MinItemWidth + Spacing)));
        var columns = Math.Min(fit, count);
        var itemWidth = Math.Min(MaxItemWidth, (width - (columns - 1) * Spacing) / columns);
        return (columns, Math.Max(0, itemWidth));
    }
}
