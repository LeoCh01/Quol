#include "plugins/example/Example.hpp"
#include "plugins/example/lib/adder.hpp"

#include "core/InputManager.hpp"
#include "plugin_api/QuolServices.hpp"

#include <QLabel>
#include <QVBoxLayout>
#include <QWidget>

QWidget *Example::createWidget(QWidget *parent) {
    auto *widget = new QWidget(parent);
    auto *layout = new QVBoxLayout(widget);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setAlignment(Qt::AlignTop);

    m_titleLabel = new QLabel(widget);
    m_titleLabel->setWordWrap(true);
    layout->addWidget(m_titleLabel);

    m_valueLabel = new QLabel(widget);
    m_valueLabel->setWordWrap(true);
    layout->addWidget(m_valueLabel);

    m_nestedNoteLabel = new QLabel(widget);
    m_nestedNoteLabel->setWordWrap(true);
    layout->addWidget(m_nestedNoteLabel);

    m_nestedEnabledLabel = new QLabel(widget);
    m_nestedEnabledLabel->setWordWrap(true);
    layout->addWidget(m_nestedEnabledLabel);

    m_nestedModeLabel = new QLabel(widget);
    m_nestedModeLabel->setWordWrap(true);
    layout->addWidget(m_nestedModeLabel);

    m_nestedInnerLabelLabel = new QLabel(widget);
    m_nestedInnerLabelLabel->setWordWrap(true);
    layout->addWidget(m_nestedInnerLabelLabel);

    m_nestedInnerChoiceLabel = new QLabel(widget);
    m_nestedInnerChoiceLabel->setWordWrap(true);
    layout->addWidget(m_nestedInnerChoiceLabel);

    m_pressedLabel = new QLabel("Key down: (none)", widget);
    m_releasedLabel = new QLabel("Key up: (none)", widget);
    m_triggeredLabel = new QLabel("Triggered: (none)", widget);

    layout->addWidget(m_pressedLabel);
    layout->addWidget(m_releasedLabel);
    layout->addWidget(m_triggeredLabel);

    refreshLabels();

    return widget;
}

void Example::initialize(const QString &pluginRootPath, const PluginConfig &pluginConfig, QuolServices *services) {
    m_pluginRootPath = pluginRootPath;
    m_cfg = pluginConfig;
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

    refreshLabels();
    applyHotkeyFromConfig();
}

void Example::onUpdateConfig(const PluginConfig &pluginConfig) {
    m_cfg = pluginConfig;
    refreshLabels();
    applyHotkeyFromConfig();
}

void Example::shutdown() {
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

void Example::applyHotkeyFromConfig() {
    if (!m_services || !m_services->inputManager())
        return;

    const QString combo = m_cfg.get("send_combo").toString().trimmed().toLower();

    if (!m_hotkeyId.isEmpty()) {
        m_services->inputManager()->removeHotkey(m_hotkeyId);
        m_hotkeyId.clear();
    }

    if (combo.isEmpty())
        return;

    m_hotkeyId = m_services->inputManager()->addHotkey(
        combo,
        [this, combo]() {
            if (m_triggeredLabel)
                m_triggeredLabel->setText(QStringLiteral("Triggered: ") + combo);
        },
        true
    );
}

void Example::refreshLabels() {
    if (m_titleLabel) {
        const QString title = m_cfg.get("sss").toString();
        m_titleLabel->setText(title);
    }

    if (m_valueLabel) {
        m_valueLabel->setText(examplelib::calculateFromConfig(m_cfg.root()));
    }

    if (m_nestedNoteLabel) {
        m_nestedNoteLabel->setText(examplelib::nestedNoteLine(m_cfg.root()));
    }

    if (m_nestedEnabledLabel) {
        m_nestedEnabledLabel->setText(examplelib::nestedEnabledLine(m_cfg.root()));
    }

    if (m_nestedModeLabel) {
        m_nestedModeLabel->setText(examplelib::nestedModeLine(m_cfg.root()));
    }

    if (m_nestedInnerLabelLabel) {
        m_nestedInnerLabelLabel->setText(examplelib::nestedInnerLabelLine(m_cfg.root()));
    }

    if (m_nestedInnerChoiceLabel) {
        m_nestedInnerChoiceLabel->setText(examplelib::nestedInnerChoiceLine(m_cfg.root()));
    }
}
