#include <QApplication>
#include <QCoreApplication>
#include <QFile>
#include <QIcon>
#include <QMenu>
#include <QProcess>
#include <QSystemTrayIcon>

#include "core/AppSettingsManager.hpp"
#include "core/InputManager.hpp"
#include "core/PluginManager.hpp"
#include "plugin_api/QuolServices.hpp"
#include "ui/QuolMainWindow.hpp"
#include "ui/TransitionManager.hpp"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    const QString appDir = QCoreApplication::applicationDirPath();
    const QString appIconPath = appDir + QStringLiteral("/res/icon.ico");
    if (QFile::exists(appIconPath)) {
        app.setWindowIcon(QIcon(appIconPath));
    }

    // Load settings
    const QString settingsPath = appDir + QStringLiteral("/settings.json");
    AppSettingsManager settings(settingsPath);
    settings.load();

    // Load stylesheet
    const QString style = settings.settingString(QStringLiteral("style"), QStringLiteral("dark"));
    const QString qssPath = appDir + QStringLiteral("/res/styles/") + style + QStringLiteral("/styles.qss");
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

    // System tray icon + menu
    // "ON" = windows visible + hotkey active. "OFF" = everything hidden + hotkey removed.
    QSystemTrayIcon trayIcon;
    QMenu trayMenu;
    QAction *toggleAction = nullptr;
    bool quolOn = true;

    auto setQuolOn = [&](bool on) {
        quolOn = on;

        if (on) {
            mainWindow.show();
            for (auto *w : pluginManager.windows())
                w->show();
            if (mainHotkeyId.isEmpty())
                mainHotkeyId = inputManager.addHotkey(
                    activeToggleKey,
                    [&]() {
                        transitions.toggleAll();
                        mainWindow.updateToggleButton();
                    },
                    true
                );
        } else {
            // Ensure windows are fully shown before hiding (cancel any transition)
            if (transitions.isHidden())
                transitions.toggleAll();
            mainWindow.hide();
            for (auto *w : pluginManager.windows())
                w->hide();
            if (!mainHotkeyId.isEmpty()) {
                inputManager.removeHotkey(mainHotkeyId);
                mainHotkeyId.clear();
            }
        }

        if (toggleAction)
            toggleAction->setText(on ? QStringLiteral("Turn OFF") : QStringLiteral("Turn ON"));
        trayIcon.setToolTip(on ? QStringLiteral("Quol — ON") : QStringLiteral("Quol — OFF"));
    };

    if (QSystemTrayIcon::isSystemTrayAvailable()) {
        trayIcon.setIcon(app.windowIcon());
        trayIcon.setToolTip(QStringLiteral("Quol — ON"));

        toggleAction = trayMenu.addAction(QStringLiteral("Turn OFF"));
        QAction *reloadAction = trayMenu.addAction(QStringLiteral("Reload"));
        trayMenu.addSeparator();
        QAction *quitAction = trayMenu.addAction(QStringLiteral("Quit"));

        QObject::connect(toggleAction, &QAction::triggered, [&]() { setQuolOn(!quolOn); });

        QObject::connect(&trayIcon, &QSystemTrayIcon::activated, [&](QSystemTrayIcon::ActivationReason reason) {
            if (reason == QSystemTrayIcon::Trigger)
                setQuolOn(!quolOn);
        });

        QObject::connect(reloadAction, &QAction::triggered, [&]() {
            trayIcon.hide();
            QProcess::startDetached(QCoreApplication::applicationFilePath());
            QCoreApplication::quit();
        });

        QObject::connect(quitAction, &QAction::triggered, [&]() {
            trayIcon.hide();
            QApplication::quit();
        });

        trayIcon.setContextMenu(&trayMenu);
        trayIcon.show();
    }

    QObject::connect(
        &mainWindow,
        &QuolMainWindow::mainConfigApplied,
        [&](const QString &toggleKey, bool resetPos, const QString &newTransitionType) {
            const QString nextKey = toggleKey.toLower();
            if (nextKey != activeToggleKey) {
                if (!mainHotkeyId.isEmpty())
                    inputManager.removeHotkey(mainHotkeyId);
                activeToggleKey = nextKey;
                if (quolOn)
                    mainHotkeyId = inputManager.addHotkey(
                        activeToggleKey,
                        [&]() {
                            transitions.toggleAll();
                            mainWindow.updateToggleButton();
                        },
                        true
                    );
            }

            transitions.setType(newTransitionType);

            if (resetPos) {
                mainWindow.applyGeometryFromConfig();
                for (auto *win : pluginManager.windows())
                    win->applyGeometryFromConfig();
            }
        }
    );

    const int exitCode = app.exec();

    if (!mainHotkeyId.isEmpty())
        inputManager.removeHotkey(mainHotkeyId);

    return exitCode;
}
