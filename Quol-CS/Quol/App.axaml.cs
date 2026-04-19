using System;
using System.IO;
using Avalonia;
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

            App.InputService.Start();
            LoadAndShowAllPlugins();

            desktop.Exit += (_, _) =>
            {
                _pluginLoader.UnloadAll();
                App.InputService.Stop();
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
            window.Show();
        }
    }
}
