#include "plugins/inputTest/InputTest.hpp"

#include "core/InputManager.hpp"
#include "plugin_api/QuolServices.hpp"

#include <QJsonObject>
#include <QLabel>
#include <QVBoxLayout>
#include <QWidget>

QWidget *InputTest::createWidget(QWidget *parent) {
    auto *widget = new QWidget(parent);
    auto *layout = new QVBoxLayout(widget);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setAlignment(Qt::AlignTop);

    m_pressedLabel = new QLabel("Key down: (none)", widget);
    m_releasedLabel = new QLabel("Key up: (none)", widget);
    m_triggeredLabel = new QLabel("Triggered: (none)", widget);

    layout->addWidget(m_pressedLabel);
    layout->addWidget(m_releasedLabel);
    layout->addWidget(m_triggeredLabel);

    return widget;
}

void InputTest::initialize(const QString &pluginRootPath, const QJsonObject &pluginConfig, QuolServices *services) {
    m_pluginRootPath = pluginRootPath;
    m_pluginConfig = pluginConfig;
    m_services = services;

    if (m_services && m_services->inputManager()) {
        m_keyListenId = m_services->inputManager()->addKeyListener([this](const QString &key, bool pressed) {
            if (pressed) {
                if (m_pressedLabel)
                    m_pressedLabel->setText(QStringLiteral("Key down: ") + key);
            } else {
                if (m_releasedLabel)
                    m_releasedLabel->setText(QStringLiteral("Key up: ") + key);
            }
        });
    }

    applyHotkeyFromConfig();
}

void InputTest::onUpdateConfig(const QJsonObject &pluginConfig) {
    m_pluginConfig = pluginConfig;
    applyHotkeyFromConfig();
}

void InputTest::shutdown() {
    if (m_services && m_services->inputManager()) {
        if (!m_hotkeyId.isEmpty()) {
            m_services->inputManager()->removeHotkey(m_hotkeyId);
            m_hotkeyId.clear();
        }
        if (!m_keyListenId.isEmpty()) {
            m_services->inputManager()->removeKeyListener(m_keyListenId);
            m_keyListenId.clear();
        }
    }
}

void InputTest::applyHotkeyFromConfig() {
    if (!m_services || !m_services->inputManager()) {
        return;
    }

    const QString combo = m_pluginConfig.value("send_combo").toString().trimmed().toLower();

    if (!m_hotkeyId.isEmpty()) {
        m_services->inputManager()->removeHotkey(m_hotkeyId);
        m_hotkeyId.clear();
    }

    if (combo.isEmpty()) {
        return;
    }

    m_hotkeyId = m_services->inputManager()->addHotkey(
        combo,
        [this, combo]() {
            if (m_triggeredLabel)
                m_triggeredLabel->setText(QStringLiteral("Triggered: ") + combo);
        },
        true
    );
}
