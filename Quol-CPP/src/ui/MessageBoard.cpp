#include "ui/MessageBoard.hpp"

#include <QGuiApplication>
#include <QHBoxLayout>
#include <QJsonDocument>
#include <QJsonObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QPushButton>
#include <QScreen>
#include <QScrollBar>
#include <QShowEvent>
#include <QTextBrowser>
#include <QTextEdit>
#include <QVBoxLayout>

static const char *kNotesBaseUrl = "https://leo-s-website-backend-695678049922.northamerica-northeast2.run.app/quol";

MessageBoard::MessageBoard(const QString &adminKey, QWidget *parent)
    : QuolPopupWindow(QStringLiteral("Message Board"), parent)
    , m_adminKey(adminKey)
    , m_network(new QNetworkAccessManager(this)) {

    auto *container = new QWidget();
    auto *layout = new QVBoxLayout(container);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(6);

    m_viewWidget = new QTextBrowser();
    m_viewWidget->setOpenExternalLinks(false);
    m_viewWidget->setReadOnly(true);

    m_editWidget = new QTextEdit();
    m_editWidget->hide();

    m_refreshBtn = new QPushButton(QStringLiteral("Refresh"));
    connect(m_refreshBtn, &QPushButton::clicked, this, &MessageBoard::refreshData);

    m_toggleBtn = new QPushButton(QStringLiteral("Edit"));
    connect(m_toggleBtn, &QPushButton::clicked, this, &MessageBoard::toggleMode);

    if (m_adminKey.isEmpty())
        m_toggleBtn->hide();

    auto *buttonBar = new QHBoxLayout();
    buttonBar->addWidget(m_refreshBtn);
    buttonBar->addWidget(m_toggleBtn);

    layout->addLayout(buttonBar);
    layout->addWidget(m_viewWidget);
    layout->addWidget(m_editWidget);

    addContent(container);

    const QRect screen = QGuiApplication::primaryScreen()->geometry();
    resize(400, 400);
    move(screen.center().x() - 200, screen.center().y() - 200);
}

void MessageBoard::setText(const QString &text) {
    m_viewWidget->setPlainText(text);
    m_editWidget->setPlainText(text);
}

void MessageBoard::refreshData() {
    m_refreshBtn->setEnabled(false);
    setText(QStringLiteral("Loading notes from server..."));
    fetchNotes();
}

void MessageBoard::fetchNotes() {
    QNetworkRequest request(QUrl(QString::fromLatin1(kNotesBaseUrl) + QStringLiteral("/notes")));
    request.setRawHeader("User-Agent", "Quol-App");

    QNetworkReply *reply = m_network->get(request);
    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        reply->deleteLater();
        m_refreshBtn->setEnabled(true);
        if (reply->error() != QNetworkReply::NoError) {
            onWorkerError(reply->errorString());
            return;
        }
        const QString text = QString::fromUtf8(reply->readAll());
        setText(text);
    });
}

void MessageBoard::postNotes() {
    if (m_adminKey.isEmpty())
        return;

    m_toggleBtn->setEnabled(false);
    const QString text = m_editWidget->toPlainText();
    setText(QStringLiteral("Saving notes to server..."));

    QJsonObject body;
    body.insert(QStringLiteral("notes"), text);

    QNetworkRequest request(
        QUrl(QString::fromLatin1(kNotesBaseUrl) + QStringLiteral("/notes/") + m_adminKey)
    );
    request.setHeader(QNetworkRequest::ContentTypeHeader, QStringLiteral("application/json"));
    request.setRawHeader("User-Agent", "Quol-App");

    QNetworkReply *reply = m_network->post(request, QJsonDocument(body).toJson(QJsonDocument::Compact));
    connect(reply, &QNetworkReply::finished, this, [this, reply, text]() {
        reply->deleteLater();
        m_toggleBtn->setEnabled(true);
        if (reply->error() != QNetworkReply::NoError) {
            onWorkerError(reply->errorString());
            return;
        }
        setText(text);
    });
}

void MessageBoard::toggleMode() {
    m_editMode = !m_editMode;
    if (m_editMode)
        enableEditMode();
    else {
        enableViewMode();
        postNotes();
    }
}

void MessageBoard::enableEditMode() {
    const int pos = m_viewWidget->verticalScrollBar()->value();
    m_editWidget->setPlainText(m_viewWidget->toPlainText());

    m_viewWidget->hide();
    m_editWidget->show();

    m_editWidget->verticalScrollBar()->setValue(pos);
    m_toggleBtn->setText(QStringLiteral("View"));
}

void MessageBoard::enableViewMode() {
    const int pos = m_editWidget->verticalScrollBar()->value();
    const QString text = m_editWidget->toPlainText();

    m_viewWidget->setPlainText(text);
    m_editWidget->hide();
    m_viewWidget->show();

    m_viewWidget->verticalScrollBar()->setValue(pos);
    m_toggleBtn->setText(QStringLiteral("Edit"));
}

void MessageBoard::showEvent(QShowEvent *event) {
    if (!event->spontaneous())
        refreshData();
    QuolPopupWindow::showEvent(event);
}

void MessageBoard::onWorkerError(const QString &error) {
    m_refreshBtn->setEnabled(true);
    m_toggleBtn->setEnabled(true);
    m_viewWidget->setPlainText(QStringLiteral("Error communicating with server."));
}
