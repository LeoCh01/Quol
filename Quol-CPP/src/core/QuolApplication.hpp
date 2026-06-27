#pragma once

#include <QObject>
#include <QString>
#include <memory>

class AppSettingsManager;
class TransitionManager;
class QuolMainWindow;
class InputManager;
class QuolServices;
class PluginManager;
class QSystemTrayIcon;
class QAction;
class QMenu;

// QuolApplication owns and coordinates all runtime components:
// the main window, plugin manager, input/hotkey system, and system tray.
class QuolApplication : public QObject {
    Q_OBJECT

public:
    explicit QuolApplication(AppSettingsManager *settings, QObject *parent = nullptr);
    ~QuolApplication() override;

    void start();

private slots:
    void onMainConfigApplied(const QString &toggleKey, bool resetPos, const QString &transitionType);

private:
    void setupTrayIcon();
    void setQuolOn(bool on);
    void performShutdown();
    QString registerMainHotkey();

    AppSettingsManager *m_settings;
    TransitionManager *m_transitions = nullptr;
    QuolMainWindow *m_mainWindow = nullptr;
    InputManager *m_inputManager = nullptr;
    std::unique_ptr<QuolServices> m_services;
    PluginManager *m_pluginManager = nullptr;

    QSystemTrayIcon *m_trayIcon = nullptr;
    std::unique_ptr<QMenu> m_trayMenu;
    QAction *m_toggleAction = nullptr;

    QString m_activeToggleKey;
    QString m_mainHotkeyId;
    bool m_quolOn = true;
    bool m_shutdownDone = false;
};
