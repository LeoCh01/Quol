using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using Avalonia;
using Avalonia.Controls;
using Quol.Models;

namespace Quol.Services;

public class PluginConfigService
{
    private static readonly JsonSerializerOptions JsonOptions = new() { WriteIndented = true };

    public string ConfigRoot => Path.Combine(AppContext.BaseDirectory, "Config");
    public string PluginsRoot => Path.Combine(AppContext.BaseDirectory, "Plugins");

    public string GetMainConfigPath() => Path.Combine(ConfigRoot, "main.config.json");

    public string GetPluginConfigPath(string pluginId) =>
        Path.Combine(PluginsRoot, pluginId, "config.json");

    public PluginConfigFile LoadMainConfig()
    {
        var path = GetMainConfigPath();
        if (!File.Exists(path))
            throw new FileNotFoundException($"Main config not found: {path}");

        var json = File.ReadAllText(path);
        return JsonSerializer.Deserialize<PluginConfigFile>(json, JsonOptions)
            ?? throw new InvalidOperationException($"Failed to parse main config: {path}");
    }

    public PluginConfigFile LoadPluginConfig(string pluginId)
    {
        var path = GetPluginConfigPath(pluginId);
        if (!File.Exists(path))
            throw new FileNotFoundException($"Plugin config not found: {path}");

        var json = File.ReadAllText(path);
        var cfg =
            JsonSerializer.Deserialize<PluginConfigFile>(json, JsonOptions)
            ?? throw new InvalidOperationException($"Failed to parse plugin config: {path}");

        if (cfg.App == null)
            throw new InvalidOperationException($"Plugin config missing '-' section: {path}");

        return cfg;
    }

    public void Save(string path, PluginConfigFile config)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        var json = JsonSerializer.Serialize(config, JsonOptions);
        File.WriteAllText(path, json);
    }

    public void SavePluginConfig(string pluginId, PluginConfigFile config)
    {
        var path = GetPluginConfigPath(pluginId);
        Save(path, config);
    }

    public void ApplyWindowGeometry(Window window, PluginConfigFile config)
    {
        var isDefaultPos = GetIsDefaultPos(config);
        var geometry = isDefaultPos ? config.App.DefaultGeometry : config.App.Geometry;

        if (geometry is not { Length: 4 })
            throw new InvalidOperationException(
                "Config geometry must have exactly 4 values [x, y, w, h]."
            );

        window.Position = new PixelPoint(geometry[0], geometry[1]);
        window.Width = geometry[2] > 0 ? geometry[2] : 250;
        window.SizeToContent = SizeToContent.Height;
    }

    public void BindWindowGeometry(Window window, PluginConfigFile config, string configPath)
    {
        window.PointerReleased += (_, _) =>
        {
            var snappedX = RoundToNearestTen(window.Position.X);
            var snappedY = RoundToNearestTen(window.Position.Y);
            window.Position = new PixelPoint(snappedX, snappedY);
            CaptureGeometry(window, config);
        };
        window.Resized += (_, _) => CaptureGeometry(window, config);
        window.Closed += (_, _) => Save(configPath, config);
    }

    public IReadOnlyList<string> GetActivePluginIds(PluginConfigFile mainConfig)
    {
        if (!mainConfig.Custom.TryGetValue("active_plugins", out var activePluginsElement))
            throw new InvalidOperationException(
                "Main config missing 'active_plugins' in '+' section."
            );

        if (activePluginsElement.ValueKind != JsonValueKind.Array)
            throw new InvalidOperationException("'active_plugins' must be a JSON array.");

        return activePluginsElement
            .EnumerateArray()
            .Where(x => x.ValueKind == JsonValueKind.String)
            .Select(x => x.GetString()!)
            .Where(x => !string.IsNullOrWhiteSpace(x))
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToList();
    }

    public bool GetIsDefaultPos(PluginConfigFile config)
    {
        if (config.Custom.TryGetValue("is_default_pos", out var element))
        {
            if (element.ValueKind == JsonValueKind.True)
                return true;
            if (element.ValueKind == JsonValueKind.False)
                return false;
        }
        return false;
    }

    private static void CaptureGeometry(Window window, PluginConfigFile config)
    {
        var width = window.Bounds.Width > 0 ? (int)Math.Round(window.Bounds.Width) : 250;
        config.App.Geometry =
        [
            RoundToNearestTen(window.Position.X),
            RoundToNearestTen(window.Position.Y),
            width,
            0,
        ];
    }

    private static int RoundToNearestTen(int value) => (int)Math.Round(value / 10.0) * 10;
}
