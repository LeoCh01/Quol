#pragma once

#include "ui/QuolPopupWindow.hpp"

#include <QString>

class QNetworkAccessManager;
class QNetworkReply;
class QPushButton;
class QTextBrowser;
class QTextEdit;

class MessageBoard : public QuolPopupWindow {
    Q_OBJECT

public:
    explicit MessageBoard(const QString &adminKey, QWidget *parent = nullptr);

protected:
    void showEvent(QShowEvent *event) override;

private slots:
    void refreshData();
    void toggleMode();

private:
    void fetchNotes();
    void postNotes();
    void setText(const QString &text);
    void enableEditMode();
    void enableViewMode();
    void onWorkerError(const QString &error);

    QString m_adminKey;
    bool m_editMode = false;

    QTextBrowser *m_viewWidget = nullptr;
    QTextEdit *m_editWidget = nullptr;
    QPushButton *m_refreshBtn = nullptr;
    QPushButton *m_toggleBtn = nullptr;
    QNetworkAccessManager *m_network = nullptr;
};
