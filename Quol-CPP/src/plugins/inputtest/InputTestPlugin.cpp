#include "plugins/inputtest/InputTestPlugin.hpp"

#include "core/InputManager.hpp"

#include <QJsonArray>
#include <QJsonObject>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QVBoxLayout>
#include <QWidget>

QWidget *InputTestPlugin::createWidget(QWidget *parent) {
    auto *widget = new QWidget(parent);
    auto *layout = new QVBoxLayout(widget);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setAlignment(Qt::AlignTop);

    const QString configHotkey = m_pluginConfig.value("hotkey").toVariant().toString().trimmed().toLower();
    const QString hotkey = configHotkey.isEmpty() ? "ctrl+f9" : configHotkey;

    const QString configSend = m_pluginConfig.value("send_combo").toVariant().toString().trimmed().toLower();
    const QString sendCombo = configSend.isEmpty() ? "ctrl+a" : configSend;

    m_hotkeyLabel = new QLabel(QString("Hotkey: %1").arg(hotkey), widget);
    m_pressedLabel = new QLabel("Key down: (none)", widget);
    m_releasedLabel = new QLabel("Key up: (none)", widget);
    m_triggeredLabel = new QLabel("Triggered: (none)", widget);
    m_availableKeysLabel = new QLabel(widget);
    m_availableKeysLabel->setWordWrap(true);

    m_sendComboEdit = new QLineEdit(widget);
    m_sendComboEdit->setPlaceholderText("combo (example: ctrl+a)");
    m_sendComboEdit->setText(sendCombo);

    auto *sendKeysBtn = new QPushButton("Send keys", widget);
    auto *sendPressBtn = new QPushButton("Send press", widget);
    auto *sendReleaseBtn = new QPushButton("Send release", widget);

    layout->addWidget(m_hotkeyLabel);
    layout->addWidget(m_pressedLabel);
    layout->addWidget(m_releasedLabel);
    layout->addWidget(m_triggeredLabel);
    layout->addWidget(m_sendComboEdit);
    layout->addWidget(sendKeysBtn);
    layout->addWidget(sendPressBtn);
    layout->addWidget(sendReleaseBtn);
    layout->addWidget(m_availableKeysLabel);

    m_inputManager = new InputManager(widget);

    QObject::connect(m_inputManager, &InputManager::keyPressed, widget, [this](const QString &key) {
        if (m_pressedLabel) {
            m_pressedLabel->setText(QString("Key down: %1").arg(key));
        }
    });

    QObject::connect(m_inputManager, &InputManager::keyReleased, widget, [this](const QString &key) {
        if (m_releasedLabel) {
            m_releasedLabel->setText(QString("Key up: %1").arg(key));
        }
    });

    QObject::connect(m_inputManager, &InputManager::hotkeyTriggered, widget, [this](const QString &combo) {
        if (m_triggeredLabel) {
            m_triggeredLabel->setText(QString("Triggered: %1").arg(combo));
        }
    });

    QObject::connect(sendKeysBtn, &QPushButton::clicked, widget, [this]() {
        m_inputManager->sendKeys(m_sendComboEdit->text().trimmed().toLower());
    });

    QObject::connect(sendPressBtn, &QPushButton::clicked, widget, [this]() {
        m_inputManager->sendPress(m_sendComboEdit->text().trimmed().toLower());
    });

    QObject::connect(sendReleaseBtn, &QPushButton::clicked, widget, [this]() {
        m_inputManager->sendRelease(m_sendComboEdit->text().trimmed().toLower());
    });

    const QStringList available = m_inputManager->availableKeys();
    const int previewCount = available.size() < 40 ? available.size() : 40;
    m_availableKeysLabel->setText(
        QString("Available keys (%1): %2").arg(available.size()).arg(available.mid(0, previewCount).join(", "))
    );

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

    if (m_sendComboEdit) {
        const QString sendCombo = m_pluginConfig.value("send_combo").toVariant().toString().trimmed().toLower();
        if (!sendCombo.isEmpty()) {
            m_sendComboEdit->setText(sendCombo);
        }
    }

    applyHotkeyFromConfig();
}

void InputTestPlugin::shutdown() {
    if (m_inputManager && m_hotkeyId >= 0) {
        m_inputManager->removeHotkey(m_hotkeyId);
        m_hotkeyId = -1;
    }
}

void InputTestPlugin::applyHotkeyFromConfig() {
    if (!m_inputManager) {
        return;
    }

    const QString configured = m_pluginConfig.value("hotkey").toVariant().toString().trimmed().toLower();
    const QString combo = configured.isEmpty() ? "ctrl+f9" : configured;

    if (m_hotkeyId >= 0) {
        m_inputManager->removeHotkey(m_hotkeyId);
        m_hotkeyId = -1;
    }

    m_hotkeyId = m_inputManager->addHotkey(combo, true);

    if (m_hotkeyLabel) {
        if (m_hotkeyId >= 0) {
            m_hotkeyLabel->setText(QString("Hotkey: %1").arg(combo));
        } else {
            m_hotkeyLabel->setText(QString("Hotkey registration failed: %1").arg(combo));
        }
    }
}
