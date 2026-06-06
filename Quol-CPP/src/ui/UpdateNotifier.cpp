#include "ui/UpdateNotifier.hpp"
#include "core/AppSettingsManager.hpp"

#include <QAbstractButton>
#include <QDesktopServices>
#include <QEventLoop>
#include <QJsonDocument>
#include <QJsonObject>
#include <QMessageBox>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QPushButton>
#include <QUrl>

static constexpr auto kRemoteSettingsUrl =
    "https://raw.githubusercontent.com/LeoCh01/Quol/CPP-migration/Quol-CPP/settings.json";
static constexpr auto kRepoUrl = "https://github.com/LeoCh01/Quol";
static constexpr auto kUnknownVersion = "N/A";

UpdateNotifier::UpdateNotifier(AppSettingsManager *settings, QObject *parent)
    : QObject(parent), m_settings(settings), m_network(new QNetworkAccessManager(this)) {
}

bool UpdateNotifier::checkForUpdateBlocking() {
    if (!m_settings->data().value(QStringLiteral("show_updates")).toBool(true))
        return true;

    const QString currentVersion = m_settings->settingString(QStringLiteral("version"));
    QString latestVersion = QString::fromLatin1(kUnknownVersion);

    QNetworkReply *reply = m_network->get(QNetworkRequest(QUrl(kRemoteSettingsUrl)));
    QEventLoop loop;
    connect(reply, &QNetworkReply::finished, &loop, &QEventLoop::quit);
    loop.exec();

    if (reply->error() == QNetworkReply::NoError) {
        const QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
        if (doc.isObject()) {
            const QString parsedVersion = doc.object().value(QStringLiteral("version")).toString();
            if (!parsedVersion.isEmpty())
                latestVersion = parsedVersion;
        }
    }
    reply->deleteLater();

    // Show popup on mismatch, or when update check failed (latest = N/A).
    if (latestVersion != currentVersion || latestVersion == QString::fromLatin1(kUnknownVersion)) {
        return showUpdatePopup(currentVersion, latestVersion);
    }

    return true;
}

bool UpdateNotifier::showUpdatePopup(const QString &currentVersion, const QString &latestVersion) {
    QMessageBox box;
    box.setWindowTitle(QStringLiteral("Update Available"));
    box.setIcon(QMessageBox::Information);
    box.setText(QStringLiteral("Current: %1\nLatest: %2").arg(currentVersion, latestVersion));
    box.setWindowFlag(Qt::WindowCloseButtonHint, true);

    box.addButton(QStringLiteral("Continue to App"), QMessageBox::AcceptRole);
    box.addButton(QStringLiteral("Open Repository"), QMessageBox::ActionRole);
    QAbstractButton *closeBtn = box.addButton(QMessageBox::Close);
    closeBtn->hide();
    box.setEscapeButton(closeBtn);

    box.exec();

    const QAbstractButton *clicked = box.clickedButton();
    if (clicked && clicked->text() == QStringLiteral("Continue to App"))
        return true;

    if (clicked && clicked->text() == QStringLiteral("Open Repository"))
        QDesktopServices::openUrl(QUrl(QString::fromLatin1(kRepoUrl)));

    // Close/X or Open Repository => do not continue into app.
    return false;
}
