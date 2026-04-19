using System;
using Avalonia.Controls;
using Avalonia.Platform;

namespace Quol.Assets;

public static class QuolWindowIcons
{
    private static readonly Lazy<WindowIcon> AppIconLazy = new(() =>
    {
        using var stream = AssetLoader.Open(new Uri("avares://Quol/Assets/Icons/icon.ico"));
        return new WindowIcon(stream);
    });

    public static WindowIcon AppIcon => AppIconLazy.Value;
}
