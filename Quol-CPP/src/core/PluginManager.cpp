#include "core/PluginManager.hpp"
#include "core/AppSettingsManager.hpp"
#include "plugin_api/IQuolPlugin.hpp"
#include "ui/QuolWindow.hpp"
#include "ui/TransitionManager.hpp"

#include <QCoreApplication>
#include <QFile>
#include <QFileInfo>
#include <QJsonArray>
#include <QJsonDocument>
#include <QLabel>
#include <QMessageBox>
#include <QPluginLoader>

#include <exception>

namespace {
QJsonObject readPluginConfig(const QString &configPath) {
    QFile file(configPath);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        throw std::runtime_error(QString("Failed to open config: %1").arg(configPath).toStdString());
    }

    const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    file.close();
    if (!doc.isObject()) {
        throw std::runtime_error(QString("Invalid JSON object in config: %1").arg(configPath).toStdString());
    }

    const QJsonObject config = doc.object();
    const QJsonArray geometry = config.value("_").toObject().value("default_geometry").toArray();
    if (geometry.size() < 4) {
        throw std::runtime_error(QString("Missing _.default_geometry in config: %1").arg(configPath).toStdString());
    }

    return config;
}
}  // namespace

PluginManager::PluginManager(QObject *parent) : QObject(parent) {
}

PluginManager::~PluginManager() {
    qDeleteAll(m_windows);
    m_windows.clear();
}

void PluginManager::loadPlugins(AppSettingsManager *settings, TransitionManager *transitions) {
    if (!settings)
        return;

    const QString appDir = QCoreApplication::applicationDirPath();
    const QString pluginsDir = appDir + "/plugins";
    const QJsonArray pluginIds = settings->data().value("plugins").toArray();

    for (const auto &val : pluginIds) {
        const QString id = val.toString().trimmed();
        if (id.isEmpty())
            continue;

        QuolWindow *win = nullptr;
        try {
            const QString configPath = pluginsDir + "/" + id + "/res/config.json";
            const QJsonObject pluginConfig = readPluginConfig(configPath);
            const QJsonArray defaultGeometry = pluginConfig.value("_").toObject().value("default_geometry").toArray();
            const QString displayTitle = pluginConfig.value("title").toString();

            const QString libPath = pluginsDir + "/" + id + "/" + id;
            auto *loader = new QPluginLoader(libPath, this);
            auto *plugin = qobject_cast<IQuolPlugin *>(loader->instance());
            if (!plugin) {
                throw std::runtime_error(QString("Failed to load plugin library: %1").arg(libPath).toStdString());
            }

            win = new QuolWindow(
                displayTitle,
                settings,
                defaultGeometry.at(0).toInt(),
                defaultGeometry.at(1).toInt(),
                defaultGeometry.at(2).toInt(),
                defaultGeometry.at(3).toInt()
            );

            win->attachConfigWindow(configPath, displayTitle + " Config");

            plugin->initialize(pluginsDir + "/" + id, settings->data(), pluginConfig);
            win->setConfigSavedCallback([plugin](const QJsonObject &updatedConfig) {
                plugin->onUpdateConfig(updatedConfig);
            });
            win->addContent(plugin->createWidget());

            if (transitions)
                transitions->addWindow(win);

            m_windows.append(win);
            win = nullptr;
        } catch (const std::exception &e) {
            if (win) {
                delete win;
            }

            QMessageBox::critical(
                nullptr,
                "Plugin Load Error",
                QString("Failed to load plugin '%1':\n%2").arg(id).arg(QString::fromStdString(e.what()))
            );
        } catch (...) {
            if (win) {
                delete win;
            }

            QMessageBox::critical(
                nullptr, "Plugin Load Error", QString("Failed to load plugin '%1' with an unknown error.").arg(id)
            );
        }
    }
}

QList<QuolWindow *> PluginManager::windows() const {
    return m_windows;
}
