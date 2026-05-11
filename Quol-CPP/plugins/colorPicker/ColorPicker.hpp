#pragma once

#include "plugin_api/IQuolPlugin.hpp"

#include <QObject>

class QGridLayout;
class QIcon;
class QLabel;
class QPushButton;
class QTimer;

class InputManager;

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
    static constexpr int kPreviewSize = 60;
    static constexpr int kDefaultSampleSize = 7;

    void togglePicking();
    void stopPicking();
    void updateColor();
    void drawFrame(QPixmap &pixmap);
    void applyVisualConfig();

    QString m_pluginRootPath;
    QJsonObject m_pluginConfig;
    QString m_escapeHotkeyId = "plugin.colorPicker.escape";
    int m_sampleSize = kDefaultSampleSize;

    QWidget *m_widget = nullptr;
    qreal m_sf = 1.0;
    bool m_picking = false;

    InputManager *m_inputManager = nullptr;

    QGridLayout *m_gridLayout = nullptr;
    QLabel *m_previewLabel = nullptr;
    QLabel *m_hexLabel = nullptr;
    QLabel *m_rgbLabel = nullptr;
    QPushButton *m_pickButton = nullptr;
    QTimer *m_timer = nullptr;
};
