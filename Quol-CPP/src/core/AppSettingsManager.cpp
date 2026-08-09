#include "core/AppSettingsManager.hpp"

#include <QFile>
#include <QJsonDocument>
#include <utility>

AppSettingsManager::AppSettingsManager(QString settingsPath, QObject *parent)
    : QObject(parent), m_settingsPath(std::move(settingsPath)) {
}

bool AppSettingsManager::load() {
    QFile file(m_settingsPath);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        return false;
    }
    const auto doc = QJsonDocument::fromJson(file.readAll());
    file.close();
    m_data = doc.object();
    return true;
}

bool AppSettingsManager::save() const {
    QFile file(m_settingsPath);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate)) {
        return false;
    }
    const QJsonDocument doc(m_data);
    file.write(doc.toJson(QJsonDocument::Indented));
    file.close();
    return true;
}

const QJsonObject &AppSettingsManager::data() const {
    return m_data;
}

void AppSettingsManager::setValue(const QString &key, const QJsonValue &value) {
    m_data.insert(key, value);
}

QString AppSettingsManager::settingString(const QString &key, const QString &defaultValue) const {
    const QString text = m_data.value(key).toString().trimmed();
    return text.isEmpty() ? defaultValue : text;
}
