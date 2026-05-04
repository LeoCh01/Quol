#include "plugins/broken/BrokenPlugin.hpp"

#include <QLabel>
#include <QWidget>

QWidget *BrokenPlugin::createWidget(QWidget *parent) {
    auto *widget = new QWidget(parent);
    auto *label = new QLabel("This should never display", widget);
    return widget;
}

void BrokenPlugin::initialize(
        const QString &pluginRootPath, const QJsonObject &appSettings, const QJsonObject &pluginConfig
) {
    // Intentionally fail
    throw std::runtime_error("Broken plugin intentionally failed during initialize");
}

void BrokenPlugin::shutdown() {
}
