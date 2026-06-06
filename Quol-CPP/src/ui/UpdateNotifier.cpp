#include "ui/UpdateNotifier.hpp"
#include "core/AppSettingsManager.hpp"
#include "ui/QuolPopupWindow.hpp"

#include <QDesktopServices>
#include <QGuiApplication>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLabel>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QPushButton>
#include <QScreen>
#include <QUrl>
#include <QVBoxLayout>

static constexpr auto kRemoteSettingsUrl = "https://raw.githubusercontent.com/LeoCh01/Quol/main/Quol-CPP/settings.json";
static constexpr auto kRepoUrl = "https://github.com/LeoCh01/Quol";

UpdateNotifier::UpdateNotifier(AppSettingsManager *settings, QObject *parent)
    : QObject(parent), m_settings(settings), m_network(new QNetworkAccessManager(this)) {
}

void UpdateNotifier::checkForUpdate() {
    if (!m_settings->data().value(QStringLiteral("show_updates")).toBool(true))
        return;

    const QString currentVersion = m_settings->settingString(QStringLiteral("version"));
    QNetworkReply *reply = m_network->get(QNetworkRequest(QUrl(kRemoteSettingsUrl)));
    connect(reply, &QNetworkReply::finished, this, [this, reply, currentVersion]() {
        onReplyFinished(reply, currentVersion);
    });
}

void UpdateNotifier::onReplyFinished(QNetworkReply *reply, const QString &currentVersion) {
    reply->deleteLater();

    if (m_popupShown)
        return;

    if (reply->error() != QNetworkReply::NoError) {
        showUpdatePopup(
            QStringLiteral("Update Check Failed"),
            QStringLiteral("Could not verify the latest version. Open the repository to check updates manually?")
        );
        return;
    }

    const QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
    if (doc.isNull() || !doc.isObject()) {
        showUpdatePopup(
            QStringLiteral("Update Check Failed"),
            QStringLiteral("Received an invalid update response. Open the repository to check updates manually?")
        );
        return;
    }

    const QString remoteVersion = doc.object().value(QStringLiteral("version")).toString();
    if (remoteVersion.isEmpty()) {
        showUpdatePopup(
            QStringLiteral("Update Check Failed"),
            QStringLiteral("Update version is missing. Open the repository to check updates manually?")
        );
        return;
    }

    if (remoteVersion != currentVersion) {
        showUpdatePopup(
            QStringLiteral("Update Available"),
            QStringLiteral("Detected version mismatch.\nCurrent: %1\nLatest: %2").arg(currentVersion, remoteVersion)
        );
    }
}

void UpdateNotifier::showUpdatePopup(const QString &title, const QString &body) {
    if (m_popupShown)
        return;
    m_popupShown = true;

    auto *popup = new QuolPopupWindow(title);

    auto *label = new QLabel(body);
    label->setWordWrap(true);
    label->setAlignment(Qt::AlignCenter);

    auto *repoBtn = new QPushButton(QStringLiteral("Open Repository"));
    auto *continueBtn = new QPushButton(QStringLiteral("Continue to App"));

    connect(repoBtn, &QPushButton::clicked, popup, [popup]() {
        QDesktopServices::openUrl(QUrl(kRepoUrl));
        popup->close();
    });
    connect(continueBtn, &QPushButton::clicked, popup, &QWidget::close);

    popup->addContent(label);
    popup->addContent(repoBtn);
    popup->addContent(continueBtn);

    popup->adjustSize();
    const QRect screen = QGuiApplication::primaryScreen()->availableGeometry();
    popup->move(screen.center() - QPoint(popup->width() / 2, popup->height() / 2));
    popup->show();
    popup->raise();
    popup->activateWindow();
}
