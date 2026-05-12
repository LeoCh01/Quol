#include "plugins/chat/Chat.hpp"

#include "plugins/chat/lib/ChatConfig.hpp"
#include "plugins/chat/lib/SnipOverlay.hpp"
#include "plugins/chat/lib/providers/GeminiProvider.hpp"
#include "plugins/chat/lib/providers/GroqProvider.hpp"
#include "plugins/chat/lib/providers/OllamaProvider.hpp"
#include "ui/QuolPopupWindow.hpp"

#include <QBuffer>
#include <QDateTime>
#include <QDir>
#include <QFile>
#include <QGuiApplication>
#include <QHBoxLayout>
#include <QIcon>
#include <QImage>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLineEdit>
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QPushButton>
#include <QRegularExpression>
#include <QScreen>
#include <QScrollBar>
#include <QTextBrowser>
#include <QUrl>
#include <QWidget>

namespace {
QString escapeHtml(const QString &value) {
    return value.toHtmlEscaped().replace("\n", "<br/>");
}
}  // namespace

QWidget *Chat::createWidget(QWidget *parent) {
    m_widget = new QWidget(parent);
    m_layout = new QHBoxLayout(m_widget);
    m_layout->setContentsMargins(0, 0, 0, 0);
    m_layout->setSpacing(4);

    m_cycleButton = new QPushButton(m_widget);
    m_clearButton = new QPushButton(m_widget);
    m_promptEdit = new QLineEdit(m_widget);
    m_includeImageButton = new QPushButton(m_widget);
    m_snipButton = new QPushButton(m_widget);

    m_includeImageButton->setCheckable(true);
    const QSize iconSize(18, 18);

    m_cycleButton->setIconSize(iconSize);
    m_clearButton->setIconSize(iconSize);
    m_includeImageButton->setIconSize(iconSize);
    m_snipButton->setIconSize(iconSize);

    m_cycleButton->setToolTip(QStringLiteral("Cycle provider"));
    m_clearButton->setToolTip(QStringLiteral("Clear message"));
    m_includeImageButton->setToolTip(QStringLiteral("Include screenshot"));
    m_snipButton->setToolTip(QStringLiteral("Snip mode"));

    m_layout->addWidget(m_cycleButton);
    m_layout->addWidget(m_clearButton);
    m_layout->addWidget(m_promptEdit, 1);
    m_layout->addWidget(m_includeImageButton);
    m_layout->addWidget(m_snipButton);

    QObject::connect(m_cycleButton, &QPushButton::clicked, this, &Chat::cycleProvider);
    QObject::connect(m_clearButton, &QPushButton::clicked, this, &Chat::clearMessage);
    QObject::connect(m_includeImageButton, &QPushButton::clicked, this, [this]() {
        m_includeImage = m_includeImageButton->isChecked();
        updateIncludeImageUi();
    });
    QObject::connect(m_snipButton, &QPushButton::clicked, this, [this]() { startSnipMode(); });
    QObject::connect(m_promptEdit, &QLineEdit::returnPressed, this, [this]() { submitPrompt(); });

    if (!m_network)
        m_network = new QNetworkAccessManager(this);

    applyButtonIcons();
    applyConfig();
    return m_widget;
}

void Chat::initialize(const QString &pluginRootPath, const QJsonObject &appSettings, const QJsonObject &pluginConfig) {
    Q_UNUSED(appSettings)
    m_pluginRootPath = pluginRootPath;
    m_pluginConfig = pluginConfig;

    applyConfig();
}

void Chat::onUpdateConfig(const QJsonObject &pluginConfig) {
    m_pluginConfig = pluginConfig;
    applyConfig();
}

void Chat::shutdown() {
    cancelSnipMode();

    if (m_reply) {
        m_reply->abort();
        m_reply->deleteLater();
        m_reply = nullptr;
    }

    if (m_outputWindow) {
        m_outputWindow->close();
        m_outputWindow = nullptr;
    }

    m_layout = nullptr;
    m_cycleButton = nullptr;
    m_clearButton = nullptr;
    m_promptEdit = nullptr;
    m_includeImageButton = nullptr;
    m_snipButton = nullptr;
    m_widget = nullptr;
}

