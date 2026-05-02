using System;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.VisualTree;
using Quol.Plugins;
using Quol.Services;

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
        var hostWindow = this.FindAncestorOfType<Window>();
        if (hostWindow?.Tag is not QuolPluginBase plugin)
            return;

        var configService = new PluginConfigService();
        var cfg = configService.LoadPluginConfig(plugin.PluginId);

        // Create and show the dedicated config window
        var configWindow = new Quol.Views.Windows.ConfigWindow();
        configWindow.Initialize(plugin.PluginId, cfg.App.Description, cfg.Custom);

        // Reload only when user saved
        configWindow.Closed += (s, e) =>
        {
            if (configWindow.WasSaved)
                plugin.ReloadConfig();
        };

        configWindow.ShowDialog(hostWindow);
    }

    private void OnCloseClicked(object? sender, RoutedEventArgs e)
    {
        var host = this.FindAncestorOfType<Window>();
        host?.Close();
    }
}
