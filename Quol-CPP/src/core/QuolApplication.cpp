#include "core/QuolApplication.hpp"
#include "core/AppSettingsManager.hpp"
#include "core/InputManager.hpp"
#include "core/PluginManager.hpp"
#include "plugin_api/QuolServices.hpp"
#include "ui/QuolMainWindow.hpp"
#include "ui/TransitionManager.hpp"

#include <QAction>
#include <QApplication>
#include <QDebug>
#include <QMenu>
#include <QProcess>
#include <QSystemTrayIcon>

QuolApplication::QuolApplication(AppSettingsManager *settings, QObject *parent)
    : QObject(parent), m_settings(settings) {
    const QString transitionType = m_settings->settingString(QStringLiteral("transition"), QStringLiteral("none"));
    m_transitions = new TransitionManager(transitionType, this);
    m_mainWindow = new QuolMainWindow(m_settings, m_transitions);
    m_inputManager = new InputManager(this);
    m_services = std::make_unique<QuolServices>(m_inputManager);
    m_pluginManager = new PluginManager(this);
}

QuolApplication::~QuolApplication() {
    performShutdown();
}

void QuolApplication::start() {
    qInfo() << "Starting QuolApplication";
    m_transitions->addWindow(m_mainWindow);
    m_mainWindow->show();

    m_pluginManager->loadPlugins(m_settings, m_transitions, m_services.get());
    for (auto *win : m_pluginManager->windows())
        win->show();

    m_services->setWindowVisibilityCallbacks(
        [this]() {
            m_mainWindow->hide();
            for (auto *w : m_pluginManager->windows())
                w->hide();
        },
        [this]() {
            m_mainWindow->show();
            for (auto *w : m_pluginManager->windows())
                w->show();
        }
    );

    m_inputManager->start();
    m_activeToggleKey = m_settings->settingString(QStringLiteral("toggle_key")).toLower();
    m_mainHotkeyId = registerMainHotkey();

    setupTrayIcon();

    connect(m_mainWindow, &QuolMainWindow::mainConfigApplied, this, &QuolApplication::onMainConfigApplied);
    connect(qApp, &QCoreApplication::aboutToQuit, this, [this]() { performShutdown(); });
}

QString QuolApplication::registerMainHotkey() {
    return m_inputManager->addHotkey(
        m_activeToggleKey,
        [this]() {
            m_transitions->toggleAll();
            m_mainWindow->updateToggleButton();
        },
        true
    );
}

void QuolApplication::performShutdown() {
    if (m_shutdownDone)
        return;
    m_shutdownDone = true;
    qInfo() << "Shutting down QuolApplication";

    if (!m_mainHotkeyId.isEmpty()) {
        m_inputManager->removeHotkey(m_mainHotkeyId);
        m_mainHotkeyId.clear();
    }

    m_pluginManager->shutdownPlugins();
    m_inputManager->stop();

    delete m_mainWindow;
    m_mainWindow = nullptr;
}

void QuolApplication::setQuolOn(bool on) {
    m_quolOn = on;

    if (on) {
        m_mainWindow->show();
        for (auto *w : m_pluginManager->windows())
            w->show();
        if (m_mainHotkeyId.isEmpty())
            m_mainHotkeyId = registerMainHotkey();
    } else {
        // Cancel any in-progress hide transition before hiding
        if (m_transitions->isHidden())
            m_transitions->toggleAll();
        m_mainWindow->hide();
        for (auto *w : m_pluginManager->windows())
            w->hide();
        if (!m_mainHotkeyId.isEmpty()) {
            m_inputManager->removeHotkey(m_mainHotkeyId);
            m_mainHotkeyId.clear();
        }
    }

    if (m_toggleAction)
        m_toggleAction->setText(on ? QStringLiteral("Turn OFF") : QStringLiteral("Turn ON"));
    if (m_trayIcon)
        m_trayIcon->setToolTip(on ? QStringLiteral("Quol — ON") : QStringLiteral("Quol — OFF"));
}

void QuolApplication::setupTrayIcon() {
    if (!QSystemTrayIcon::isSystemTrayAvailable())
        return;

    m_trayMenu = std::make_unique<QMenu>();
    m_toggleAction = m_trayMenu->addAction(QStringLiteral("Turn OFF"));
    QAction *reloadAction = m_trayMenu->addAction(QStringLiteral("Reload"));
    m_trayMenu->addSeparator();
    QAction *quitAction = m_trayMenu->addAction(QStringLiteral("Quit"));

    m_trayIcon = new QSystemTrayIcon(qApp->windowIcon(), this);
    m_trayIcon->setToolTip(QStringLiteral("Quol — ON"));
    m_trayIcon->setContextMenu(m_trayMenu.get());

    connect(m_toggleAction, &QAction::triggered, this, [this]() { setQuolOn(!m_quolOn); });

    connect(m_trayIcon, &QSystemTrayIcon::activated, this, [this](QSystemTrayIcon::ActivationReason reason) {
        if (reason == QSystemTrayIcon::Trigger)
            setQuolOn(!m_quolOn);
    });

    connect(reloadAction, &QAction::triggered, this, [this]() {
        m_trayIcon->hide();
        performShutdown();
        QProcess::startDetached(QCoreApplication::applicationFilePath());
        QCoreApplication::quit();
    });

    connect(quitAction, &QAction::triggered, this, [this]() {
        m_trayIcon->hide();
        performShutdown();
        QApplication::quit();
    });

    m_trayIcon->show();
}

void QuolApplication::onMainConfigApplied(const QString &toggleKey, bool resetPos, const QString &newTransitionType) {
    const QString nextKey = toggleKey.toLower();
    if (nextKey != m_activeToggleKey) {
        if (!m_mainHotkeyId.isEmpty())
            m_inputManager->removeHotkey(m_mainHotkeyId);
        m_activeToggleKey = nextKey;
        if (m_quolOn)
            m_mainHotkeyId = registerMainHotkey();
    }

    m_transitions->setType(newTransitionType);

    if (resetPos) {
        m_mainWindow->applyGeometryFromConfig();
        for (auto *win : m_pluginManager->windows())
            win->applyGeometryFromConfig();
    }
}
