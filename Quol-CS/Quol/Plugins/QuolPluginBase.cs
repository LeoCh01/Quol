using System;
using System.Collections.Generic;
using System.Text.Json;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using Quol.Assets;
using Quol.Plugins;
using Quol.Services;
using Quol.Views.Controls;

namespace Quol.Plugins;

/// <summary>
/// Base class for all Quol plugins.
/// Host owns config loading, geometry, shell, and window creation.
/// Subclasses provide metadata and UI content only.
/// Plugins can access user-editable config via the Config property
/// and override OnUpdateConfig() to react to changes.
/// </summary>
public abstract class QuolPluginBase
{
    private readonly PluginConfigService _configService = new();
    private string _configPath = string.Empty;
    public Dictionary<string, JsonElement> Config { get; private set; } = [];

    public abstract string PluginId { get; }
    public abstract string Name { get; }
    public abstract string Version { get; }

    protected virtual bool ShowConfigButton => true;
    protected virtual bool ShowCloseButton => false;
    protected virtual bool IsTopmost => true;

    public void Initialize()
    {
        _configPath = _configService.GetPluginConfigPath(PluginId);
        LoadConfig();
    }

    private void LoadConfig()
    {
        var data = ConfigService.LoadConfig(_configPath);
        Config = data.Settings;
    }

    /// <summary>
    /// Reload config from disk and trigger OnUpdateConfig.
    /// Call this after manually updating the config file.
    /// </summary>
    public void ReloadConfig()
    {
        LoadConfig();
        OnUpdateConfig();
    }

    public Window CreateWindow()
    {
        var cfg = _configService.LoadPluginConfig(PluginId);
        var content = CreateContent();

        var shell = new QuolWindowShell
        {
            PluginName = cfg.App.Description,
            ShowConfigButton = cfg.App.ShowConfig,
            ShowCloseButton = ShowCloseButton,
            InnerContent = content,
        };

        var window = new Window
        {
            CanResize = true,
            WindowDecorations = WindowDecorations.None,
            Background = Brushes.Transparent,
            Content = shell,
            Title = cfg.App.Description,
            Topmost = IsTopmost,
            Icon = QuolWindowIcons.AppIcon,
        };

        // Store reference to plugin in window's tag for config window access
        window.Tag = this;

        _configService.ApplyWindowGeometry(window, cfg);
        _configService.BindWindowGeometry(window, cfg, _configPath);
        OnWindowCreated(window);
        return window;
    }

    public void Unload() => OnUnload();

    // ── Config helpers ────────────────────────────────────────────────────────

    public T GetConfig<T>(string key, T fallback = default!)
    {
        if (!Config.TryGetValue(key, out var elem))
            return fallback;
        try
        {
            return Config.Cfg<T>(key);
        }
        catch
        {
            return fallback;
        }
    }

    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Override this to react to config changes.
    /// Called when config is reloaded.
    /// </summary>
    protected virtual void OnUpdateConfig() { }

    protected virtual void OnWindowCreated(Window window) { }

    protected virtual void OnUnload() { }

    protected abstract Control CreateContent();
}
