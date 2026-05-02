#include "core/AppSettingsManager.hpp"

#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QVariantList>
#include <utility>

AppSettingsManager::AppSettingsManager(QString settingsPath, QObject *parent)
    : QObject(parent),
      m_settingsPath(std::move(settingsPath))
{
}

bool AppSettingsManager::load()
{
    QFile file(m_settingsPath);
    if (!file.exists())
    {
        m_data = defaultSettings();
        return save();
    }

    if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
    {
        m_data = defaultSettings();
        return false;
    }

    const auto doc = QJsonDocument::fromJson(file.readAll());
    file.close();

    if (!doc.isObject())
    {
        m_data = defaultSettings();
        save();
        return false;
    }

    m_data = defaultSettings();
    const auto loaded = doc.object();

    for (auto it = loaded.begin(); it != loaded.end(); ++it)
    {
        m_data.insert(it.key(), it.value());
    }

    // C++ migration keeps a single supported theme for now.
    m_data.insert("style", "dark");

    return true;
}

bool AppSettingsManager::save() const
{
    QFile file(m_settingsPath);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate))
    {
        return false;
    }

    const QJsonDocument doc(m_data);
    file.write(doc.toJson(QJsonDocument::Indented));
    file.close();
    return true;
}

const QJsonObject &AppSettingsManager::data() const
{
    return m_data;
}

QJsonObject &AppSettingsManager::data()
{
    return m_data;
}

QVariantList AppSettingsManager::windowGeometry(const QString &pluginId,
                                                int defaultX,
                                                int defaultY,
                                                int defaultWidth,
                                                int defaultHeight)
{
    QJsonObject pluginConfig = ensurePluginConfig(pluginId);
    QJsonObject meta = pluginConfig.value("_").toObject();
    QJsonArray geometry = meta.value("geometry").toArray();

    if (geometry.size() < 4)
    {
        geometry = QJsonArray{defaultX, defaultY, defaultWidth, defaultHeight};
        meta.insert("geometry", geometry);
        pluginConfig.insert("_", meta);
        setPluginConfig(pluginId, pluginConfig);
        save();
    }

    return QVariantList{
        geometry.at(0).toInt(defaultX),
        geometry.at(1).toInt(defaultY),
        geometry.at(2).toInt(defaultWidth),
        geometry.at(3).toInt(defaultHeight)};
}

void AppSettingsManager::setWindowGeometry(
    const QString &pluginId,
    int x,
    int y,
    int width,
    int height)
{
    QJsonObject pluginConfig = ensurePluginConfig(pluginId);
    QJsonObject meta = pluginConfig.value("_").toObject();
    meta.insert("geometry", QJsonArray{x, y, width, height});
    pluginConfig.insert("_", meta);

    setPluginConfig(pluginId, pluginConfig);
    save();
}

QString AppSettingsManager::settingString(const QString &key, const QString &defaultValue) const
{
    const QJsonValue value = m_data.value(key);
    if (!value.isString())
    {
        return defaultValue;
    }
    return value.toString(defaultValue);
}

QJsonObject AppSettingsManager::defaultSettings() const
{
    return {
        {"name", "Quol"},
        {"version", "4.2.0-cpp-mvp"},
        {"description", "Versatile toolbox for windows."},
        {"startup", false},
        {"toggle_key", "`"},
        {"style", "dark"},
        {"transition", "none"},
        {"is_default_pos", false},
        {"plugins_dir", "plugins"},
        {"plugins", QJsonArray{"example"}},
        {"show_updates", true},
        {"configs", QJsonObject()}};
}

QJsonObject AppSettingsManager::ensurePluginConfig(const QString &pluginId)
{
    const QJsonObject configs = m_data.value("configs").toObject();
    return configs.value(pluginId).toObject();
}

void AppSettingsManager::setPluginConfig(const QString &pluginId, const QJsonObject &pluginConfig)
{
    QJsonObject configs = m_data.value("configs").toObject();
    configs.insert(pluginId, pluginConfig);
    m_data.insert("configs", configs);
}
