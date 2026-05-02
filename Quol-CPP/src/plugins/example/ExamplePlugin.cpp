#include "plugins/example/ExamplePlugin.hpp"

#include <QJsonObject>
#include <QLabel>
#include <QVBoxLayout>
#include <QWidget>

QString ExamplePlugin::pluginId() const
{
    return "example";
}

QString ExamplePlugin::displayName() const
{
    return "Example";
}

QWidget* ExamplePlugin::createWidget(QWidget* parent)
{
    const QString message = m_pluginConfig.value("message")
        .toString("Hello from the C++ example plugin");

    auto* widget = new QWidget(parent);
    auto* layout = new QVBoxLayout(widget);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setAlignment(Qt::AlignTop);

    auto* label = new QLabel(message, widget);
    label->setWordWrap(true);
    layout->addWidget(label);

    return widget;
}

QJsonObject ExamplePlugin::defaultConfig() const
{
    return {
        {"message", "Hello from the C++ example plugin"},
        {"accent", "#4FC3F7"}
    };
}

void ExamplePlugin::initialize(const QString& pluginRootPath,
                               const QJsonObject& appSettings,
                               const QJsonObject& pluginConfig)
{
    m_pluginRootPath = pluginRootPath;
    m_appSettings = appSettings;
    m_pluginConfig = pluginConfig;
}

void ExamplePlugin::shutdown()
{
}
