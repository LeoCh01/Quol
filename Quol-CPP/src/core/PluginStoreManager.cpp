#include "core/PluginStoreManager.hpp"
#include "core/JsonFile.hpp"

#include <QCoreApplication>
#include <QDebug>
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
#include <QThread>
#include <QUrl>

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
    const QString &zipPath, const QString &pluginDir, const QString &pluginName, std::function<void(bool)> onDone
) {
    const QString script = QStringLiteral("Expand-Archive -LiteralPath \"%1\" -DestinationPath \"%2\" -Force")
                               .arg(QDir::toNativeSeparators(zipPath), QDir::toNativeSeparators(pluginDir));

    auto *proc = new QProcess(this);
    connect(
        proc,
        qOverload<int, QProcess::ExitStatus>(&QProcess::finished),
        this,
        [proc, zipPath, pluginDir, pluginName, onDone](int exitCode, QProcess::ExitStatus) {
            proc->deleteLater();
            QFile::remove(zipPath);

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

bool PluginStoreManager::createTempPluginZip(const QByteArray &data, QString &zipPath) const {
    QTemporaryFile tempZip(QDir::tempPath() + QStringLiteral("/quol_plugin_XXXXXX.zip"));
    tempZip.setAutoRemove(false);
    if (!tempZip.open())
        return false;
    tempZip.write(data);
    tempZip.close();
    zipPath = tempZip.fileName();
    return true;
}

bool PluginStoreManager::checkPluginDependency(
    const QString &pluginDir, const QString &appVersion, QString &errorMessage
) const {
    if (appVersion.isEmpty())
        return true;

    const QString dependency = readJsonObjectFile(pluginDir + QStringLiteral("/res/config.json"))
                                   .value(QStringLiteral("_"))
                                   .toObject()
                                   .value(QStringLiteral("dependency"))
                                   .toString();
    if (!dependency.isEmpty() && compareVersions(appVersion, dependency) < 0) {
        errorMessage = QStringLiteral("This plugin requires Quol v%1 or newer.").arg(dependency);
        return false;
    }
    return true;
}

void PluginStoreManager::applyPendingUpdates() {
    const QString pluginsDir = QCoreApplication::applicationDirPath() + QStringLiteral("/plugins");
    const QFileInfoList staged = QDir(pluginsDir).entryInfoList(QStringList{QStringLiteral("*_updated")}, QDir::Dirs);
    if (staged.isEmpty())
        return;

    const QString suffix = QStringLiteral("_updated");

    for (const QFileInfo &entry : staged) {
        if (!entry.fileName().endsWith(suffix))
            continue;

        const QString pluginName = entry.fileName().left(entry.fileName().size() - suffix.size());
        const QString pluginDir = pluginsDir + QStringLiteral("/") + pluginName;
        const QString oldDir = pluginsDir + QStringLiteral("/") + pluginName + QStringLiteral("_old");

        // a previous instance may still be shutting down and holding the old DLL mapped
        bool oldMoved = !QDir(pluginDir).exists();
        for (int attempt = 0; !oldMoved && attempt < 40; ++attempt) {
            QThread::msleep(250);
            oldMoved = QDir().rename(pluginDir, oldDir);
        }
        if (!oldMoved) {
            qWarning() << "Could not move the old plugin folder aside for" << pluginName;
            continue;
        }

        if (!QDir().rename(entry.filePath(), pluginDir)) {
            qWarning() << "Could not install the staged update for" << pluginName;
            if (!QDir(pluginDir).exists() && QDir(oldDir).exists())
                QDir().rename(oldDir, pluginDir);
            QDir(entry.filePath()).removeRecursively();
            continue;
        }

        if (QDir(oldDir).exists())
            QDir(oldDir).removeRecursively();
    }
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
            emit pluginDownloadFinished(pluginName, false, reply->errorString(), false);
            return;
        }

        QString zipPath;
        if (!createTempPluginZip(reply->readAll(), zipPath)) {
            emit pluginDownloadFinished(
                pluginName, false, QStringLiteral("Failed to write the downloaded file to disk."), false
            );
            return;
        }

        const QString pluginsDir = QCoreApplication::applicationDirPath() + QStringLiteral("/plugins");
        const QString pluginDir = pluginsDir + QStringLiteral("/") + pluginName;

        // a DLL loaded in this process cannot be renamed or overwritten mid-process, so
        // updates stage beside the live folder and are swapped in on the next start;
        // fresh installs extract straight into place
        const QString stagingDir = pluginsDir + QStringLiteral("/") + pluginName + QStringLiteral("_updated");
        const bool staging = isUpdate && QDir(pluginDir).exists();
        const QString targetDir = staging ? stagingDir : pluginDir;

        if (QDir(targetDir).exists())
            QDir(targetDir).removeRecursively();
        if (!QDir().mkpath(targetDir)) {
            QFile::remove(zipPath);
            emit pluginDownloadFinished(
                pluginName, false, QStringLiteral("Failed to create the plugin folder."), false
            );
            return;
        }

        extractZipAsync(
            zipPath, targetDir, pluginName, [this, pluginName, targetDir, appVersion, staging](bool extracted) {
                bool ok = extracted;
                QString errorMessage;
                if (ok)
                    ok = checkPluginDependency(targetDir, appVersion, errorMessage);
                if (!ok && errorMessage.isEmpty())
                    errorMessage =
                        QStringLiteral("The plugin ZIP could not be unpacked, or required files are missing.");

                if (ok) {
                    emit pluginDownloadFinished(pluginName, true, QString(), staging);
                    return;
                }

                QDir(targetDir).removeRecursively();
                emit pluginDownloadFinished(pluginName, false, errorMessage, false);
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

    QFile srcFile(zipFilePath);
    if (!srcFile.open(QIODevice::ReadOnly)) {
        emit localPluginInstallFinished(pluginName, false);
        return;
    }
    const QByteArray data = srcFile.readAll();
    srcFile.close();

    QString zipPath;
    if (!createTempPluginZip(data, zipPath)) {
        emit localPluginInstallFinished(pluginName, false);
        return;
    }

    if (!QDir().mkpath(pluginDir)) {
        QFile::remove(zipPath);
        emit localPluginInstallFinished(pluginName, false);
        return;
    }

    extractZipAsync(zipPath, pluginDir, pluginName, [this, pluginName, pluginDir](bool ok) {
        if (!ok && QDir(pluginDir).exists()) {
            QDir(pluginDir).removeRecursively();
        }
        emit localPluginInstallFinished(pluginName, ok);
    });
}
