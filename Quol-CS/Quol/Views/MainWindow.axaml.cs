using Avalonia;
using Avalonia.Controls;
using Quol.Assets;
using Quol.Models;
using Quol.Services;
using Quol.ViewModels;

namespace Quol.Views;

public partial class MainWindow : Window
{
    private readonly PluginConfigService _pluginConfigService = new();
    private readonly PluginConfigFile _mainConfig;
    private readonly string _mainConfigPath;

    public MainWindow()
    {
        InitializeComponent();
        Icon = QuolWindowIcons.AppIcon;

        _mainConfigPath = _pluginConfigService.GetMainConfigPath();
        _mainConfig = _pluginConfigService.LoadMainConfig();

        _pluginConfigService.ApplyWindowGeometry(this, _mainConfig);
        _pluginConfigService.BindWindowGeometry(this, _mainConfig, _mainConfigPath);

        DataContext = new MainWindowViewModel(_mainConfig.App.Description, _mainConfig.App.Version);
    }
}
