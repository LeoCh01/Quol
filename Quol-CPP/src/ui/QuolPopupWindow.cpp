#include "ui/QuolPopupWindow.hpp"
#include "ui/TitleBar.hpp"

#include <QPainterPath>
#include <QRegion>
#include <QResizeEvent>
#include <QVBoxLayout>

QuolPopupWindow::QuolPopupWindow(const QString &title, QWidget *parent) : QWidget(parent) {
    setWindowFlags(Qt::FramelessWindowHint | Qt::Tool);
    setAttribute(Qt::WA_DeleteOnClose);

    auto *rootLayout = new QVBoxLayout(this);
    rootLayout->setContentsMargins(0, 0, 0, 0);
    rootLayout->setSpacing(0);

    m_titleBar = new TitleBar(this, title, this);
    m_titleBar->setCloseAction([this]() { close(); });
    rootLayout->addWidget(m_titleBar);

    auto *sep = new QWidget(this);
    sep->setFixedHeight(1);
    sep->setStyleSheet("background-color: #2F2F2F;");
    rootLayout->addWidget(sep);

    auto *body = new QWidget(this);
    body->setObjectName("content");
    m_bodyLayout = new QVBoxLayout(body);
    m_bodyLayout->setContentsMargins(8, 8, 8, 8);
    m_bodyLayout->setSpacing(6);
    m_bodyLayout->setAlignment(Qt::AlignTop);
    rootLayout->addWidget(body, 1);

    updateMask();
}

TitleBar *QuolPopupWindow::titleBar() const {
    return m_titleBar;
}

void QuolPopupWindow::addContent(QWidget *widget) {
    m_bodyLayout->addWidget(widget);
}

void QuolPopupWindow::addContent(QLayout *layout) {
    m_bodyLayout->addLayout(layout);
}

void QuolPopupWindow::resizeEvent(QResizeEvent *event) {
    QWidget::resizeEvent(event);
    updateMask();
}

void QuolPopupWindow::updateMask() {
    QPainterPath path;
    path.addRoundedRect(rect(), 6, 6);
    setMask(QRegion(path.toFillPolygon().toPolygon()));
}
