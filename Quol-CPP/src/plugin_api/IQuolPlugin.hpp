#pragma once

#include <QJsonObject>
#include <QObject>

class QWidget;

class IQuolPlugin {
public:
    virtual ~IQuolPlugin() = default;

    virtual QWidget *createWidget(QWidget *parent = nullptr) = 0;

    virtual void initialize(
            const QString &pluginRootPath, const QJsonObject &appSettings, const QJsonObject &pluginConfig
    ) = 0;
    virtual void onUpdateConfig(const QJsonObject &pluginConfig) {
        Q_UNUSED(pluginConfig);
    }
    virtual void shutdown() = 0;
};

#define IQuolPlugin_iid "com.quol.IQuolPlugin/2.0"
Q_DECLARE_INTERFACE(IQuolPlugin, IQuolPlugin_iid)
