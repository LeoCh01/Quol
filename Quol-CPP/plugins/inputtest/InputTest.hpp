#pragma once

#include "plugin_api/IQuolPlugin.hpp"

#include <QObject>

class QLabel;

class InputTest final : public QObject, public IQuolPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID IQuolPlugin_iid)
    Q_INTERFACES(IQuolPlugin)

public:
    QWidget *createWidget(QWidget *parent = nullptr) override;

    void initialize(const QString &pluginRootPath, const QJsonObject &pluginConfig, QuolServices *services) override;
    void onUpdateConfig(const QJsonObject &pluginConfig) override;
    void shutdown() override;

private:
    void applyHotkeyFromConfig();

    QString m_pluginRootPath;
    QJsonObject m_pluginConfig;
    QuolServices *m_services = nullptr;

    QString m_hotkeyId;     // handle returned by InputManager::addHotkey
    QString m_keyListenId;  // handle returned by InputManager::addKeyListener

    QLabel *m_pressedLabel = nullptr;
    QLabel *m_releasedLabel = nullptr;
    QLabel *m_triggeredLabel = nullptr;
};
