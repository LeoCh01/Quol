#pragma once

#include <QJsonArray>
#include <QObject>
#include <QString>

#include <functional>

class QNetworkAccessManager;

class PluginStoreManager : public QObject {
    Q_OBJECT

public:
    explicit PluginStoreManager(QObject *parent = nullptr);

    void fetchStoreItems();
    // itemName is the zip base name without extension, e.g. "example--v2"
    void downloadPlugin(const QString &itemName, bool isUpdate, const QString &appVersion = QString());
    void installLocalPlugin(const QString &zipFilePath);

    static QString artifactPluginName(const QString &itemName);

    static int compareVersions(const QString &a, const QString &b);

signals:
    void storeItemsFetched(const QJsonArray &items);
    void storeItemsFetchFailed(const QString &error);
    void pluginDownloadFinished(const QString &pluginName, bool success);
    void localPluginInstallFinished(const QString &pluginName, bool success);

private:
    void extractZipAsync(const QString &zipPath, const QString &pluginDir, std::function<void(bool)> onDone);

    QNetworkAccessManager *m_network;
};