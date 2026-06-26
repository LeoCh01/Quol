#include "core/PluginManager.hpp"
#include "core/AppSettingsManager.hpp"
#include "plugin_api/IQuolPlugin.hpp"
#include "plugin_api/PluginConfig.hpp"
#include "plugin_api/QuolServices.hpp"
#include "ui/QuolWindow.hpp"
#include "ui/TransitionManager.hpp"

#include <QCoreApplication>
#include <QDebug>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QJsonArray>
#include <QJsonDocument>
#include <QMessageBox>
#include <QPluginLoader>

#include <exception>

namespace {
QJsonObject readPluginConfig(const QString &configPath) {
    QFile file(configPath);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        throw std::runtime_error(QString("Cannot open plugin config: %1").arg(configPath).toStdString());
    }
    const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    file.close();
    return doc.object();
}
}  // namespace

PluginManager::PluginManager(QObject *parent) : QObject(parent) {
}

PluginManager::~PluginManager() {
    shutdownPlugins();
}

void PluginManager::shutdownPlugins() {
    if (m_plugins.isEmpty() && m_windows.isEmpty())
        return;

    // 1) Let plugins detach hotkeys/listeners while InputManager is still alive.
    for (const auto &lp : std::as_const(m_plugins)) {
        if (lp.plugin) {
            lp.plugin->shutdown();
        }
    }

    // 2) Destroy plugin-created widgets before unloading plugin DLLs.
    qDeleteAll(m_windows);
    m_windows.clear();

    // 3) Unload plugin DLLs last.
    for (const auto &lp : std::as_const(m_plugins)) {
        if (lp.loader) {
            lp.loader->unload();
            delete lp.loader;
        }
    }
    m_plugins.clear();
}

void PluginManager::loadPlugins(AppSettingsManager *settings, TransitionManager *transitions, QuolServices *services) {
    if (!settings)
        return;

    auto removePluginFromSettings = [settings](const QString &pluginId) {
        QJsonArray plugins = settings->data().value(QStringLiteral("plugins")).toArray();
        QJsonArray filtered;

        for (const QJsonValue &value : plugins) {
            const QString currentId = value.toString().trimmed();
            if (!currentId.isEmpty() && currentId != pluginId) {
                filtered.append(currentId);
            }
        }

        settings->setValue(QStringLiteral("plugins"), filtered);
        settings->save();
    };

    const QString appDir = QCoreApplication::applicationDirPath();
    QString pluginsDirSetting =
        settings->settingString(QStringLiteral("plugins_dir"), QStringLiteral("plugins")).trimmed();
    if (pluginsDirSetting.isEmpty()) {
        pluginsDirSetting = QStringLiteral("plugins");
    }

    const QString pluginsDirPath =
        QDir::isRelativePath(pluginsDirSetting) ? QDir(appDir).filePath(pluginsDirSetting) : pluginsDirSetting;
    const QDir pluginsDir(pluginsDirPath);
    const QJsonArray pluginIds = settings->data().value(QStringLiteral("plugins")).toArray();

    for (const auto &val : pluginIds) {
        qInfo() << "Loading plugin:" << val.toString();
        const QString id = val.toString().trimmed();

        QuolWindow *win = nullptr;
        QPluginLoader *loader = nullptr;
        try {
            const QString configPath = pluginsDir.filePath(id + QStringLiteral("/res/config.json"));
            const PluginConfig pluginConfig(readPluginConfig(configPath), configPath);
            const QJsonArray defaultGeometry = pluginConfig.root()
                                                   .value(QStringLiteral("_"))
                                                   .toObject()
                                                   .value(QStringLiteral("default_geometry"))
                                                   .toArray();
            const QString displayTitle = pluginConfig.root()
                                             .value(QStringLiteral("_"))
                                             .toObject()
                                             .value(QStringLiteral("name"))
                                             .toString()
                                             .trimmed();

            const QString libPath = pluginsDir.filePath(id + QStringLiteral("/") + id);
            loader = new QPluginLoader(libPath);
            auto *plugin = qobject_cast<IQuolPlugin *>(loader->instance());
            if (!plugin) {
                qWarning() << "Failed to load plugin library:" << libPath << loader->errorString();
                throw std::runtime_error(
                    QString("Failed to load plugin library: %1 — %2").arg(libPath, loader->errorString()).toStdString()
                );
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

            // initialize() before createWidget() so plugins have config + services available.
            plugin->initialize(pluginsDir.filePath(id), pluginConfig, services);
            win->setConfigSavedCallback([plugin, configPath](const QJsonObject &updatedConfig) {
                plugin->onUpdateConfig(PluginConfig(updatedConfig, configPath));
            });
            win->addContent(plugin->createWidget());

            transitions->addWindow(win);

            qInfo() << "Plugin loaded:" << id;
            m_windows.append(win);
            m_plugins.append(LoadedPlugin{loader, plugin});
            win = nullptr;
            loader = nullptr;
        } catch (...) {
            qWarning() << "Plugin failed to load:" << id;
            delete win;
            if (loader) {
                loader->unload();
                delete loader;
            }

            removePluginFromSettings(id);

            QString msg = QStringLiteral("Failed to load plugin '%1' with an unknown error.").arg(id);
            try {
                std::rethrow_exception(std::current_exception());
            } catch (const std::exception &e) {
                msg = QString(QStringLiteral("Failed to load plugin '%1':\n%2"))
                          .arg(id)
                          .arg(QString::fromStdString(e.what()));
            } catch (...) {
            }

            QMessageBox::critical(nullptr, QStringLiteral("Plugin Load Error"), msg);
        }
    }
}

QList<QuolWindow *> PluginManager::windows() const {
    return m_windows;
}
