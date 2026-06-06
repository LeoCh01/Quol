#pragma once

#include <QObject>
#include <QString>

class AppSettingsManager;
class QNetworkAccessManager;
class QNetworkReply;

class UpdateNotifier : public QObject {
    Q_OBJECT

public:
    explicit UpdateNotifier(AppSettingsManager *settings, QObject *parent = nullptr);

    // Fires off an async network request; shows a popup if a newer version is found.
    void checkForUpdate();

private:
    void onReplyFinished(QNetworkReply *reply, const QString &currentVersion);
    void showUpdatePopup(const QString &title, const QString &body);

    AppSettingsManager *m_settings;
    QNetworkAccessManager *m_network;
    bool m_popupShown = false;
};
