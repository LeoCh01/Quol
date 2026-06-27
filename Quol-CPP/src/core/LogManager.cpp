#include "core/LogManager.hpp"

#include <QDateTime>
#include <QDir>
#include <QFileInfo>
#include <QtGlobal>

LogManager *LogManager::s_instance = nullptr;

LogManager::LogManager(const QString &filePath, QObject *parent) : QObject(parent) {
    QDir().mkpath(QFileInfo(filePath).absolutePath());
    m_file.setFileName(filePath);
    if (!m_file.open(QIODevice::Append | QIODevice::Text | QIODevice::Unbuffered)) {
        qWarning("LogManager: failed to open log file: %s", qPrintable(filePath));
    }

    s_instance = this;
    qInstallMessageHandler(messageHandler);
}

LogManager::~LogManager() {
    qInstallMessageHandler(nullptr);
    s_instance = nullptr;
    if (m_file.isOpen())
        m_file.close();
}

void LogManager::messageHandler(QtMsgType type, const QMessageLogContext &ctx, const QString &msg) {
    if (!s_instance)
        return;

    QMutexLocker lock(&s_instance->m_mutex);

    const QString timestamp = QDateTime::currentDateTime().toString(QStringLiteral("yyyy-MM-dd HH:mm:ss.zzz"));

    const char *level = "";
    switch (type) {
        case QtDebugMsg:
            level = "DEBUG";
            break;
        case QtInfoMsg:
            level = "INFO";
            break;
        case QtWarningMsg:
            level = "WARNING";
            break;
        case QtCriticalMsg:
            level = "CRITICAL";
            break;
        case QtFatalMsg:
            level = "FATAL";
            break;
    }

    const QString line = QStringLiteral("[%1] [%2] %3\n").arg(timestamp, QString::fromLatin1(level), msg);

    s_instance->m_file.write(line.toUtf8());

    if (type == QtFatalMsg) {
        s_instance->m_file.flush();
        abort();
    }
}
