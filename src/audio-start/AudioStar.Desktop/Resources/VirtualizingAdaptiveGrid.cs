using System.Collections.Specialized;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Media;

namespace AudioStar.Desktop.Resources;

/// <summary>
/// Card grid like <see cref="AdaptiveGrid"/> that only builds the cards in view, so a playlist of
/// hundreds of tracks neither decodes hundreds of covers nor lays them all out. Every card is as
/// tall as the first one.
/// </summary>
public sealed class VirtualizingAdaptiveGrid : VirtualizingPanel, IScrollInfo
{
    private const double WheelStep = 56;

    public static readonly DependencyProperty MinItemWidthProperty = DependencyProperty.Register(
        nameof(MinItemWidth), typeof(double), typeof(VirtualizingAdaptiveGrid), new FrameworkPropertyMetadata(160.0, FrameworkPropertyMetadataOptions.AffectsMeasure));

    public static readonly DependencyProperty MaxItemWidthProperty = DependencyProperty.Register(
        nameof(MaxItemWidth), typeof(double), typeof(VirtualizingAdaptiveGrid), new FrameworkPropertyMetadata(320.0, FrameworkPropertyMetadataOptions.AffectsMeasure));

    public static readonly DependencyProperty SpacingProperty = DependencyProperty.Register(
        nameof(Spacing), typeof(double), typeof(VirtualizingAdaptiveGrid), new FrameworkPropertyMetadata(12.0, FrameworkPropertyMetadataOptions.AffectsMeasure));

    private Size _extent;
    private Size _viewport;
    private double _offset;
    private double _itemWidth;
    private double _rowHeight = double.NaN;
    private double _measuredForWidth = double.NaN;
    private int _columns = 1;

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
        _ = InternalChildren;
        var owner = ItemsControl.GetItemsOwner(this);
        var count = owner?.HasItems == true ? owner.Items.Count : 0;
        var width = double.IsInfinity(availableSize.Width) ? MinItemWidth : availableSize.Width;
        var fit = Math.Max(1, (int)((width + Spacing) / (MinItemWidth + Spacing)));
        _columns = Math.Max(1, Math.Min(fit, Math.Max(1, count)));
        _itemWidth = Math.Max(0, Math.Min(MaxItemWidth, (width - (_columns - 1) * Spacing) / _columns));

        if (count == 0)
        {
            RemoveRealized(0, -1);
            SetMetrics(new Size(width, 0), new Size(width, 0), 0);
            return new Size(width, 0);
        }

        if (double.IsNaN(_rowHeight) || _measuredForWidth != _itemWidth)
        {
            // Probe the first card for the common card height at this width.
            Realize(0, 0);
            _rowHeight = InternalChildren.Count > 0 ? InternalChildren[0].DesiredSize.Height : 0;
            _measuredForWidth = _itemWidth;
        }

        var rows = (count + _columns - 1) / _columns;
        var step = _rowHeight + Spacing;
        var extentHeight = Math.Max(0, rows * step - Spacing);
        var viewportHeight = double.IsInfinity(availableSize.Height) ? extentHeight : availableSize.Height;
        var offset = Math.Max(0, Math.Min(_offset, Math.Max(0, extentHeight - viewportHeight)));

        var firstRow = (int)Math.Floor(offset / step);
        var lastRow = Math.Min(rows - 1, (int)Math.Floor((offset + viewportHeight) / step));
        var first = firstRow * _columns;
        var last = Math.Min(count - 1, (lastRow + 1) * _columns - 1);

        Realize(first, last);
        RemoveRealized(first, last);
        // A card's height can depend on its own width (cover ratio), so follow the realized cards.
        var tallest = InternalChildren.Cast<UIElement>().Max(c => c.DesiredSize.Height);
        if (tallest != _rowHeight)
        {
            _rowHeight = tallest;
            step = _rowHeight + Spacing;
            extentHeight = Math.Max(0, rows * step - Spacing);
            viewportHeight = double.IsInfinity(availableSize.Height) ? extentHeight : availableSize.Height;
            offset = Math.Max(0, Math.Min(offset, Math.Max(0, extentHeight - viewportHeight)));
        }

