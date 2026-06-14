#pragma once

#include <QJsonArray>
#include <QObject>
#include <QString>

class QNetworkAccessManager;

class PluginStoreManager : public QObject {
    Q_OBJECT

public:
    explicit PluginStoreManager(QObject *parent = nullptr);

    void fetchStoreItems();
    // itemName is the zip base name without extension, e.g. "example--v2"
    void downloadPlugin(const QString &itemName, bool isUpdate);

signals:
    void storeItemsFetched(const QJsonArray &items);
    void storeItemsFetchFailed(const QString &error);
    void pluginDownloadFinished(const QString &pluginName, bool success);

private:
    QNetworkAccessManager *m_network;
};
