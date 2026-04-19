using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Quol.Models;

public class PluginConfigFile
{
    [JsonPropertyName("-")]
    public PluginAppSection App { get; set; } = new();

    [JsonPropertyName("+")]
    public Dictionary<string, JsonElement> Custom { get; set; } = new();
}

public class PluginAppSection
{
    [JsonPropertyName("id")]
    public string? Id { get; set; }

    [JsonPropertyName("version")]
    public string Version { get; set; } = "0.1.0";

    [JsonPropertyName("description")]
    public string Description { get; set; } = "Plugin";

    [JsonPropertyName("default_geometry")]
    public int[] DefaultGeometry { get; set; } = [40, 40, 250, 250];

    [JsonPropertyName("geometry")]
    public int[] Geometry { get; set; } = [40, 40, 250, 250];
}
