#include "plugins/inputtest/InputTestPlugin.hpp"

#include "core/InputManager.hpp"

#include <QJsonArray>
#include <QJsonObject>
#include <QLabel>
#include <QVBoxLayout>
#include <QWidget>

QWidget *InputTestPlugin::createWidget(QWidget *parent) {
    auto *widget = new QWidget(parent);
    auto *layout = new QVBoxLayout(widget);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setAlignment(Qt::AlignTop);

    const QString configHotkey = m_pluginConfig.value("hotkey").toVariant().toString().trimmed().toLower();
    const QString hotkey = configHotkey.isEmpty() ? "ctrl+f9" : configHotkey;

    m_pressedLabel = new QLabel("Key down: (none)", widget);
    m_releasedLabel = new QLabel("Key up: (none)", widget);
    m_triggeredLabel = new QLabel("Triggered: (none)", widget);

    layout->addWidget(m_pressedLabel);
    layout->addWidget(m_releasedLabel);
    layout->addWidget(m_triggeredLabel);
    m_inputManager = new InputManager(widget);

    QObject::connect(m_inputManager, &InputManager::keyPressed, widget, [this](const QString &key) {
        m_pressedLabel->setText(QString("Key down: %1").arg(key));
    });

    QObject::connect(m_inputManager, &InputManager::keyReleased, widget, [this](const QString &key) {
        m_releasedLabel->setText(QString("Key up: %1").arg(key));
    });

    QObject::connect(m_inputManager, &InputManager::hotkeyTriggered, widget, [this](const QString &combo) {
        m_triggeredLabel->setText(QString("Triggered: %1").arg(combo));
    });

    applyHotkeyFromConfig();

    return widget;
}

void InputTestPlugin::initialize(
    const QString &pluginRootPath, const QJsonObject &appSettings, const QJsonObject &pluginConfig
) {
    m_pluginRootPath = pluginRootPath;
    m_appSettings = appSettings;
    m_pluginConfig = pluginConfig;
}

void InputTestPlugin::onUpdateConfig(const QJsonObject &pluginConfig) {
    m_pluginConfig = pluginConfig;

    applyHotkeyFromConfig();
}

void InputTestPlugin::shutdown() {
    if (m_inputManager) {
        m_inputManager->removeHotkey(m_hotkeyId);
    }
}

void InputTestPlugin::applyHotkeyFromConfig() {
    if (!m_inputManager) {
        return;
    }

    const QString combo = m_pluginConfig.value("send_combo").toVariant().toString().trimmed().toLower();

    m_inputManager->removeHotkey(m_hotkeyId);

    const bool ok = m_inputManager->addHotkey(m_hotkeyId, combo, true);
}
