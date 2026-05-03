#include "plugins/example/ExamplePlugin.hpp"
#include "plugins/example/lib/adder.hpp"

#include <QJsonObject>
#include <QLabel>
#include <QVBoxLayout>
#include <QWidget>

QWidget *ExamplePlugin::createWidget(QWidget *parent)
{
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

    refreshLabels();

    return widget;
}

void ExamplePlugin::initialize(const QString &pluginRootPath,
                               const QJsonObject &appSettings,
                               const QJsonObject &pluginConfig)
{
    m_pluginRootPath = pluginRootPath;
    m_appSettings = appSettings;
    m_pluginConfig = pluginConfig;
    refreshLabels();
}

void ExamplePlugin::onUpdateConfig(const QJsonObject &pluginConfig)
{
    m_pluginConfig = pluginConfig;
    refreshLabels();
}

void ExamplePlugin::shutdown()
{
}

void ExamplePlugin::refreshLabels()
{
    if (m_titleLabel)
    {
        const QString title = m_pluginConfig.value("title").toString("Example");
        m_titleLabel->setText(title);
    }

    if (m_valueLabel)
    {
        m_valueLabel->setText(examplelib::calculateFromConfig(m_pluginConfig));
    }

    if (m_nestedNoteLabel)
    {
        m_nestedNoteLabel->setText(examplelib::nestedNoteLine(m_pluginConfig));
    }

    if (m_nestedEnabledLabel)
    {
        m_nestedEnabledLabel->setText(examplelib::nestedEnabledLine(m_pluginConfig));
    }

    if (m_nestedModeLabel)
    {
        m_nestedModeLabel->setText(examplelib::nestedModeLine(m_pluginConfig));
    }

    if (m_nestedInnerLabelLabel)
    {
        m_nestedInnerLabelLabel->setText(examplelib::nestedInnerLabelLine(m_pluginConfig));
    }

    if (m_nestedInnerChoiceLabel)
    {
        m_nestedInnerChoiceLabel->setText(examplelib::nestedInnerChoiceLine(m_pluginConfig));
    }
}