        var size = new Size(width, viewportHeight);
        SetMetrics(new Size(width, extentHeight), size, offset);
        return size;
    }

    protected override Size ArrangeOverride(Size finalSize)
    {
        var generator = ItemContainerGenerator;
        var step = _rowHeight + Spacing;
        for (var i = 0; i < InternalChildren.Count; i++)
        {
            var index = generator.IndexFromGeneratorPosition(new GeneratorPosition(i, 0));
            if (index < 0)
            {
                continue;
            }
            var row = index / _columns;
            var column = index % _columns;
            InternalChildren[i].Arrange(new Rect(column * (_itemWidth + Spacing), row * step - _offset, _itemWidth, _rowHeight));
        }
        return finalSize;
    }

    private void Realize(int first, int last)
    {
        var generator = ItemContainerGenerator;
        var start = generator.GeneratorPositionFromIndex(first);
        var childIndex = start.Offset == 0 ? start.Index : start.Index + 1;
        using (generator.StartAt(start, GeneratorDirection.Forward, true))
        {
            for (var index = first; index <= last; index++, childIndex++)
            {
                var child = (UIElement)generator.GenerateNext(out var isNew);
                if (isNew)
                {
                    if (childIndex >= InternalChildren.Count)
                    {
                        AddInternalChild(child);
                    }
                    else
                    {
                        InsertInternalChild(childIndex, child);
                    }
                    generator.PrepareItemContainer(child);
                }
                child.Measure(new Size(_itemWidth, double.PositiveInfinity));
            }
        }
    }

    private void RemoveRealized(int first, int last)
    {
        var generator = ItemContainerGenerator;
        for (var i = InternalChildren.Count - 1; i >= 0; i--)
        {
            var position = new GeneratorPosition(i, 0);
            var index = generator.IndexFromGeneratorPosition(position);
            if (index < first || index > last)
            {
                generator.Remove(position, 1);
                RemoveInternalChildRange(i, 1);
            }
        }
    }

    protected override void OnItemsChanged(object sender, ItemsChangedEventArgs args)
    {
        switch (args.Action)
        {
            case NotifyCollectionChangedAction.Remove:
            case NotifyCollectionChangedAction.Replace:
                RemoveInternalChildRange(args.Position.Index, args.ItemUICount);
                break;
            case NotifyCollectionChangedAction.Move:
                RemoveInternalChildRange(args.OldPosition.Index, args.ItemUICount);
                break;
            case NotifyCollectionChangedAction.Reset:
                RemoveInternalChildRange(0, InternalChildren.Count);
                _offset = 0;
                break;
        }
        InvalidateMeasure();
    }

    private void SetMetrics(Size extent, Size viewport, double offset)
    {
        var changed = extent != _extent || viewport != _viewport || offset != _offset;
        _extent = extent;
        _viewport = viewport;
        _offset = offset;
        if (changed)
        {
            ScrollOwner?.InvalidateScrollInfo();
        }
    }

    public bool CanVerticallyScroll { get; set; } = true;

    public bool CanHorizontallyScroll { get; set; }

    public double ExtentWidth => _extent.Width;

    public double ExtentHeight => _extent.Height;

    public double ViewportWidth => _viewport.Width;

    public double ViewportHeight => _viewport.Height;

    public double HorizontalOffset => 0;

    public double VerticalOffset => _offset;

    public ScrollViewer? ScrollOwner { get; set; }

    public void SetVerticalOffset(double offset)
    {
        offset = Math.Max(0, Math.Min(offset, Math.Max(0, _extent.Height - _viewport.Height)));
        if (offset == _offset)
        {
            return;
        }
        _offset = offset;
        ScrollOwner?.InvalidateScrollInfo();
        InvalidateMeasure();
    }

    public void SetHorizontalOffset(double offset)
    {
    }

    public void LineUp() => SetVerticalOffset(_offset - WheelStep / 2);

    public void LineDown() => SetVerticalOffset(_offset + WheelStep / 2);

    public void LineLeft()
    {
    }

    public void LineRight()
    {
    }

    public void PageUp() => SetVerticalOffset(_offset - _viewport.Height);

    public void PageDown() => SetVerticalOffset(_offset + _viewport.Height);

    public void PageLeft()
    {
    }

    public void PageRight()
    {
    }

    public void MouseWheelUp() => SetVerticalOffset(_offset - WheelStep);

    public void MouseWheelDown() => SetVerticalOffset(_offset + WheelStep);

    public void MouseWheelLeft()
    {
    }

    public void MouseWheelRight()
    {
    }

    public Rect MakeVisible(Visual visual, Rect rectangle)
    {
        var child = visual as UIElement;
        while (child is not null && !InternalChildren.Contains(child))
        {
            child = VisualTreeHelper.GetParent(child) as UIElement;
        }
        if (child is null)
        {
            return rectangle;
        }
        var index = ItemContainerGenerator.IndexFromGeneratorPosition(new GeneratorPosition(InternalChildren.IndexOf(child), 0));
        var top = index / _columns * (_rowHeight + Spacing);
        if (top < _offset)
        {
            SetVerticalOffset(top);
        }
        else if (top + _rowHeight > _offset + _viewport.Height)
        {
            SetVerticalOffset(top + _rowHeight - _viewport.Height);
        }
        return rectangle;
    }
}
