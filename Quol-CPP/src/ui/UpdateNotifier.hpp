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

    // Blocking check used at startup before showing app windows.
    // Returns true only when user explicitly chooses to continue.
    bool checkForUpdateBlocking();

private:
    bool showUpdatePopup(const QString &currentVersion, const QString &latestVersion);

    AppSettingsManager *m_settings;
    QNetworkAccessManager *m_network;
};
