#pragma once

#include "plugin_api/IQuolPlugin.hpp"

#include <QObject>

class QGridLayout;
class QIcon;
class QLabel;
class QPushButton;
class QTimer;

class ColorPicker final : public QObject, public IQuolPlugin {
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
    void togglePicking();
    void stopPicking();
    void updateColor();
    void drawFrame(QPixmap &pixmap);

    QString m_pluginRootPath;
    QJsonObject m_pluginConfig;

    qreal m_sf = 1.0;

    QGridLayout *m_gridLayout = nullptr;
    QLabel *m_previewLabel = nullptr;
    QLabel *m_hexLabel = nullptr;
    QLabel *m_rgbLabel = nullptr;
    QPushButton *m_pickButton = nullptr;
    QTimer *m_timer = nullptr;
};
