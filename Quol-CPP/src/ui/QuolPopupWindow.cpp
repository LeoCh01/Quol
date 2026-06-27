#include "ui/QuolPopupWindow.hpp"
#include "ui/TitleBar.hpp"

#include <QGuiApplication>
#include <QPainterPath>
#include <QRegion>
#include <QResizeEvent>
#include <QScreen>
#include <QTimer>
#include <QVBoxLayout>

namespace {
void quolInitBaseLayout(QWidget *widget, const QString &title, TitleBar *&titleBarOut, QVBoxLayout *&bodyLayoutOut) {
    auto *rootLayout = new QVBoxLayout(widget);
    rootLayout->setContentsMargins(0, 0, 0, 0);
    rootLayout->setSpacing(0);

    titleBarOut = new TitleBar(widget, title, widget);
    rootLayout->addWidget(titleBarOut);

    auto *sep = new QWidget(widget);
    sep->setFixedHeight(1);
    sep->setStyleSheet("background-color: #2F2F2F;");
    rootLayout->addWidget(sep);

    auto *body = new QWidget(widget);
    body->setObjectName("content");
    bodyLayoutOut = new QVBoxLayout(body);
    bodyLayoutOut->setContentsMargins(8, 8, 8, 8);
    bodyLayoutOut->setSpacing(6);
    bodyLayoutOut->setAlignment(Qt::AlignTop);
    rootLayout->addWidget(body, 1);
}
}  // namespace

QuolPopupWindow::QuolPopupWindow(const QString &title, QWidget *parent) : QWidget(parent) {
    setWindowFlags(Qt::FramelessWindowHint | Qt::Tool);
    setAttribute(Qt::WA_DeleteOnClose);

    quolInitBaseLayout(this, title, m_titleBar, m_bodyLayout);
    m_titleBar->setCloseAction([this]() { close(); });

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

void QuolPopupWindow::showEvent(QShowEvent *event) {
    QWidget::showEvent(event);
    if (!m_centered) {
        m_centered = true;
        QTimer::singleShot(0, this, &QuolPopupWindow::centerOnScreen);
    }
}

void QuolPopupWindow::centerOnScreen() {
    if (QScreen *screen = QGuiApplication::primaryScreen()) {
        const QRect g = screen->availableGeometry();
        move(g.center().x() - width() / 2, g.center().y() - height() / 2);
    }
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
