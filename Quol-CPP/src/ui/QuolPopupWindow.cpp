#include "ui/QuolPopupWindow.hpp"
#include "ui/QuolWindowLayout.hpp"
#include "ui/TitleBar.hpp"

#include <QResizeEvent>
#include <QTimer>
#include <QVBoxLayout>

QuolPopupWindow::QuolPopupWindow(const QString &title, QWidget *parent) : QWidget(parent) {
    setWindowFlags(Qt::FramelessWindowHint | Qt::Tool);
    setAttribute(Qt::WA_DeleteOnClose);

    quolInitBaseLayout(this, title, m_titleBar, m_bodyLayout);
    m_titleBar->setCloseAction([this]() { close(); });

    quolApplyRoundedMask(this);
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
        QTimer::singleShot(0, this, [this]() { quolCenterOnScreen(this); });
    }
}

void QuolPopupWindow::resizeEvent(QResizeEvent *event) {
    QWidget::resizeEvent(event);
    quolApplyRoundedMask(this);
}
