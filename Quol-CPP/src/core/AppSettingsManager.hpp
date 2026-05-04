#pragma once

#include <QJsonObject>
#include <QObject>
#include <QString>
#include <QVariantList>

class AppSettingsManager : public QObject {
    Q_OBJECT

public:
    explicit AppSettingsManager(QString settingsPath, QObject *parent = nullptr);

    bool load();
    bool save() const;

    const QJsonObject &data() const;
    QJsonObject &data();

    QVariantList windowGeometry(
        const QString &configKey, int defaultX, int defaultY, int defaultWidth, int defaultHeight
    );
    void setWindowGeometry(const QString &configKey, int x, int y, int width, int height);
    QString settingString(const QString &key, const QString &defaultValue = QString()) const;

private:
    QJsonObject ensurePluginConfig(const QString &configKey);
    void setPluginConfig(const QString &configKey, const QJsonObject &pluginConfig);

    QString m_settingsPath;
    QJsonObject m_data;
};
