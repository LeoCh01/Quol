#pragma once

#include <QJsonObject>
#include <QJsonValue>
#include <QString>
#include <QStringList>

// PluginConfig — convenience wrapper around a plugin's config.json.
//
// Keys use dot-notation to address nested objects:
//   "_.provider_index"   →  root["_"]["provider_index"]
//   "config.history"     →  root["config"]["history"]
//   "groq.model"         →  root["groq"]["model"]
//
// Typical usage in a plugin:
//
//   void MyPlugin::initialize(const QString &rootPath,
//                             const QJsonObject &pluginConfig,
//                             QuolServices *) {
//       m_cfg = PluginConfig(pluginConfig, rootPath + "/res/config.json");
//       int idx = m_cfg.get("_.provider_index", 0).toInt();
//   }
//
//   void MyPlugin::onUpdateConfig(const QJsonObject &pluginConfig) {
//       m_cfg.setRoot(pluginConfig);   // host already reloaded it
//   }
//
//   // When you want to persist a change at runtime:
//   m_cfg.set("_.provider_index", 2);
//   m_cfg.save();
//
class PluginConfig {
public:
    PluginConfig() = default;

    // Wrap an existing QJsonObject (e.g. from initialize()) and remember
    // where to save it.
    explicit PluginConfig(const QJsonObject &obj, const QString &filePath = {});

    // Load from file on disk (also sets the file path for future save() calls).
    bool load(const QString &filePath);

    // Write the current root back to m_filePath. Returns false on error.
    bool save() const;

    // ── Accessors ──────────────────────────────────────────────────────────

    // Read a value at dotPath.  Returns fallback if any key in the chain
    // is missing or the final value is Undefined.
    QJsonValue get(const QString &dotPath, const QJsonValue &fallback = QJsonValue::Undefined) const;

    // Write value at dotPath, creating intermediate objects as needed.
    void set(const QString &dotPath, const QJsonValue &value);

    // Remove the key at dotPath (no-op if absent).
    void remove(const QString &dotPath);

    // Direct access to the underlying object.
    QJsonObject root() const {
        return m_root;
    }
    void setRoot(const QJsonObject &obj) {
        m_root = obj;
    }

    QString filePath() const {
        return m_filePath;
    }
    void setFilePath(const QString &path) {
        m_filePath = path;
    }

private:
    static QStringList splitPath(const QString &dotPath);

    // Recursively read a nested value following the key list.
    static QJsonValue readNested(const QJsonObject &obj, const QStringList &keys);

    // Recursively write a nested value into a *copy* of obj and return it.
    static QJsonObject writeNested(QJsonObject obj, const QStringList &keys, const QJsonValue &value);

    // Recursively remove the leaf key and return the modified copy.
    static QJsonObject removeNested(QJsonObject obj, const QStringList &keys);

    QJsonObject m_root;
    QString m_filePath;
};
