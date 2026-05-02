using System;
using System.Collections.Generic;
using System.Text.Json;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Interactivity;
using Quol.Services;
using Quol.Views.Controls;

namespace Quol.Views.Windows;

public partial class ConfigWindow : Window
{
    private Dictionary<string, JsonElement> _configChanges = [];
    private PluginConfigService _configService = new();
    private string _pluginId = "";
    private QuolClosableWindowShell? _shell;

    public bool WasSaved { get; private set; }

    public ConfigWindow()
    {
        InitializeComponent();
        _shell = this.FindControl<QuolClosableWindowShell>("Shell");
    }

    /// <summary>
    /// Initialize the config window with plugin configuration
    /// </summary>
    public void Initialize(string pluginId, string title, Dictionary<string, JsonElement> settings)
    {
        _pluginId = pluginId;
        Title = $"{title} - Config";
        WasSaved = false;

        _configChanges.Clear();

        if (_shell is not null)
        {
            _shell.WindowTitle = $"{title} Config";
            _shell.InnerContent = BuildContent(settings);
        }
    }

    private Control BuildContent(Dictionary<string, JsonElement> settings)
    {
        var mainPanel = new Grid
        {
            RowDefinitions = new RowDefinitions("Auto,Auto"),
            RowSpacing = 10,
            Margin = new Thickness(12),
        };

        var cancelButton = new Button { Content = "Cancel", MinWidth = 84 };
        var saveButton = new Button { Content = "Save", MinWidth = 84 };
        var actionsPanel = new StackPanel
        {
            Orientation = Avalonia.Layout.Orientation.Horizontal,
            Spacing = 8,
            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Right,
        };
        actionsPanel.Children.Add(cancelButton);
        actionsPanel.Children.Add(saveButton);

        var configPanel = ConfigWindowBuilder.BuildConfigPanel(settings, OnConfigValueChanged);
        Grid.SetRow(configPanel, 0);
        mainPanel.Children.Add(configPanel);

        Grid.SetRow(actionsPanel, 1);
        mainPanel.Children.Add(actionsPanel);

        cancelButton.Click += OnCancelClicked;
        saveButton.Click += OnSaveClicked;

        return mainPanel;
    }

    private void OnConfigValueChanged(string key, JsonElement value)
    {
        _configChanges[key] = value;
    }

    private void OnCancelClicked(object? sender, RoutedEventArgs e)
    {
        WasSaved = false;
        Close();
    }

    private void OnSaveClicked(object? sender, RoutedEventArgs e)
    {
        if (string.IsNullOrEmpty(_pluginId))
            return;

        // Load current config
        var cfg = _configService.LoadPluginConfig(_pluginId);

        // Apply all tracked changes
        foreach (var kvp in _configChanges)
        {
            cfg.Custom[kvp.Key] = kvp.Value;
        }

        // Save to file
        _configService.SavePluginConfig(_pluginId, cfg);

        WasSaved = true;

        Close();
    }
}
