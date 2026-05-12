#include "plugins/chat/lib/ChatConfig.hpp"

#include <QJsonArray>

namespace chat::config {

ParsedConfig parse(const QJsonObject &pluginConfig) {
    ParsedConfig out;

    const QJsonObject hidden = pluginConfig.value("_").toObject();
    if (hidden.contains("providers") && hidden.value("providers").isArray()) {
        QStringList providers;
        const QJsonArray arr = hidden.value("providers").toArray();
        for (const auto &v : arr) {
            const QString p = v.toString().trimmed().toLower();
            if (!p.isEmpty())
                providers.append(p);
        }
        if (!providers.isEmpty())
            out.providers = providers;
    }

    out.providerIndex = hidden.value("provider_index").toInt(0);
    if (out.providerIndex < 0 || out.providerIndex >= out.providers.size())
        out.providerIndex = 0;

    out.includeImage = hidden.value("include_image").toBool(true);

    const QJsonObject cfg = pluginConfig.value("config").toObject();
    out.historyEnabled = cfg.value("history").toBool(true);
    out.maxHistory = qMax(0, cfg.value("max_history").toInt(10));
    out.snipPrompt = cfg.value("snip").toString(QStringLiteral("What is this image?"));

    const QJsonObject commands = pluginConfig.value("commands").toObject();
    for (auto it = commands.begin(); it != commands.end(); ++it)
        out.commands.insert(it.key(), it.value().toString());

    out.models["ollama"] = pluginConfig.value("ollama").toObject().value("model").toString("gemma3");
    out.models["gemini"] = pluginConfig.value("gemini").toObject().value("model").toString("gemini-2.5-flash");
    out.models["groq"] =
        pluginConfig.value("groq").toObject().value("model").toString("meta-llama/llama-4-scout-17b-16e-instruct");

    out.apiKeys["gemini"] = pluginConfig.value("gemini").toObject().value("apikey").toString();
    out.apiKeys["groq"] = pluginConfig.value("groq").toObject().value("apikey").toString();

    return out;
}

}  // namespace chat::config
