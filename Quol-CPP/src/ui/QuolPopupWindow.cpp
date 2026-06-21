#include "ui/QuolPopupWindow.hpp"
#include "ui/QuolWindow.hpp"
#include "ui/TitleBar.hpp"

#include <QGuiApplication>
#include <QPainterPath>
#include <QRegion>
#include <QResizeEvent>
#include <QScreen>
#include <QTimer>
#include <QVBoxLayout>

QuolPopupWindow::QuolPopupWindow(const QString &title, QWidget *parent) : QWidget(parent) {
    setWindowFlags(Qt::FramelessWindowHint | Qt::Tool);
    setAttribute(Qt::WA_DeleteOnClose);

    QuolWindow::initBaseLayout(this, title, m_titleBar, m_bodyLayout);
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
