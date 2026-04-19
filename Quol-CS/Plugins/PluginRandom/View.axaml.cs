using System;
using Avalonia.Controls;
using Avalonia.Interactivity;

namespace PluginRandom;

public partial class PluginView : UserControl
{
    private readonly Random _random = new();

    public PluginView()
    {
        InitializeComponent();
    }

    private void OnGenerateClicked(object? sender, RoutedEventArgs e)
    {
        NumberText.Text = _random.Next(0, 1000).ToString();
    }
}
