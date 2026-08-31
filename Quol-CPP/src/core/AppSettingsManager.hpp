#pragma once

#include <QJsonObject>
#include <QObject>
#include <QString>

class AppSettingsManager : public QObject {
    Q_OBJECT

public:
    explicit AppSettingsManager(QString settingsPath, QObject *parent = nullptr);

    bool load();
    bool save() const;

    const QJsonObject &data() const;

    void setValue(const QString &key, const QJsonValue &value);

    QString settingString(const QString &key, const QString &defaultValue = QString()) const;

private:
    QString m_settingsPath;
    QJsonObject m_data;
};
