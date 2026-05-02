#pragma once

#include <QJsonObject>
#include <QObject>

class QWidget;

class IQuolPlugin
{
public:
    virtual ~IQuolPlugin() = default;

    virtual QString pluginId() const = 0;
    virtual QString displayName() const = 0;

    virtual QWidget* createWidget(QWidget* parent = nullptr) = 0;

    virtual QJsonObject defaultConfig() const = 0;
    virtual void initialize(const QString& pluginRootPath,
                            const QJsonObject& appSettings,
                            const QJsonObject& pluginConfig) = 0;
    virtual void shutdown() = 0;
};

#define IQuolPlugin_iid "com.quol.IQuolPlugin/2.0"
Q_DECLARE_INTERFACE(IQuolPlugin, IQuolPlugin_iid)
