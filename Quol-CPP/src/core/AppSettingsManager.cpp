#include "core/AppSettingsManager.hpp"

#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QVariantList>
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

QJsonObject &AppSettingsManager::data() {
    return m_data;
}

QVariantList AppSettingsManager::windowGeometry(
    const QString &configKey, int defaultX, int defaultY, int defaultWidth, int defaultHeight
) {
    QJsonObject pluginConfig = ensurePluginConfig(configKey);
    QJsonObject meta = pluginConfig.value(QStringLiteral("_")).toObject();
    QJsonArray geometry = meta.value(QStringLiteral("geometry")).toArray();

    if (geometry.size() < 4) {
        geometry = QJsonArray{defaultX, defaultY, defaultWidth, defaultHeight};
        meta.insert(QStringLiteral("geometry"), geometry);
        pluginConfig.insert(QStringLiteral("_"), meta);
        setPluginConfig(configKey, pluginConfig);
        save();
    }

    return QVariantList{
        geometry.at(0).toInt(defaultX),
        geometry.at(1).toInt(defaultY),
        geometry.at(2).toInt(defaultWidth),
        geometry.at(3).toInt(defaultHeight)
    };
}

void AppSettingsManager::setWindowGeometry(const QString &configKey, int x, int y, int width, int height) {
    QJsonObject pluginConfig = ensurePluginConfig(configKey);
    QJsonObject meta = pluginConfig.value(QStringLiteral("_")).toObject();
    meta.insert(QStringLiteral("geometry"), QJsonArray{x, y, width, height});
    pluginConfig.insert(QStringLiteral("_"), meta);

    setPluginConfig(configKey, pluginConfig);
    save();
}

QString AppSettingsManager::settingString(const QString &key, const QString &defaultValue) const {
    const QString text = m_data.value(key).toString().trimmed();
    return text.isEmpty() ? defaultValue : text;
}

QJsonObject AppSettingsManager::ensurePluginConfig(const QString &configKey) {
    const QJsonObject configs = m_data.value(QStringLiteral("configs")).toObject();
    return configs.value(configKey).toObject();
}

void AppSettingsManager::setPluginConfig(const QString &configKey, const QJsonObject &pluginConfig) {
    QJsonObject configs = m_data.value(QStringLiteral("configs")).toObject();
    configs.insert(configKey, pluginConfig);
    m_data.insert(QStringLiteral("configs"), configs);
}
