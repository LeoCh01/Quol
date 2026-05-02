using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;

namespace Quol.Views.Controls;

/// <summary>
/// Auto-generates config UI from a dictionary of JsonElement settings.
/// Supports: string, number, boolean, array (ComboBox), and nested object (GroupBox).
/// Layout: Horizontal rows with label on left and control on right.
/// </summary>
public static class ConfigWindowBuilder
{
    /// <summary>
    /// Build a control tree from config settings.
    /// Returns a StackPanel with horizontal rows for each setting.
    /// </summary>
    public static StackPanel BuildConfigPanel(
        Dictionary<string, JsonElement> settings,
        Action<string, JsonElement>? onValueChanged = null
    )
    {
        var panel = new StackPanel
        {
            Spacing = 5,
            Margin = new Thickness(0),
            Orientation = Orientation.Vertical,
        };

        foreach (var (key, value) in settings.OrderBy(kv => kv.Key))
            panel.Children.Add(BuildItem(key, value, onValueChanged));

        return panel;
    }

    // Dispatch: objects become group boxes, everything else becomes a row
    private static Control BuildItem(
        string key,
        JsonElement value,
        Action<string, JsonElement>? onValueChanged
    )
    {
        if (value.ValueKind == JsonValueKind.Object)
            return BuildGroupBox(key, value, onValueChanged);

        return BuildConfigRow(key, value, onValueChanged);
    }

    // Nested object → titled border with inner rows (white outline, no fill)
    private static Control BuildGroupBox(
        string key,
        JsonElement value,
        Action<string, JsonElement>? onValueChanged
    )
    {
        var innerPanel = new StackPanel
        {
            Spacing = 3,
            Orientation = Orientation.Vertical,
            HorizontalAlignment = HorizontalAlignment.Stretch,
        };

        var currentObject = new Dictionary<string, JsonElement>();
        foreach (var p in value.EnumerateObject())
            currentObject[p.Name] = p.Value;

        foreach (var prop in value.EnumerateObject())
        {
            void Relay(string k, JsonElement v)
            {
                currentObject[k] = v;
                using var doc = JsonDocument.Parse(
                    System.Text.Json.JsonSerializer.Serialize(currentObject)
                );
                onValueChanged?.Invoke(key, doc.RootElement.Clone());
            }

            innerPanel.Children.Add(
                BuildItem(prop.Name, prop.Value, onValueChanged is not null ? Relay : null)
            );
        }

        return new GroupBox
        {
            Margin = new Thickness(0),
            Padding = new Thickness(0),
            Header = new Border
            {
                Margin = new Thickness(-6, 0, 0, 0),
                Padding = new Thickness(4, 1, 4, 1),
                Child = new TextBlock
                {
                    Text = FormatLabel(key),
                    Margin = new Thickness(0),
                    VerticalAlignment = VerticalAlignment.Center,
                },
            },
            Content = innerPanel,
        };
    }

    private static Control BuildConfigRow(
        string key,
        JsonElement value,
        Action<string, JsonElement>? onValueChanged
    )
    {
        var row = new Grid
        {
            Margin = new Thickness(0),
            ColumnDefinitions = new ColumnDefinitions("120,*"),
            ColumnSpacing = 8,
        };

        var label = new TextBlock
        {
            Text = FormatLabel(key),
            VerticalAlignment = VerticalAlignment.Center,
        };
        Grid.SetColumn(label, 0);
        row.Children.Add(label);

        var input = BuildInputControl(key, value, onValueChanged);
        Grid.SetColumn(input, 1);
        row.Children.Add(input);

        return row;
    }

    private static Control BuildInputControl(
        string key,
        JsonElement value,
        Action<string, JsonElement>? onValueChanged
    )
    {
        return value.ValueKind switch
        {
            JsonValueKind.String => BuildStringInput(key, value, onValueChanged),
            JsonValueKind.Number => BuildNumberInput(key, value, onValueChanged),
            JsonValueKind.True or JsonValueKind.False => BuildBooleanInput(
                key,
                value,
                onValueChanged
            ),
            JsonValueKind.Array => BuildArrayInput(key, value, onValueChanged),
            _ => new TextBlock { Text = value.GetRawText() },
        };
    }

