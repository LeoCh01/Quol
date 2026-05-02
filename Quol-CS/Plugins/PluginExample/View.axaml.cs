using System.Collections.Generic;
using System.Text.Json;
using Avalonia.Controls;
using Avalonia.Media;
using Quol;
using Quol.Plugins;

namespace PluginExample;

public partial class View : UserControl
{
    private string _keyListenerId = string.Empty;
    private bool _isListening = false;
    private Window? _testWindow;
    private TextBlock? _mathLabel;
    private TextBlock? _opInfoLabel;
    private Dictionary<string, JsonElement> _config = new();

    public View()
    {
        InitializeComponent();
        _mathLabel = this.FindControl<TextBlock>("MathLabel");
        _opInfoLabel = this.FindControl<TextBlock>("OpInfoLabel");
        Loaded += OnLoaded;
        Unloaded += OnUnloaded;
    }

    public void OnUpdateConfig(Dictionary<string, JsonElement> config)
    {
        _config = config;
        RefreshMathDisplay();
    }

    private void OnLoaded(object? sender, Avalonia.Interactivity.RoutedEventArgs e) =>
        RefreshMathDisplay();

    private void OnUnloaded(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        if (_isListening)
            App.InputService.RemoveKeyPressListener(_keyListenerId);

        _testWindow?.Close();
        _testWindow = null;
    }

    private void OnOpenTestWindowClick(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        if (_testWindow is { IsVisible: true })
        {
            _testWindow.Activate();
            return;
        }

        var content = new TestWindowView();
        content.SetTitle(_config["advanced"].GetProperty("output_prefix").GetString()!);
        content.SetMathResult(_mathLabel?.Text ?? string.Empty);

        _testWindow = new Window
        {
            Width = 360,
            Height = 220,
            CanResize = true,
            WindowDecorations = WindowDecorations.None,
            Background = Brushes.Transparent,
            Content = content,
        };

        _testWindow.Closed += (_, _) => _testWindow = null;
        _testWindow.Show();
    }

    private void OnToggleClick(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        if (_isListening)
        {
            App.InputService.RemoveKeyPressListener(_keyListenerId);
            _isListening = false;
            ToggleButton.Content = "Start Listening";
            KeyLabel.Text = "Last Key: None";
            MessageLabel.Text = string.Empty;
        }
        else
        {
            _keyListenerId = App.InputService.AddKeyPressListener(
                OnKeyPressed,
                [_config.Cfg<string>("listen_key")]
            );
            _isListening = true;
            ToggleButton.Content = "Stop Listening";
        }
    }

    private void OnKeyPressed(string key)
    {
        KeyLabel.Text = $"Last Key: {key}";

        MessageLabel.Text =
            _config.Cfg<bool>("show_message") && key == _config.Cfg<string>("listen_key")
                ? _config.Cfg<string>("message_text")
                : string.Empty;
    }

    private void RefreshMathDisplay()
    {
        var a = _config.Cfg<int>("a");
        var b = _config.Cfg<int>("b");
        var opElem = _config.Cfg<JsonElement>("op");
        var opIndex = opElem[1].GetInt32();
        var op = opElem[0][opIndex].GetString()!;

        var result = op switch
        {
            "+" => (a + b).ToString(),
            "-" => (a - b).ToString(),
            "*" => (a * b).ToString(),
            "/" => (a / (double)b).ToString("0.##"),
            _ => "?",
        };

        if (_mathLabel is not null)
            _mathLabel.Text = $"{a} {op} {b} = {result}";

        if (_opInfoLabel is not null)
            _opInfoLabel.Text = $"Operator source: op[0][{opIndex}] -> '{op}'";
    }
}