void Chat::applyConfig() {
    const auto parsed = chat::config::parse(m_pluginConfig);

    m_providers = parsed.providers;
    m_providerIndex = parsed.providerIndex;
    m_includeImage = parsed.includeImage;
    m_historyEnabled = parsed.historyEnabled;
    m_maxHistory = parsed.maxHistory;
    m_snipPrompt = parsed.snipPrompt;

    m_commands = parsed.commands;
    m_models = parsed.models;
    m_apiKeys = parsed.apiKeys;

    applyButtonIcons();
    updatePromptPlaceholder();
    updateIncludeImageUi();
}

void Chat::applyButtonIcons() {
    if (m_pluginRootPath.isEmpty())
        return;

    // check issue later
    if (m_cycleButton)
        m_cycleButton->setIcon(QIcon(m_pluginRootPath + "/res/img/cycle.svg"));
    if (m_clearButton)
        m_clearButton->setIcon(QIcon(m_pluginRootPath + "/res/img/clear.svg"));
    if (m_includeImageButton)
        m_includeImageButton->setIcon(QIcon(m_pluginRootPath + "/res/img/img.svg"));
    if (m_snipButton)
        m_snipButton->setIcon(QIcon(m_pluginRootPath + "/res/img/snip.svg"));
}

void Chat::cycleProvider() {
    if (m_providers.isEmpty())
        return;
    m_providerIndex = (m_providerIndex + 1) % m_providers.size();
    updatePromptPlaceholder();
}

void Chat::clearMessage() {
    if (m_promptEdit)
        m_promptEdit->clear();
}

void Chat::updateIncludeImageUi() {
    if (!m_includeImageButton)
        return;

    m_includeImageButton->setChecked(m_includeImage);
    m_includeImageButton->setStyleSheet(
        m_includeImage ? QStringLiteral("background-color: #4CAF50;") : QStringLiteral("background-color: #F44336;")
    );

    m_includeImageButton->setToolTip(
        m_includeImage ? QStringLiteral("Include screenshot: ON") : QStringLiteral("Include screenshot: OFF")
    );
}

void Chat::submitPrompt(bool useExistingSnipImage) {
    if (!m_promptEdit || m_providers.isEmpty())
        return;

    QString prompt = m_promptEdit->text().trimmed();
    if (prompt.isEmpty())
        return;

    prompt = applyCommandTemplate(prompt);
    const QString provider = m_providers.value(m_providerIndex, QStringLiteral("groq"));

    QString imageBase64;
    if (m_includeImage) {
        if (useExistingSnipImage) {
            imageBase64 = m_pendingSnipImageBase64;
        } else {
            imageBase64 = capturePrimaryScreenBase64Png();
        }
    }

    addHistory(QStringLiteral("user"), prompt, imageBase64);
    appendLog(provider, true, prompt);

    m_pendingProvider = provider;

    setControlsEnabled(false);
    setOutputText(buildConversationHtml(QStringLiteral("Loading...")));

    dispatchProviderRequest(provider, prompt, imageBase64);

    m_promptEdit->clear();
}

void Chat::startSnipMode() {
    QScreen *screen = QGuiApplication::primaryScreen();
    if (!screen)
        return;

    const QPixmap screenshot = screen->grabWindow(0);
    cancelSnipMode();

    m_snipOverlay = new SnipOverlay(screenshot, [this](const QPixmap &cropped) { onSnipSelected(cropped); });
    QObject::connect(m_snipOverlay, &QObject::destroyed, this, [this]() { m_snipOverlay = nullptr; });
    m_snipOverlay->showFullScreen();
    m_snipOverlay->raise();
    m_snipOverlay->activateWindow();
}

void Chat::cancelSnipMode() {
    if (m_snipOverlay) {
        m_snipOverlay->close();
        m_snipOverlay->deleteLater();
        m_snipOverlay = nullptr;
    }
}

void Chat::onSnipSelected(const QPixmap &cropped) {
    if (cropped.isNull())
        return;

    m_pendingSnipImageBase64 = pixmapToBase64Png(cropped);

    if (m_promptEdit && m_promptEdit->text().trimmed().isEmpty())
        m_promptEdit->setText(m_snipPrompt);

    submitPrompt(true);
}

