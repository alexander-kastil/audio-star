using System.Windows;
using System.Windows.Controls;

namespace AudioStar.Desktop.Resources;

/// <summary>Masonry panel: columns of equal width, each child goes into the shortest column.</summary>
public sealed class ColumnFlow : Panel
{
    public static readonly DependencyProperty MinItemWidthProperty = DependencyProperty.Register(
        nameof(MinItemWidth), typeof(double), typeof(ColumnFlow), new FrameworkPropertyMetadata(380.0, FrameworkPropertyMetadataOptions.AffectsMeasure));

    public static readonly DependencyProperty MaxItemWidthProperty = DependencyProperty.Register(
        nameof(MaxItemWidth), typeof(double), typeof(ColumnFlow), new FrameworkPropertyMetadata(100000.0, FrameworkPropertyMetadataOptions.AffectsMeasure));

    public static readonly DependencyProperty SpacingProperty = DependencyProperty.Register(
        nameof(Spacing), typeof(double), typeof(ColumnFlow), new FrameworkPropertyMetadata(24.0, FrameworkPropertyMetadataOptions.AffectsMeasure));

    private Rect[] _slots = [];

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
        var heights = new double[columns];
        _slots = new Rect[InternalChildren.Count];
        for (var i = 0; i < InternalChildren.Count; i++)
        {
            var child = InternalChildren[i];
            if (child.Visibility == Visibility.Collapsed)
            {
                continue;
            }
            child.Measure(new Size(itemWidth, double.PositiveInfinity));
            var column = 0;
            for (var c = 1; c < columns; c++)
            {
                if (heights[c] < heights[column])
                {
                    column = c;
                }
            }
            var height = child.DesiredSize.Height;
            _slots[i] = new Rect(column * (itemWidth + Spacing), heights[column], itemWidth, height);
            heights[column] += height + Spacing;
        }
        var total = Math.Max(0, heights.Max() - Spacing);
        var used = columns * itemWidth + (columns - 1) * Spacing;
        return new Size(double.IsInfinity(availableSize.Width) ? used : availableSize.Width, total);
    }

    protected override Size ArrangeOverride(Size finalSize)
    {
        for (var i = 0; i < InternalChildren.Count && i < _slots.Length; i++)
        {
            if (InternalChildren[i].Visibility != Visibility.Collapsed)
            {
                InternalChildren[i].Arrange(_slots[i]);
            }
        }
        return finalSize;
    }

    private (int Columns, double ItemWidth) Columns(double width)
    {
        if (double.IsInfinity(width) || double.IsNaN(width))
        {
            return (1, MinItemWidth);
        }
        var fit = Math.Max(1, (int)((width + Spacing) / (MinItemWidth + Spacing)));
        var itemWidth = Math.Min(MaxItemWidth, (width - (fit - 1) * Spacing) / fit);
        return (fit, Math.Max(0, itemWidth));
    }
}
