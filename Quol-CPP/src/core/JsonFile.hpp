#pragma once

#include <QJsonObject>
#include <QString>

// Reads the file at path and parses it as JSON.
// Returns an empty object if the file cannot be read or is not valid JSON.
QJsonObject readJsonObjectFile(const QString &path);

// Serializes obj to the file at path. Writes indented JSON unless compact.
// Returns true on success.
bool writeJsonObjectFile(const QString &path, const QJsonObject &obj, bool compact = false);