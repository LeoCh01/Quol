#include "ui/TitleBar.hpp"

#include <QCoreApplication>
#include <QHBoxLayout>
#include <QIcon>
#include <QLabel>
#include <QMouseEvent>
#include <QPushButton>

TitleBar::TitleBar(QWidget *window, const QString &title, QWidget *parent) : QFrame(parent), m_window(window) {
    setObjectName("title-bar");
    setFixedHeight(36);

    auto *layout = new QHBoxLayout(this);
    layout->setContentsMargins(10, 0, 8, 0);

    m_titleLabel = new QLabel(title, this);
    layout->addWidget(m_titleLabel, 1);

    m_configBtn = new QPushButton(this);
    m_configBtn->setToolTip("Open config");
    m_configBtn->setVisible(false);
    m_configBtn->setCursor(Qt::PointingHandCursor);
    m_configBtn->setFixedSize(24, 24);

    // Load the SVG icon for the config button
    const QString iconPath = QCoreApplication::applicationDirPath() + "/plugins/quol/res/img/config.svg";
    QIcon configIcon(iconPath);
    m_configBtn->setIcon(configIcon);
    layout->addWidget(m_configBtn);

    m_closeBtn = new QPushButton(this);
    m_closeBtn->setToolTip("Close");
    m_closeBtn->setVisible(false);
    m_closeBtn->setCursor(Qt::PointingHandCursor);
    m_closeBtn->setObjectName("close-btn");
    m_closeBtn->setFixedSize(24, 24);
    const QString closeIconPath = QCoreApplication::applicationDirPath() + "/plugins/quol/res/img/close.svg";
    m_closeBtn->setIcon(QIcon(closeIconPath));
    layout->addWidget(m_closeBtn);
}

void TitleBar::setTitle(const QString &title) {
    if (m_titleLabel)
        m_titleLabel->setText(title);
}

void TitleBar::setConfigAction(const std::function<void()> &onClick) {
    m_configBtn->setVisible(true);
    m_configBtn->disconnect();
    connect(m_configBtn, &QPushButton::clicked, this, [onClick]() {
        if (onClick) {
            onClick();
        }
    });
}

void TitleBar::setCloseAction(const std::function<void()> &onClick) {
    m_closeBtn->setVisible(true);
    m_closeBtn->disconnect();
    connect(m_closeBtn, &QPushButton::clicked, this, [onClick]() {
        if (onClick) {
            onClick();
        }
    });
}

void TitleBar::setDragReleaseAction(const std::function<void()> &onRelease) {
    m_onDragRelease = onRelease;
}

void TitleBar::mousePressEvent(QMouseEvent *event) {
    if (event->button() == Qt::LeftButton) {
        m_dragOffset = event->globalPosition().toPoint() - m_window->pos();
        m_dragging = true;
        m_window->setWindowOpacity(0.8);
    }
    event->accept();
}

void TitleBar::mouseMoveEvent(QMouseEvent *event) {
    if (m_dragging && (event->buttons() & Qt::LeftButton))
        m_window->move(event->globalPosition().toPoint() - m_dragOffset);
    event->accept();
}

void TitleBar::mouseReleaseEvent(QMouseEvent *event) {
    if (event->button() == Qt::LeftButton && m_dragging) {
        m_dragging = false;
        m_window->setWindowOpacity(1.0);
        if (m_onDragRelease) {
            m_onDragRelease();
        }
    }
    event->accept();
}
