#include "plugins/chat/lib/providers/GeminiProvider.hpp"

#include <QJsonArray>

namespace chat::providers::gemini {

ProviderRequest buildRequest(
    const ProviderConfig &config,
    const QVector<HistoryItem> &history,
    const QString &prompt,
    const QString &imageBase64,
    bool includeHistory
) {
    ProviderRequest req;
    req.providerName = QStringLiteral("gemini");
    req.url = QUrl(QString("https://generativelanguage.googleapis.com/v1beta/models/%1:generateContent?key=%2")
                       .arg(config.model, config.apiKey));

    QJsonArray contents;

    if (includeHistory) {
        for (const auto &item : history) {
            QJsonObject c;
            c.insert("role", item.role == "model" ? "model" : "user");
            QJsonArray parts;
            parts.append(QJsonObject{{"text", item.text}});
            if (!item.imageBase64.isEmpty()) {
                parts.append(
                    QJsonObject{{"inline_data", QJsonObject{{"mime_type", "image/png"}, {"data", item.imageBase64}}}}
                );
            }
            c.insert("parts", parts);
            contents.append(c);
        }
    }

    QJsonObject cur;
    cur.insert("role", "user");
    QJsonArray parts;
    parts.append(QJsonObject{{"text", prompt}});
    if (!imageBase64.isEmpty()) {
        parts.append(QJsonObject{{"inline_data", QJsonObject{{"mime_type", "image/png"}, {"data", imageBase64}}}});
    }
    cur.insert("parts", parts);
    contents.append(cur);

    req.payload.insert("contents", contents);
    return req;
}

QString parseResponse(const QJsonObject &response) {
    const QJsonArray candidates = response.value("candidates").toArray();
    if (candidates.isEmpty())
        return {};

    const QJsonObject content = candidates.at(0).toObject().value("content").toObject();
    const QJsonArray parts = content.value("parts").toArray();
    if (parts.isEmpty())
        return {};

    return parts.at(0).toObject().value("text").toString();
}

}  // namespace chat::providers::gemini
