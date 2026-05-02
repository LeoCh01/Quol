using System;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.VisualTree;

namespace Quol.Views.Controls;

public partial class QuolClosableWindowShell : UserControl
{
    public static readonly StyledProperty<string> WindowTitleProperty = AvaloniaProperty.Register<
        QuolClosableWindowShell,
        string
    >(nameof(WindowTitle), "Window");

    public static readonly StyledProperty<object?> InnerContentProperty = AvaloniaProperty.Register<
        QuolClosableWindowShell,
        object?
    >(nameof(InnerContent));

    public string WindowTitle
    {
        get => GetValue(WindowTitleProperty);
        set => SetValue(WindowTitleProperty, value);
    }

    public object? InnerContent
    {
        get => GetValue(InnerContentProperty);
        set => SetValue(InnerContentProperty, value);
    }

    public QuolClosableWindowShell()
    {
        InitializeComponent();
    }

    private void OnTitleBarPointerPressed(object? sender, PointerPressedEventArgs e)
    {
        if (!e.GetCurrentPoint(this).Properties.IsLeftButtonPressed)
            return;

        var host = this.FindAncestorOfType<Window>();
        if (host is null)
            return;

        try
        {
            host.BeginMoveDrag(e);
            e.Handled = true;
        }
        catch (InvalidOperationException)
        {
            // Ignore if drag cannot start from current pointer state.
        }
    }

    private void OnCloseClicked(object? sender, RoutedEventArgs e)
    {
        this.FindAncestorOfType<Window>()?.Close();
    }
}
