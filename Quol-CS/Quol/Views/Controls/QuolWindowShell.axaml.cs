using System;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.VisualTree;

namespace Quol.Views.Controls;

public partial class QuolWindowShell : UserControl
{
    public static readonly StyledProperty<string> PluginNameProperty = AvaloniaProperty.Register<
        QuolWindowShell,
        string
    >(nameof(PluginName), "Plugin");

    public static readonly StyledProperty<bool> ShowConfigButtonProperty =
        AvaloniaProperty.Register<QuolWindowShell, bool>(nameof(ShowConfigButton), false);

    public static readonly StyledProperty<bool> ShowCloseButtonProperty = AvaloniaProperty.Register<
        QuolWindowShell,
        bool
    >(nameof(ShowCloseButton), false);

    public static readonly StyledProperty<object?> InnerContentProperty = AvaloniaProperty.Register<
        QuolWindowShell,
        object?
    >(nameof(InnerContent));

    public string PluginName
    {
        get => GetValue(PluginNameProperty);
        set => SetValue(PluginNameProperty, value);
    }

    public bool ShowConfigButton
    {
        get => GetValue(ShowConfigButtonProperty);
        set => SetValue(ShowConfigButtonProperty, value);
    }

    public bool ShowCloseButton
    {
        get => GetValue(ShowCloseButtonProperty);
        set => SetValue(ShowCloseButtonProperty, value);
    }

    public object? InnerContent
    {
        get => GetValue(InnerContentProperty);
        set => SetValue(InnerContentProperty, value);
    }

    public QuolWindowShell()
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

    private void OnConfigClicked(object? sender, RoutedEventArgs e)
    {
        // Intentionally no-op for now.
    }

    private void OnCloseClicked(object? sender, RoutedEventArgs e)
    {
        var host = this.FindAncestorOfType<Window>();
        host?.Close();
    }
}
