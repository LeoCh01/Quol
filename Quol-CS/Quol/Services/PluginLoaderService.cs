using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using Quol.Plugins;

namespace Quol.Services;

public class PluginLoaderService
{
    private readonly Dictionary<string, QuolPluginBase> _loaded = new();
    private readonly PluginConfigService _configService = new();

    public QuolPluginBase Load(string pluginDir)
    {
        var pluginName = Path.GetFileName(pluginDir)!;
        var dllPath = Path.Combine(pluginDir, $"{pluginName}.dll");

        if (!File.Exists(dllPath))
            throw new FileNotFoundException($"Plugin DLL not found: {dllPath}");

        var config = _configService.LoadPluginConfig(pluginName);

        if (string.IsNullOrWhiteSpace(config.App.Id))
            throw new InvalidOperationException($"Plugin config missing 'id' field: {pluginName}");

        var asm = Assembly.LoadFrom(dllPath);
        var viewType =
            FindViewType(asm)
            ?? throw new InvalidOperationException($"No Control subclass found in {dllPath}");

        var plugin = new PluginProxy(
            config.App.Id,
            config.App.Description,
            config.App.Version,
            viewType
        );
        plugin.Initialize();
        _loaded[pluginName] = plugin;
        LoggingService.Info($"Loaded plugin '{config.App.Id}' v{config.App.Version}");
        return plugin;
    }

    private static Type? FindViewType(Assembly asm)
    {
        var controlType = typeof(Avalonia.Controls.Control);

        var candidates = asm.GetTypes()
            .Where(t =>
                t.IsClass
                && !t.IsAbstract
                && controlType.IsAssignableFrom(t)
                && t.Namespace?.StartsWith("Avalonia") == false
            )
            .ToList();

        // Prefer a type named exactly "View"
        return candidates.FirstOrDefault(t => t.Name == "View")
            // Last resort: first candidate
            ?? candidates.FirstOrDefault();
    }

    public void Unload(string pluginName)
    {
        if (!_loaded.TryGetValue(pluginName, out var plugin))
            return;

        plugin.Unload();
        _loaded.Remove(pluginName);
    }

    public void UnloadAll()
    {
        foreach (var name in new List<string>(_loaded.Keys))
            Unload(name);
    }
}
