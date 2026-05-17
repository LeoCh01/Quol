#pragma once

#include "plugin_api/QuolServices.hpp"

#include <QJsonObject>
#include <QObject>

class QWidget;

class IQuolPlugin {
public:
    virtual ~IQuolPlugin() = default;

    // Called first; build and return the plugin's root widget.
    virtual QWidget *createWidget(QWidget *parent = nullptr) = 0;

    // Called immediately after createWidget. pluginRootPath is the absolute
    // path to the plugin's output folder (e.g. build/plugins/myPlugin/).
    // services provides access to the shared InputManager and any future
    // application-level services. The global appSettings JSON is intentionally
    // not forwarded here — plugins should only need their own pluginConfig.
    virtual void initialize(const QString &pluginRootPath, const QJsonObject &pluginConfig, QuolServices *services) = 0;

    virtual void onUpdateConfig(const QJsonObject &pluginConfig) {
        Q_UNUSED(pluginConfig);
    }
    virtual void shutdown() = 0;
};

#define IQuolPlugin_iid "com.quol.IQuolPlugin/3.0"
Q_DECLARE_INTERFACE(IQuolPlugin, IQuolPlugin_iid)
