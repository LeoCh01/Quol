#pragma once

#include "plugin_api/IQuolPlugin.hpp"

#include <QObject>

class InputManager;
class QLabel;
class QLineEdit;

class InputTestPlugin final : public QObject, public IQuolPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID IQuolPlugin_iid)
    Q_INTERFACES(IQuolPlugin)

public:
    QWidget *createWidget(QWidget *parent = nullptr) override;

    void initialize(
        const QString &pluginRootPath, const QJsonObject &appSettings, const QJsonObject &pluginConfig
    ) override;
    void onUpdateConfig(const QJsonObject &pluginConfig) override;
    void shutdown() override;

private:
    void applyHotkeyFromConfig();

    QString m_pluginRootPath;
    QJsonObject m_appSettings;
    QJsonObject m_pluginConfig;

    InputManager *m_inputManager = nullptr;
    int m_hotkeyId = -1;

    QLabel *m_hotkeyLabel = nullptr;
    QLabel *m_pressedLabel = nullptr;
    QLabel *m_releasedLabel = nullptr;
    QLabel *m_triggeredLabel = nullptr;
    QLineEdit *m_sendComboEdit = nullptr;
};
