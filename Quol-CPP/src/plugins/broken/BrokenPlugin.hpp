#pragma once

#include "plugin_api/IQuolPlugin.hpp"

#include <QObject>

class BrokenPlugin final : public QObject, public IQuolPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID IQuolPlugin_iid)
    Q_INTERFACES(IQuolPlugin)

public:
    QWidget *createWidget(QWidget *parent = nullptr) override;
    void initialize(
        const QString &pluginRootPath, const QJsonObject &appSettings, const QJsonObject &pluginConfig
    ) override;
    void shutdown() override;
};