    private static TextBox BuildStringInput(
        string key,
        JsonElement value,
        Action<string, JsonElement>? onValueChanged
    )
    {
        var originalValue = value.GetString() ?? "";
        var textBox = new TextBox { Text = originalValue };

        if (onValueChanged is not null)
        {
            textBox.LostFocus += (_, _) =>
            {
                if (textBox.Text != originalValue)
                {
                    using var doc = JsonDocument.Parse($"\"{textBox.Text}\"");
                    onValueChanged(key, doc.RootElement.Clone());
                }
            };
        }

        return textBox;
    }

    private static TextBox BuildNumberInput(
        string key,
        JsonElement value,
        Action<string, JsonElement>? onValueChanged
    )
    {
        var originalValue = value.GetRawText();
        var textBox = new TextBox { Text = originalValue };

        if (onValueChanged is not null)
        {
            textBox.LostFocus += (_, _) =>
            {
                if (double.TryParse(textBox.Text, out var num) && num.ToString() != originalValue)
                {
                    using var doc = JsonDocument.Parse(num.ToString());
                    onValueChanged(key, doc.RootElement.Clone());
                }
            };
        }

        return textBox;
    }

    private static Control BuildBooleanInput(
        string key,
        JsonElement value,
        Action<string, JsonElement>? onValueChanged
    )
    {
        var originalValue = value.GetBoolean();
        var checkBox = new CheckBox
        {
            IsChecked = originalValue,
            VerticalAlignment = VerticalAlignment.Center,
        };

        if (onValueChanged is not null)
        {
            checkBox.IsCheckedChanged += (_, _) =>
            {
                var newVal = checkBox.IsChecked ?? false;
                if (newVal != originalValue)
                {
                    using var doc = JsonDocument.Parse(newVal.ToString().ToLowerInvariant());
                    onValueChanged(key, doc.RootElement.Clone());
                }
            };
        }

        return checkBox;
    }

    private static Control BuildArrayInput(
        string key,
        JsonElement value,
        Action<string, JsonElement>? onValueChanged
    )
    {
        // Handle arrays - typically [options, currentIndex] format for ComboBox
        // Format: [["option1", "option2", ...], currentIndex]
        try
        {
            var arrayLen = value.GetArrayLength();

            // Check if it's [options_array, selected_index] format (like Python)
            if (arrayLen == 2)
            {
                var first = value[0];
                var second = value[1];

                if (
                    first.ValueKind == JsonValueKind.Array
                    && second.ValueKind == JsonValueKind.Number
                )
                {
                    var options = new List<string>();
                    foreach (var opt in first.EnumerateArray())
                    {
                        if (opt.ValueKind == JsonValueKind.String)
                            options.Add(opt.GetString() ?? "");
                        else
                            options.Add(opt.GetRawText());
                    }

                    var selectedIndex = Math.Max(
                        0,
                        Math.Min((int)second.GetDouble(), options.Count - 1)
                    );
                    var comboBox = new ComboBox
                    {
                        ItemsSource = options,
                        SelectedIndex = selectedIndex,
                        HorizontalAlignment = HorizontalAlignment.Stretch,
                        Height = 36,
                        MinHeight = 36,
                        Padding = new Thickness(6, 0),
                        VerticalContentAlignment = VerticalAlignment.Center,
                    };

                    if (onValueChanged is not null)
                    {
                        comboBox.SelectionChanged += (_, _) =>
                        {
                            if (comboBox.SelectedIndex >= 0)
                            {
                                var payload = new object[] { options, comboBox.SelectedIndex };
                                using var doc = JsonDocument.Parse(
                                    System.Text.Json.JsonSerializer.Serialize(payload)
                                );
                                onValueChanged(key, doc.RootElement.Clone());
                            }
                        };
                    }

                    return comboBox;
                }
            }

            // Fallback: just show as text
            return new TextBlock
            {
                Text = $"[array with {arrayLen} items]",
                VerticalAlignment = VerticalAlignment.Center,
            };
        }
        catch
        {
            return new TextBlock { Text = "[array]", VerticalAlignment = VerticalAlignment.Center };
        }
    }

    private static string FormatLabel(string key)
    {
        // Convert snake_case or camelCase to Title Case
        var formatted = System
            .Text.RegularExpressions.Regex.Replace(key, @"([a-z])([A-Z])|_", "$1 $2")
            .Trim();

        // Capitalize first letter
        return char.ToUpper(formatted[0]) + formatted.Substring(1);
    }
}
