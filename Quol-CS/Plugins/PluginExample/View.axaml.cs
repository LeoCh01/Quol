using System;
using Avalonia.Controls;
using Quol;

namespace PluginExample;

public partial class PluginView : UserControl
{
    private string _keyListenerId = string.Empty;

    public PluginView()
    {
        InitializeComponent();
        Loaded += OnLoaded;
        Unloaded += OnUnloaded;
    }

    private void OnLoaded(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        _keyListenerId = App.InputService.AddKeyPressListener(OnKeyPressed);
    }

    private void OnUnloaded(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        App.InputService.RemoveKeyPressListener(_keyListenerId);
    }

    private void OnKeyPressed(string key)
    {
        KeyLabel.Text = $"Last Key: {key}";
        Console.WriteLine($"{key == "1"} {key}");
        MessageLabel.Text = key == "1" ? "You pressed 1!" : string.Empty;
    }
}
