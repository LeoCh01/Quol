#include "core/PluginStoreManager.hpp"
#include "core/JsonFile.hpp"

#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QJsonDocument>
#include <QJsonObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QProcess>
#include <QTemporaryFile>
#include <QUrl>

#include <functional>

static const char *kStoreApiUrl = "https://api.github.com/repos/LeoCh01/Quol-Tools/contents/plugins?ref=main";
static const char *kRawBaseUrl = "https://raw.githubusercontent.com/LeoCh01/Quol-Tools/main/plugins/";

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

QString PluginStoreManager::artifactPluginName(const QString &itemName) {
    QString base = itemName;
    if (base.endsWith(QStringLiteral(".zip"))) {
        base.chop(4);
    }
    const int sep = base.lastIndexOf(QStringLiteral("--v"));
    return (sep != -1) ? base.left(sep) : base;
}

int PluginStoreManager::compareVersions(const QString &a, const QString &b) {
    const QStringList aParts = a.split('.');
    const QStringList bParts = b.split('.');
    const int maxLen = qMax(aParts.size(), bParts.size());
    for (int i = 0; i < maxLen; ++i) {
        const int aNum = i < aParts.size() ? aParts[i].toInt() : 0;
        const int bNum = i < bParts.size() ? bParts[i].toInt() : 0;
        if (aNum < bNum)
            return -1;
        if (aNum > bNum)
            return 1;
    }
    return 0;
}

void PluginStoreManager::extractZipAsync(
    const QString &zipPath, const QString &pluginDir, std::function<void(bool)> onDone
) {
    const QString script = QStringLiteral("Expand-Archive -LiteralPath \"%1\" -DestinationPath \"%2\" -Force")
                               .arg(QDir::toNativeSeparators(zipPath), QDir::toNativeSeparators(pluginDir));

    auto *proc = new QProcess(this);
    connect(
        proc,
        qOverload<int, QProcess::ExitStatus>(&QProcess::finished),
        this,
        [this, proc, zipPath, pluginDir, onDone](int exitCode, QProcess::ExitStatus) {
            proc->deleteLater();
            QFile::remove(zipPath);

            const QString pluginName = QFileInfo(pluginDir).fileName();
            const QString configPath = pluginDir + QStringLiteral("/res/config.json");
            const QString dllPath = pluginDir + QStringLiteral("/") + pluginName + QStringLiteral(".dll");

            onDone(exitCode == 0 && QFile::exists(configPath) && QFile::exists(dllPath));
        }
    );
    proc->start(
        QStringLiteral("powershell"),
        {QStringLiteral("-NoProfile"), QStringLiteral("-NonInteractive"), QStringLiteral("-Command"), script}
    );
}

void PluginStoreManager::downloadPlugin(const QString &itemName, bool isUpdate, const QString &appVersion) {
    const QString url = QLatin1String(kRawBaseUrl) + itemName + QStringLiteral(".zip");
    QNetworkRequest request;
    request.setUrl(QUrl(url));
    request.setRawHeader("User-Agent", "Quol-App");

    QNetworkReply *reply = m_network->get(request);
    connect(reply, &QNetworkReply::finished, this, [this, reply, itemName, isUpdate, appVersion]() {
        reply->deleteLater();

        const QString pluginName = artifactPluginName(itemName);

        if (reply->error() != QNetworkReply::NoError) {
            emit pluginDownloadFinished(pluginName, false);
            return;
        }

        const QByteArray data = reply->readAll();
        const QString pluginsDir = QCoreApplication::applicationDirPath() + QStringLiteral("/plugins");
        const QString pluginDir = pluginsDir + QStringLiteral("/") + pluginName;
        const QString backupDir = pluginsDir + QStringLiteral("/") + pluginName + QStringLiteral("_backup");

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

        extractZipAsync(
            zipPath, pluginDir, [this, pluginName, isUpdate, pluginDir, backupDir, appVersion](bool extracted) {
                bool ok = extracted;

                if (ok && !appVersion.isEmpty()) {
                    const QString configPath = pluginDir + QStringLiteral("/res/config.json");
                    const QString dependency = readJsonObjectFile(configPath)
                                                   .value(QStringLiteral("_"))
                                                   .toObject()
                                                   .value(QStringLiteral("dependency"))
                                                   .toString();
                    if (!dependency.isEmpty() && compareVersions(appVersion, dependency) < 0) {
                        ok = false;
                    }
                }

                if (!ok) {
                    if (isUpdate && QDir(backupDir).exists()) {
                        if (QDir(pluginDir).exists())
                            QDir(pluginDir).removeRecursively();
                        QDir().rename(backupDir, pluginDir);
                    } else if (QDir(pluginDir).exists()) {
                        QDir(pluginDir).removeRecursively();
                    }
                } else if (isUpdate && QDir(backupDir).exists()) {
                    QDir(backupDir).removeRecursively();
                }

                emit pluginDownloadFinished(pluginName, ok);
            }
        );
    });
}

void PluginStoreManager::installLocalPlugin(const QString &zipFilePath) {
    const QString pluginName = artifactPluginName(QFileInfo(zipFilePath).completeBaseName());

    const QString pluginsDir = QCoreApplication::applicationDirPath() + QStringLiteral("/plugins");
    const QString pluginDir = pluginsDir + QStringLiteral("/") + pluginName;

    if (QDir(pluginDir).exists()) {
        emit localPluginInstallFinished(pluginName, false);
        return;
    }

    if (!QDir().mkpath(pluginDir)) {
        emit localPluginInstallFinished(pluginName, false);
        return;
    }

    QTemporaryFile tempZip(QDir::tempPath() + QStringLiteral("/quol_plugin_XXXXXX.zip"));
    tempZip.setAutoRemove(false);
    if (!tempZip.open()) {
        QDir(pluginDir).removeRecursively();
        emit localPluginInstallFinished(pluginName, false);
        return;
    }
    QFile srcFile(zipFilePath);
    if (!srcFile.open(QIODevice::ReadOnly)) {
        tempZip.remove();
        QDir(pluginDir).removeRecursively();
        emit localPluginInstallFinished(pluginName, false);
        return;
    }
    tempZip.write(srcFile.readAll());
    tempZip.close();
    srcFile.close();
    const QString zipPath = tempZip.fileName();

    extractZipAsync(zipPath, pluginDir, [this, pluginName, pluginDir](bool ok) {
        if (!ok && QDir(pluginDir).exists()) {
            QDir(pluginDir).removeRecursively();
        }
        emit localPluginInstallFinished(pluginName, ok);
    });
}