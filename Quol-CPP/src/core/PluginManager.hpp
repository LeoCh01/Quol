#pragma once

#include <QList>
#include <QObject>

class AppSettingsManager;
class QuolWindow;
class TransitionManager;

class PluginManager : public QObject {
    Q_OBJECT

public:
    explicit PluginManager(QObject *parent = nullptr);
    ~PluginManager() override;

    void loadPlugins(AppSettingsManager *settings, TransitionManager *transitions);
    QList<QuolWindow *> windows() const;

private:
    QList<QuolWindow *> m_windows;
};
