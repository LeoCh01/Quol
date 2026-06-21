#pragma once

#include "ui/QuolWindow.hpp"

#include <QList>
#include <QMap>
#include <QStringList>

class AppSettingsManager;
class TransitionManager;
class QCheckBox;
class QLabel;
class QListWidget;
class QPushButton;
class QuolPopupWindow;
class PluginStoreManager;

class QuolMainWindow : public QuolWindow {
    Q_OBJECT

public:
    explicit QuolMainWindow(AppSettingsManager *settings, TransitionManager *transitions, QWidget *parent = nullptr);

    void updateToggleButton();

signals:
    void mainConfigApplied(const QString &toggleKey, bool resetPos, const QString &transitionType);

private:
    void openManagePluginsDialog();
    QWidget *buildInstalledTab(QWidget *popup, QList<QCheckBox *> &pluginChecks);
    QWidget *buildStoreTab(QWidget *popup, QListWidget *&storeListOut, QLabel *&storeStatusOut);
    QStringList discoverInstalledPluginIds() const;
    QMap<QString, int> getInstalledPluginVersions() const;
    void reloadApplication() const;

    void copySettingsToMainConfig();
    void applyMainConfigToSettings(const QJsonObject &config);

    AppSettingsManager *m_settings;
    TransitionManager *m_transitions;
    QPushButton *m_toggleBtn = nullptr;
    QuolPopupWindow *m_pluginManagerWindow = nullptr;
    PluginStoreManager *m_pluginStore = nullptr;
};
