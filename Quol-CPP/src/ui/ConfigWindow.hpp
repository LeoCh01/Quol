#pragma once

#include "ui/QuolWindow.hpp"

#include <QJsonObject>

class QGroupBox;
class QLayout;
class QVBoxLayout;

class ConfigWindow : public QuolWindow {
    Q_OBJECT

public:
    explicit ConfigWindow(
            const QString &pluginId,
            const QString &title,
            AppSettingsManager *settings,
            const QString &configPath,
            QWidget *parent = nullptr
    );

    void reloadFromDisk();

signals:
    void configSaved(const QJsonObject &config);

private slots:
    void saveConfig();

private:
    void buildUi();
    void clearDynamicUi();
    void generateSettings();

    static void addItemToLayout(QLayout *layout, QLayout *itemLayout);
    static void addItemToLayout(QLayout *layout, QWidget *widget);

    QLayout *createItem(const QString &key, const QJsonValue &value);
    QJsonObject extractFromLayout(QLayout *layout) const;

    static QJsonValue parseLineEditValue(const QString &text);

    QString m_configPath;
    QJsonObject m_config;

    QVBoxLayout *m_configLayout = nullptr;
    QVBoxLayout *m_rootContentLayout = nullptr;
};
