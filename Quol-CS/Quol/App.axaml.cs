using System;
using System.Collections.Generic;
using System.IO;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using Quol.Services;
using Quol.Views;

namespace Quol;

public partial class App : Application
{
    private readonly PluginLoaderService _pluginLoader = new();
    private readonly PluginConfigService _pluginConfigService = new();
    public static readonly GlobalInputService InputService = new();

    private readonly List<Window> _pluginWindows = [];
    private bool _isHidden = false;
    private string? _toggleHotkeyId;

    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
    }

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            desktop.MainWindow = new MainWindow();
            desktop.MainWindow.Show();

            InputService.Start();
            LoadAndShowAllPlugins();
            RegisterToggleHotkey();

            desktop.Exit += (_, _) =>
            {
                _pluginLoader.UnloadAll();
                InputService.Stop();
            };
        }

        base.OnFrameworkInitializationCompleted();
    }

    private void LoadAndShowAllPlugins()
    {
        var pluginsRoot = Path.Combine(AppContext.BaseDirectory, "Plugins");
        if (!Directory.Exists(pluginsRoot))
            return;

        var mainConfig = _pluginConfigService.LoadMainConfig();
        var activePlugins = _pluginConfigService.GetActivePluginIds(mainConfig);

        foreach (var pluginId in activePlugins)
        {
            var pluginDir = Path.Combine(pluginsRoot, pluginId);
            if (!Directory.Exists(pluginDir))
                continue;

            var plugin = _pluginLoader.Load(pluginDir);
            var window = plugin.CreateWindow();
            _pluginWindows.Add(window);
            window.Show();
        }
    }

    private void RegisterToggleHotkey()
    {
        var mainConfig = _pluginConfigService.LoadMainConfig();
        var keyName = mainConfig.Custom["toggle_key"].GetString()!;
        _toggleHotkeyId = InputService.AddHotkey(keyName, ToggleAll, suppress: true);
    }

    private void ToggleAll()
    {
        _isHidden = !_isHidden;

        if (
            ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop
            && desktop.MainWindow is not null
        )
        {
            desktop.MainWindow.IsVisible = !_isHidden;
        }

        foreach (var window in _pluginWindows)
            window.IsVisible = !_isHidden;
    }
}