void Chat::ensureOutputWindow() {
    if (m_outputWindow)
        return;

    m_outputWindow = new QuolPopupWindow(QStringLiteral("Chat Output"), m_widget);
    QObject::connect(m_outputWindow, &QObject::destroyed, this, [this]() { m_outputWindow = nullptr; });
    m_outputWindow->resize(500, 400);
}

void Chat::setOutputText(const QString &html) {
    ensureOutputWindow();
    if (!m_outputWindow)
        return;

    // Get or create the text browser in the popup
    QWidget *content = m_outputWindow->findChild<QTextBrowser *>();
    QTextBrowser *browser = qobject_cast<QTextBrowser *>(content);

    if (!browser) {
        browser = new QTextBrowser(m_outputWindow);
        browser->setOpenExternalLinks(false);
        m_outputWindow->addContent(browser);
    }

    browser->setHtml(html);

    m_outputWindow->show();
    m_outputWindow->raise();
    m_outputWindow->activateWindow();
    auto *sb = browser->verticalScrollBar();
    sb->setValue(sb->maximum());
}

QString Chat::buildConversationHtml(const QString &pendingAssistantText) const {
    QString html = QStringLiteral("<html><body>");

    for (const auto &item : m_history) {
        const bool isModel = (item.role == QStringLiteral("model"));
        html += QStringLiteral(
                    "<div style='margin:8px 0; text-align:%1;'><span style='display:inline-block; padding:8px; "
                    "border-radius:8px; background:%2;'>%3</span></div>"
        )
                    .arg(
                        isModel ? QStringLiteral("left") : QStringLiteral("right"),
                        isModel ? QStringLiteral("#2A2A2A") : QStringLiteral("#164A8A"),
                        escapeHtml(item.text)
                    );
    }

    if (!pendingAssistantText.isEmpty()) {
        html += QStringLiteral(
                    "<div style='margin:8px 0; text-align:left;'><span style='display:inline-block; padding:8px; "
                    "border-radius:8px; background:#2A2A2A;'>%1</span></div>"
        )
                    .arg(escapeHtml(pendingAssistantText));
    }

    html += QStringLiteral("</body></html>");
    return html;
}

QString Chat::applyCommandTemplate(const QString &rawPrompt) const {
    const QStringList tokens = rawPrompt.split(' ', Qt::SkipEmptyParts);
    if (tokens.isEmpty())
        return rawPrompt;

    const QString cmd = tokens.first();
    if (!m_commands.contains(cmd))
        return rawPrompt;

    QString result = m_commands.value(cmd);
    for (int i = 1; i < tokens.size(); ++i) {
        result.replace(QString("{%1}").arg(i - 1), tokens.at(i));
    }

    QRegularExpression optionalExpr(R"(\{(\d+):([^}]+)\})");
    auto it = optionalExpr.globalMatch(result);
    while (it.hasNext()) {
        const auto m = it.next();
        result.replace(m.captured(0), m.captured(2));
    }

    QRegularExpression bareExpr(R"(\{\d+\})");
    result.remove(bareExpr);
    return result.trimmed();
}

QString Chat::capturePrimaryScreenBase64Png() const {
    QScreen *screen = QGuiApplication::primaryScreen();
    if (!screen)
        return {};

    return pixmapToBase64Png(screen->grabWindow(0));
}

QString Chat::pixmapToBase64Png(const QPixmap &pixmap) {
    if (pixmap.isNull())
        return {};

    QByteArray bytes;
    QBuffer buffer(&bytes);
    if (!buffer.open(QIODevice::WriteOnly))
        return {};

    pixmap.toImage().save(&buffer, "PNG");
    return QString::fromLatin1(bytes.toBase64());
}

void Chat::dispatchProviderRequest(const QString &provider, const QString &prompt, const QString &imageBase64) {
    chat::providers::ProviderConfig config{m_models.value(provider), m_apiKeys.value(provider)};
    chat::providers::ProviderRequest request;

    if (provider == "gemini") {
        request = chat::providers::gemini::buildRequest(config, m_history, prompt, imageBase64, m_historyEnabled);
    } else if (provider == "groq") {
        request = chat::providers::groq::buildRequest(config, m_history, prompt, imageBase64, m_historyEnabled);
    } else {
        request = chat::providers::ollama::buildRequest(config, m_history, prompt, imageBase64, m_historyEnabled);
    }

    sendJsonRequest(request);
}

