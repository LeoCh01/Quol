using System;
using System.Collections.Generic;
using System.Text.Json;
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
    private Control? _viewInstance;

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
        var view =
            (Control?)Activator.CreateInstance(_viewType)
            ?? throw new InvalidOperationException(
                $"Could not instantiate view type {_viewType.FullName}."
            );

        _viewInstance = view;
        DispatchConfigToView();

        return view;
    }

    protected override void OnUpdateConfig()
    {
        DispatchConfigToView();
    }

    private void DispatchConfigToView()
    {
        if (_viewInstance is null)
            return;

        // Preferred: public void OnUpdateConfig(Dictionary<string, JsonElement> config)
        var withConfig = _viewType.GetMethod(
            "OnUpdateConfig",
            System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance,
            null,
            [typeof(Dictionary<string, JsonElement>)],
            null
        );
        if (withConfig is not null)
        {
            withConfig.Invoke(_viewInstance, [Config]);
            return;
        }

        // Fallback: parameterless method if plugin view prefers pulling values itself
        var noArgs = _viewType.GetMethod(
            "OnUpdateConfig",
            System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance,
            null,
            Type.EmptyTypes,
            null
        );
        noArgs?.Invoke(_viewInstance, null);
    }
}
