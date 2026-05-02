using System;
using System.Collections.Generic;
using System.Text.Json;

namespace Quol.Plugins;

/// <summary>
/// Extension methods for reading typed values from a plugin config dictionary.
/// </summary>
public static class PluginConfigExtensions
{
    /// <summary>
    /// Get a typed value directly from the config. Throws if key is missing or type mismatch.
    /// Supported types: string, bool, int, double, float, JsonElement.
    /// </summary>
    public static T Cfg<T>(this Dictionary<string, JsonElement> config, string key)
    {
        var elem = config[key];
        object result = typeof(T) switch
        {
            var t when t == typeof(string) => elem.GetString()!,
            var t when t == typeof(bool) => (object)elem.GetBoolean(),
            var t when t == typeof(int) => (object)elem.GetInt32(),
            var t when t == typeof(double) => (object)elem.GetDouble(),
            var t when t == typeof(float) => (object)(float)elem.GetDouble(),
            var t when t == typeof(JsonElement) => (object)elem,
            _ => throw new InvalidOperationException($"Unsupported config type {typeof(T).Name}"),
        };
        return (T)result;
    }
}
