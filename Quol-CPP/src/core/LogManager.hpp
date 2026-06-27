#pragma once

#include <QFile>
#include <QMessageLogContext>
#include <QMutex>
#include <QObject>
#include <QString>

class LogManager : public QObject {
    Q_OBJECT

public:
    explicit LogManager(const QString &filePath, QObject *parent = nullptr);
    ~LogManager() override;

private:
    static void messageHandler(QtMsgType type, const QMessageLogContext &ctx, const QString &msg);

    QFile m_file;
    QMutex m_mutex;
    static LogManager *s_instance;
};
