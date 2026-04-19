using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using Quol.Assets;
using Quol.Services;
using Quol.Views.Controls;

namespace Quol.Plugins;

/// <summary>
/// Base class for all Quol plugins.
/// Host owns config loading, geometry, shell, and window creation.
/// Subclasses provide metadata and UI content only.
/// </summary>
public abstract class QuolPluginBase
{
    private readonly PluginConfigService _configService = new();
    private string _configPath = string.Empty;

    public abstract string PluginId { get; }
    public abstract string Name { get; }
    public abstract string Version { get; }

    protected virtual bool ShowConfigButton => true;
    protected virtual bool ShowCloseButton => false;
    protected virtual bool IsTopmost => true;

    public void Initialize()
    {
        _configPath = _configService.GetPluginConfigPath(PluginId);
    }

    public Window CreateWindow()
    {
        var cfg = _configService.LoadPluginConfig(PluginId);
        var content = CreateContent();

        var shell = new QuolWindowShell
        {
            PluginName = cfg.App.Description,
            ShowConfigButton = ShowConfigButton,
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

        _configService.ApplyWindowGeometry(window, cfg);
        _configService.BindWindowGeometry(window, cfg, _configPath);
        OnWindowCreated(window);
        return window;
    }

    public void Unload() => OnUnload();

    protected virtual void OnWindowCreated(Window window) { }

    protected virtual void OnUnload() { }

    protected abstract Control CreateContent();
}
