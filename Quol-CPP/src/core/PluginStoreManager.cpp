#include "core/PluginStoreManager.hpp"

#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QJsonDocument>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QProcess>
#include <QTemporaryFile>
#include <QUrl>

static const char *kStoreApiUrl = "https://api.github.com/repos/LeoCh01/Quol-Tools/contents/plugins?ref=cpp-migration";
static const char *kRawBaseUrl = "https://raw.githubusercontent.com/LeoCh01/Quol-Tools/cpp-migration/plugins/";

PluginStoreManager::PluginStoreManager(QObject *parent) : QObject(parent), m_network(new QNetworkAccessManager(this)) {
}

void PluginStoreManager::fetchStoreItems() {
    QNetworkRequest request;
    request.setUrl(QUrl(QString::fromLatin1(kStoreApiUrl)));
    request.setRawHeader("Accept", "application/vnd.github.v3+json");
    request.setRawHeader("User-Agent", "Quol-App");

    QNetworkReply *reply = m_network->get(request);
    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        reply->deleteLater();
        if (reply->error() != QNetworkReply::NoError) {
            emit storeItemsFetchFailed(reply->errorString());
            return;
        }
        const QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
        if (!doc.isArray()) {
            emit storeItemsFetchFailed(QStringLiteral("Unexpected response format from GitHub"));
            return;
        }
        emit storeItemsFetched(doc.array());
    });
}

void PluginStoreManager::downloadPlugin(const QString &itemName, bool isUpdate) {
    const QString url = QLatin1String(kRawBaseUrl) + itemName + QStringLiteral(".zip");
    QNetworkRequest request;
    request.setUrl(QUrl(url));
    request.setRawHeader("User-Agent", "Quol-App");

    QNetworkReply *reply = m_network->get(request);
    connect(reply, &QNetworkReply::finished, this, [this, reply, itemName, isUpdate]() {
        reply->deleteLater();

        // Derive folder name by stripping "--v<version>" suffix
        QString pluginName = itemName;
        const int sep = pluginName.lastIndexOf(QStringLiteral("--v"));
        if (sep != -1)
            pluginName = pluginName.left(sep);

        if (reply->error() != QNetworkReply::NoError) {
            emit pluginDownloadFinished(pluginName, false);
            return;
        }

        const QByteArray data = reply->readAll();
        const QString pluginsDir = QCoreApplication::applicationDirPath() + QStringLiteral("/plugins");
        const QString pluginDir = pluginsDir + QStringLiteral("/") + pluginName;
        const QString backupDir = pluginsDir + QStringLiteral("/") + pluginName + QStringLiteral("_backup");
        const QString configPath = pluginDir + QStringLiteral("/res/config.json");
        const QString dllPath = pluginDir + QStringLiteral("/") + pluginName + QStringLiteral(".dll");

        // Save downloaded zip to a temp file
        QTemporaryFile tempZip(QDir::tempPath() + QStringLiteral("/quol_plugin_XXXXXX.zip"));
        tempZip.setAutoRemove(false);
        if (!tempZip.open()) {
            emit pluginDownloadFinished(pluginName, false);
            return;
        }
        tempZip.write(data);
        tempZip.close();
        const QString zipPath = tempZip.fileName();

        // Backup the existing plugin directory before updating
        if (isUpdate && QDir(pluginDir).exists()) {
            if (QDir(backupDir).exists())
                QDir(backupDir).removeRecursively();
            QDir().rename(pluginDir, backupDir);
        }

        if (!QDir().mkpath(pluginDir)) {
            QFile::remove(zipPath);
            emit pluginDownloadFinished(pluginName, false);
            return;
        }

        // Use PowerShell Expand-Archive for zip extraction (async, non-blocking)
        const QString script = QStringLiteral("Expand-Archive -LiteralPath \"%1\" -DestinationPath \"%2\" -Force")
                                   .arg(QDir::toNativeSeparators(zipPath), QDir::toNativeSeparators(pluginDir));

        auto *proc = new QProcess(this);
        connect(
            proc,
            qOverload<int, QProcess::ExitStatus>(&QProcess::finished),
            this,
            [this, proc, pluginName, isUpdate, zipPath, pluginDir, backupDir](int exitCode, QProcess::ExitStatus) {
                proc->deleteLater();
                QFile::remove(zipPath);

                const QString configPath = pluginDir + QStringLiteral("/res/config.json");
                const QString dllPath = pluginDir + QStringLiteral("/") + pluginName + QStringLiteral(".dll");
                const bool ok = exitCode == 0 && QFile::exists(configPath) && QFile::exists(dllPath);

                if (!ok) {
                    // Restore backup on failure
                    if (isUpdate && QDir(backupDir).exists()) {
                        if (QDir(pluginDir).exists())
                            QDir(pluginDir).removeRecursively();
                        QDir().rename(backupDir, pluginDir);
                    }
                } else {
                    // Remove backup on success
                    if (isUpdate && QDir(backupDir).exists())
                        QDir(backupDir).removeRecursively();
                }

                emit pluginDownloadFinished(pluginName, ok);
            }
        );
        proc->start(
            QStringLiteral("powershell"),
            {QStringLiteral("-NoProfile"), QStringLiteral("-NonInteractive"), QStringLiteral("-Command"), script}
        );
    });
}
