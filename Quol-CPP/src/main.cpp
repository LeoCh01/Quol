#include <QApplication>
#include <QCoreApplication>
#include <QFile>

#include "core/AppSettingsManager.hpp"
#include "core/InputManager.hpp"
#include "core/PluginManager.hpp"
#include "ui/QuolMainWindow.hpp"
#include "ui/TransitionManager.hpp"

int main(int argc, char* argv[])
{
    QApplication app(argc, argv);

    // Load settings
    const QString settingsPath = QCoreApplication::applicationDirPath() + "/settings.json";
    AppSettingsManager settings(settingsPath);
    settings.load();

    // Load stylesheet
    const QString style = settings.settingString("style", "dark");
    const QString qssPath = QCoreApplication::applicationDirPath()
        + "/res/styles/" + style + "/styles.qss";
    QFile qssFile(qssPath);
    if (qssFile.open(QIODevice::ReadOnly | QIODevice::Text))
    {
        app.setStyleSheet(QString::fromUtf8(qssFile.readAll()));
        qssFile.close();
    }

    // Transitions
    const QString transitionType = settings.settingString("transition", "none");
    TransitionManager transitions(transitionType);

    // Main Quol control window
    QuolMainWindow mainWindow(&settings, &transitions);
    transitions.addWindow(&mainWindow);
    mainWindow.show();

    // Plugin windows
    PluginManager pluginManager;
    pluginManager.loadPlugins(&settings, &transitions);
    for (auto* win : pluginManager.windows())
        win->show();

    // Global hotkey
    InputManager inputManager;
    inputManager.start();

    const QString toggleKey = settings.settingString("toggle_key", "`").toLower();
    const int hotkeyId = inputManager.addHotkey(toggleKey, true);

    QObject::connect(&inputManager, &InputManager::hotkeyTriggered,
        [&](const QString& combo) {
            if (combo == toggleKey)
            {
                transitions.toggleAll();
                mainWindow.updateToggleButton();
            }
        });

    const int exitCode = app.exec();

    if (hotkeyId >= 0)
        inputManager.removeHotkey(hotkeyId);

    return exitCode;
}
