#include <QApplication>
#include <QCoreApplication>
#include <QFile>

#include "core/AppSettingsManager.hpp"
#include "core/InputManager.hpp"
#include "core/PluginManager.hpp"
#include "plugin_api/QuolServices.hpp"
#include "ui/QuolMainWindow.hpp"
#include "ui/TransitionManager.hpp"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    // Load settings
    const QString settingsPath = QCoreApplication::applicationDirPath() + QStringLiteral("/settings.json");
    AppSettingsManager settings(settingsPath);
    settings.load();

    // Load stylesheet
    const QString style = settings.settingString(QStringLiteral("style"), QStringLiteral("dark"));
    const QString qssPath =
        QCoreApplication::applicationDirPath() + QStringLiteral("/res/styles/") + style + QStringLiteral("/styles.qss");
    QFile qssFile(qssPath);
    if (qssFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
        app.setStyleSheet(QString::fromUtf8(qssFile.readAll()));
        qssFile.close();
    }

    // Transitions
    const QString transitionType = settings.settingString(QStringLiteral("transition"), QStringLiteral("none"));
    TransitionManager transitions(transitionType);

    // Main Quol control window
    QuolMainWindow mainWindow(&settings, &transitions);
    transitions.addWindow(&mainWindow);
    mainWindow.show();

    // Plugin windows
    InputManager inputManager;
    QuolServices services(&inputManager);
    PluginManager pluginManager;
    pluginManager.loadPlugins(&settings, &transitions, &services);
    for (auto *win : pluginManager.windows())
        win->show();

    services.setWindowVisibilityCallbacks(
        [&]() {
            mainWindow.hide();
            for (auto *w : pluginManager.windows())
                w->hide();
        },
        [&]() {
            mainWindow.show();
            for (auto *w : pluginManager.windows())
                w->show();
        }
    );

    // Global hotkey
    inputManager.start();

    QString activeToggleKey = settings.settingString(QStringLiteral("toggle_key")).toLower();
    QString mainHotkeyId = inputManager.addHotkey(
        activeToggleKey,
        [&]() {
            transitions.toggleAll();
            mainWindow.updateToggleButton();
        },
        true
    );

    QObject::connect(
        &mainWindow,
        &QuolMainWindow::mainConfigApplied,
        [&](const QString &toggleKey, bool resetPos, const QString &transitionType) {
            const QString nextToggleKey = toggleKey.toLower();
            if (nextToggleKey != activeToggleKey) {
                if (!mainHotkeyId.isEmpty()) {
                    inputManager.removeHotkey(mainHotkeyId);
                }

                mainHotkeyId = inputManager.addHotkey(
                    nextToggleKey,
                    [&]() {
                        transitions.toggleAll();
                        mainWindow.updateToggleButton();
                    },
                    true
                );
                if (!mainHotkeyId.isEmpty()) {
                    activeToggleKey = nextToggleKey;
                }
            }

            transitions.setType(transitionType);

            if (resetPos) {
                mainWindow.applyGeometryFromConfig();
                for (auto *win : pluginManager.windows()) {
                    win->applyGeometryFromConfig();
                }
            }
        }
    );

    const int exitCode = app.exec();

    if (!mainHotkeyId.isEmpty())
        inputManager.removeHotkey(mainHotkeyId);

    return exitCode;
}
