using System;
using System.Diagnostics;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace Quol.ViewModels;

public partial class MainWindowViewModel : ObservableObject
{
    public string PluginName { get; }
    public bool ShowConfigButton { get; } = true;
    public string VersionText { get; }
    public string VersionTooltip { get; }

    public MainWindowViewModel()
        : this("Quol", "0.1.0") { }

    public MainWindowViewModel(string pluginName, string version)
    {
        PluginName = pluginName;
        VersionText = $"v{version}";
        VersionTooltip = $"Check version on GitHub ({VersionText})";
    }

    [RelayCommand]
    private void ManagePlugins()
    {
        // Placeholder for upcoming plugin manager window.
    }

    [RelayCommand]
    private static void OpenReleases()
    {
        Process.Start(
            new ProcessStartInfo
            {
                FileName = "https://github.com/LeoCh01/Quol/releases/latest",
                UseShellExecute = true,
            }
        );
    }

    [RelayCommand]
    private static void OpenProjectFolder()
    {
        Process.Start(
            new ProcessStartInfo { FileName = AppContext.BaseDirectory, UseShellExecute = true }
        );
    }

    [RelayCommand]
    private void Reload()
    {
        // Placeholder for upcoming app reload.
    }

    [RelayCommand]
    private void Quit()
    {
        if (
            Avalonia.Application.Current?.ApplicationLifetime
            is Avalonia.Controls.ApplicationLifetimes.IClassicDesktopStyleApplicationLifetime desktop
        )
            desktop.Shutdown();
    }
}
