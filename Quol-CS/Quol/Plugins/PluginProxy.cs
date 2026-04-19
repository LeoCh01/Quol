using System;
using Avalonia.Controls;
using Quol.Services;

namespace Quol.Plugins;

/// <summary>
/// Config-driven plugin wrapper. Metadata comes from config.json; UI from the View type in the plugin DLL.
/// </summary>
public class PluginProxy : QuolPluginBase
{
    private readonly string _pluginId;
    private readonly string _name;
    private readonly string _version;
    private readonly Type _viewType;

    public PluginProxy(string pluginId, string name, string version, Type viewType)
    {
        _pluginId = pluginId;
        _name = name;
        _version = version;
        _viewType = viewType;
    }

    public override string PluginId => _pluginId;
    public override string Name => _name;
    public override string Version => _version;

    protected override Control CreateContent()
    {
        return (Control?)Activator.CreateInstance(_viewType)
            ?? throw new InvalidOperationException(
                $"Could not instantiate view type {_viewType.FullName}."
            );
    }
}