void Chat::sendJsonRequest(const chat::providers::ProviderRequest &request) {
    if (!m_network)
        return;

    if (m_reply) {
        m_reply->deleteLater();
        m_reply = nullptr;
    }

    QNetworkRequest req(request.url);
    req.setHeader(QNetworkRequest::ContentTypeHeader, QStringLiteral("application/json"));
    if (!request.bearerToken.trimmed().isEmpty()) {
        req.setRawHeader("Authorization", QByteArray("Bearer ") + request.bearerToken.toUtf8());
    }

    m_pendingProvider = request.providerName;
    m_reply = m_network->post(req, QJsonDocument(request.payload).toJson(QJsonDocument::Compact));
    QObject::connect(m_reply, &QNetworkReply::finished, this, &Chat::onRequestFinished);
    QObject::connect(m_reply, &QNetworkReply::errorOccurred, this, &Chat::onRequestError);
}

void Chat::onRequestFinished() {
    if (!m_reply)
        return;

    const QByteArray raw = m_reply->readAll();
    const QJsonDocument doc = QJsonDocument::fromJson(raw);
    QString answer;

    if (doc.isObject()) {
        const QJsonObject obj = doc.object();
        if (obj.contains("error")) {
            answer = obj.value("error").toObject().value("message").toString();
            if (answer.isEmpty())
                answer = QStringLiteral("Unknown provider error");
            answer = QStringLiteral("Error: ") + answer;
        } else if (m_pendingProvider == "gemini") {
            answer = chat::providers::gemini::parseResponse(obj);
        } else if (m_pendingProvider == "groq") {
            answer = chat::providers::groq::parseResponse(obj);
        } else {
            answer = chat::providers::ollama::parseResponse(obj);
        }
    } else {
        answer = QString::fromUtf8(raw);
    }

    if (answer.trimmed().isEmpty())
        answer = QStringLiteral("(no response)");

    addHistory(QStringLiteral("model"), answer);
    appendLog(m_pendingProvider, false, answer);
    setOutputText(buildConversationHtml());
    setControlsEnabled(true);

    m_reply->deleteLater();
    m_reply = nullptr;
}

void Chat::onRequestError(QNetworkReply::NetworkError code) {
    Q_UNUSED(code)
    const QString msg = m_reply ? m_reply->errorString() : QStringLiteral("Unknown network error");
    setOutputText(buildConversationHtml(QStringLiteral("Error: ") + msg));
    setControlsEnabled(true);

    if (m_reply) {
        m_reply->deleteLater();
        m_reply = nullptr;
    }
}

void Chat::addHistory(const QString &role, const QString &text, const QString &imageBase64) {
    if (!m_historyEnabled)
        return;
    m_history.push_back({role, text, imageBase64});
    trimHistory();
}

void Chat::trimHistory() {
    const int limit = qMax(0, m_maxHistory) * 2;
    if (limit == 0) {
        m_history.clear();
        return;
    }
    while (m_history.size() > limit)
        m_history.removeFirst();
}

void Chat::appendLog(const QString &provider, bool isUser, const QString &text) const {
    const QString logsDir = m_pluginRootPath + "/res/logs";
    QDir().mkpath(logsDir);

    QFile f(logsDir + "/" + provider + ".log");
    if (!f.open(QIODevice::Append | QIODevice::Text))
        return;

    const QString ts = QDateTime::currentDateTime().toString(Qt::ISODate);
    const QString line = isUser ? QString("%1\nQ: %2\n").arg(ts, text) : QString("A: %1\n\n").arg(text);
    f.write(line.toUtf8());
    f.close();
}

void Chat::setControlsEnabled(bool enabled) {
    if (m_promptEdit)
        m_promptEdit->setEnabled(enabled);
    if (m_cycleButton)
        m_cycleButton->setEnabled(enabled);
    if (m_clearButton)
        m_clearButton->setEnabled(enabled);
    if (m_includeImageButton)
        m_includeImageButton->setEnabled(enabled);
    if (m_snipButton)
        m_snipButton->setEnabled(enabled);
}

void Chat::updatePromptPlaceholder() {
    if (!m_promptEdit)
        return;

    const QString provider = m_providers.value(m_providerIndex, QStringLiteral("groq"));
    m_promptEdit->setPlaceholderText(QStringLiteral("Prompt for %1...").arg(provider));
}
