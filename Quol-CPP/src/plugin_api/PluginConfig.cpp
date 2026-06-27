#include "plugin_api/PluginConfig.hpp"

#include <QFile>
#include <QJsonDocument>

// ── ctor ──────────────────────────────────────────────────────────────────

PluginConfig::PluginConfig(const QJsonObject &obj, const QString &filePath) : m_root(obj), m_filePath(filePath) {
}

// ── I/O ───────────────────────────────────────────────────────────────────

bool PluginConfig::load(const QString &filePath) {
    if (!filePath.isEmpty())
        m_filePath = filePath;

    QFile f(m_filePath);
    if (!f.open(QIODevice::ReadOnly))
        return false;

    QJsonParseError err;
    const QJsonDocument doc = QJsonDocument::fromJson(f.readAll(), &err);
    f.close();

    if (err.error != QJsonParseError::NoError || !doc.isObject())
        return false;

    m_root = doc.object();
    return true;
}

bool PluginConfig::save() const {
    if (m_filePath.isEmpty())
        return false;

    QFile f(m_filePath);
    if (!f.open(QIODevice::WriteOnly | QIODevice::Truncate))
        return false;

    f.write(QJsonDocument(m_root).toJson());
    f.close();
    return true;
}

// ── helpers ───────────────────────────────────────────────────────────────

QStringList PluginConfig::splitPath(const QString &dotPath) {
    return dotPath.split(QLatin1Char('.'), Qt::SkipEmptyParts);
}

QJsonValue PluginConfig::readNested(const QJsonObject &obj, const QStringList &keys) {
    if (keys.isEmpty())
        return obj;

    const QJsonValue v = obj.value(keys.first());

    if (keys.size() == 1)
        return v;

    if (!v.isObject())
        return QJsonValue::Undefined;

    return readNested(v.toObject(), keys.mid(1));
}

QJsonObject PluginConfig::writeNested(QJsonObject obj, const QStringList &keys, const QJsonValue &value) {
    if (keys.isEmpty())
        return obj;

    const QString &key = keys.first();

    if (keys.size() == 1) {
        obj.insert(key, value);
        return obj;
    }

    QJsonObject child = obj.value(key).toObject();  // creates empty obj if missing/wrong type
    obj.insert(key, writeNested(child, keys.mid(1), value));
    return obj;
}

QJsonObject PluginConfig::removeNested(QJsonObject obj, const QStringList &keys) {
    if (keys.isEmpty())
        return obj;

    const QString &key = keys.first();

    if (keys.size() == 1) {
        obj.remove(key);
        return obj;
    }

    if (!obj.contains(key) || !obj.value(key).isObject())
        return obj;

    QJsonObject child = obj.value(key).toObject();
    obj.insert(key, removeNested(child, keys.mid(1)));
    return obj;
}

// ── public API ────────────────────────────────────────────────────────────

QJsonValue PluginConfig::get(const QString &dotPath, const QJsonValue &fallback) const {
    const QJsonValue v = readNested(m_root, splitPath(dotPath));
    return (v.isUndefined() || v.isNull()) ? fallback : v;
}

void PluginConfig::set(const QString &dotPath, const QJsonValue &value) {
    m_root = writeNested(m_root, splitPath(dotPath), value);
}

void PluginConfig::remove(const QString &dotPath) {
    m_root = removeNested(m_root, splitPath(dotPath));
}
