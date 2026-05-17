#pragma once

#include <QList>
#include <QObject>

class AppSettingsManager;
class IQuolPlugin;
class QPluginLoader;
class QuolServices;
class QuolWindow;
class TransitionManager;

class PluginManager : public QObject {
    Q_OBJECT

public:
    explicit PluginManager(QObject *parent = nullptr);
    ~PluginManager() override;

    void loadPlugins(AppSettingsManager *settings, TransitionManager *transitions, QuolServices *services);
    QList<QuolWindow *> windows() const;

private:
    struct LoadedPlugin {
        QPluginLoader *loader = nullptr;
        IQuolPlugin *plugin = nullptr;
    };

    QList<QuolWindow *> m_windows;
    QList<LoadedPlugin> m_plugins;
};
