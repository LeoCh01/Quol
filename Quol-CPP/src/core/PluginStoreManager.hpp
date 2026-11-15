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

    // Applies staged plugin updates (<name>_updated dirs) by swapping them in. Must run
    // before plugins load: loaded DLLs cannot be renamed mid-process.
    static void applyPendingUpdates();

    static QString artifactPluginName(const QString &itemName);

    static int compareVersions(const QString &a, const QString &b);

signals:
    void storeItemsFetched(const QJsonArray &items);
    void storeItemsFetchFailed(const QString &error);
    // restartRequired: the update was staged and applies after an app restart
    void pluginDownloadFinished(
        const QString &pluginName, bool success, const QString &errorMessage, bool restartRequired
    );
    void localPluginInstallFinished(const QString &pluginName, bool success);

private:
    void extractZipAsync(
        const QString &zipPath, const QString &pluginDir, const QString &pluginName, std::function<void(bool)> onDone
    );

    bool createTempPluginZip(const QByteArray &data, QString &zipPath) const;

    // sets errorMessage and returns false when the plugin needs a newer app version
    bool checkPluginDependency(const QString &pluginDir, const QString &appVersion, QString &errorMessage) const;

    QNetworkAccessManager *m_network;
};