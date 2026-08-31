#pragma once

#include "ui/QuolWindow.hpp"

#include <QList>
#include <QMap>
#include <QStringList>

class AppSettingsManager;
class QCheckBox;
class QLabel;
class QListWidget;
class QTabWidget;
class MessageBoard;
class QuolPopupWindow;
class PluginStoreManager;

class QuolMainWindow : public QuolWindow {
    Q_OBJECT

public:
    explicit QuolMainWindow(AppSettingsManager *settings, QWidget *parent = nullptr);

    static void reloadApplication();

signals:
    void mainConfigApplied(const QString &toggleKey, bool resetPos, const QString &transitionType);

private:
    struct InstalledPluginMeta {
        QString id;
        QString title;
        int version;
    };

    void openManagePluginsDialog();
    void openMessageBoard();
    QWidget *buildInstalledTab(QWidget *popup, QList<QCheckBox *> &pluginChecks);
    QWidget *buildStoreTab(QWidget *popup, QListWidget *&storeListOut, QLabel *&storeStatusOut);
    QWidget *buildCustomTab(QWidget *popup, QLabel *&statusOut);
    QMap<QString, InstalledPluginMeta> discoverInstalledPlugins() const;
    void rebuildInstalledTab(QTabWidget *tabs, QWidget *popup);
    void addListRow(QListWidget *list, QWidget *rowWidget);

    void copySettingsToMainConfig();
    void applyMainConfigToSettings(const QJsonObject &config);

    AppSettingsManager *m_settings;
    QuolPopupWindow *m_pluginManagerWindow = nullptr;
    MessageBoard *m_messageBoard = nullptr;
    PluginStoreManager *m_pluginStore = nullptr;
};
