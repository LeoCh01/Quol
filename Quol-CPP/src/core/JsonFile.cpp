#include "core/JsonFile.hpp"

#include <QFile>
#include <QJsonDocument>

QJsonObject readJsonObjectFile(const QString &path) {
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
        return {};
    const QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    file.close();
    return doc.object();
}

bool writeJsonObjectFile(const QString &path, const QJsonObject &obj, bool compact) {
    QFile file(path);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Text | QIODevice::Truncate))
        return false;
    file.write(QJsonDocument(obj).toJson(compact ? QJsonDocument::Compact : QJsonDocument::Indented));
    file.close();
    return true;
}