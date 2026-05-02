using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace Quol.Services;

/// <summary>
/// Service for loading and saving plugin config files.
/// Plugins store their config in a JSON file with two top-level keys:
/// "-" : metadata (id, version, description, geometry, etc.)
/// "+" : user-editable config (arbitrary JSON)
/// </summary>
public sealed class ConfigService
{
    public class ConfigData
    {
        public Dictionary<string, JsonElement> Metadata { get; set; } = [];
        public Dictionary<string, JsonElement> Settings { get; set; } = [];
    }

    /// <summary>
    /// Load config from a JSON file.
    /// Returns both metadata ("-" key) and settings ("+" key).
    /// </summary>
    public static ConfigData LoadConfig(string configPath)
    {
        if (!File.Exists(configPath))
            return new ConfigData();

        var json = File.ReadAllText(configPath);
        using var doc = JsonDocument.Parse(json);

        var data = new ConfigData();

        if (
            doc.RootElement.TryGetProperty("-", out var metaElem)
            && metaElem.ValueKind == JsonValueKind.Object
        )
        {
            foreach (var prop in metaElem.EnumerateObject())
                data.Metadata[prop.Name] = prop.Value.Clone();
        }

        if (
            doc.RootElement.TryGetProperty("+", out var settingsElem)
            && settingsElem.ValueKind == JsonValueKind.Object
        )
        {
            foreach (var prop in settingsElem.EnumerateObject())
                data.Settings[prop.Name] = prop.Value.Clone();
        }

        return data;
    }

    /// <summary>
    /// Save config back to a JSON file.
    /// </summary>
    public static void SaveConfig(string configPath, ConfigData data)
    {
        var options = new JsonSerializerOptions { WriteIndented = true };
        using var doc = JsonDocument.Parse("{}");
        var root = doc.RootElement;

        var json = JsonSerializer.Serialize(
            new
            {
                _ = (object?)null, // Placeholder; will be replaced
                plus = (object?)null, // Placeholder
            },
            options
        );

        // Manual rebuild since we need to preserve JsonElement values
        var dict = new Dictionary<string, object?>();

        if (data.Metadata.Count > 0)
        {
            var metaDict = new Dictionary<string, JsonElement>();
            foreach (var kv in data.Metadata)
                metaDict[kv.Key] = kv.Value;
            dict["-"] = metaDict;
        }
        else
        {
            dict["-"] = new Dictionary<string, JsonElement>();
        }

        if (data.Settings.Count > 0)
        {
            var settingsDict = new Dictionary<string, JsonElement>();
            foreach (var kv in data.Settings)
                settingsDict[kv.Key] = kv.Value;
            dict["+"] = settingsDict;
        }
        else
        {
            dict["+"] = new Dictionary<string, JsonElement>();
        }

        json = JsonSerializer.Serialize(dict, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(configPath, json);
    }

    /// <summary>
    /// Get a typed value from settings, with optional fallback.
    /// </summary>
    public static T? GetSetting<T>(
        Dictionary<string, JsonElement> settings,
        string key,
        T? fallback = default
    )
    {
        if (!settings.TryGetValue(key, out var elem))
            return fallback;

        try
        {
            return JsonSerializer.Deserialize<T>(elem.GetRawText());
        }
        catch
        {
            return fallback;
        }
    }

    /// <summary>
    /// Set a value in settings (in-memory; call SaveConfig to persist).
    /// </summary>
    public static void SetSetting<T>(Dictionary<string, JsonElement> settings, string key, T value)
    {
        var json = JsonSerializer.Serialize(value);
        using var doc = JsonDocument.Parse(json);
        settings[key] = doc.RootElement.Clone();
    }
}
