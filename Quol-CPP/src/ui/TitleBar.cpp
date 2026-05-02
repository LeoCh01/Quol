#include "ui/TitleBar.hpp"
#include "ui/QuolWindow.hpp"

#include <QHBoxLayout>
#include <QLabel>
#include <QMouseEvent>
#include <QPushButton>

TitleBar::TitleBar(QuolWindow* window, const QString& title, QWidget* parent)
    : QFrame(parent)
    , m_window(window)
{
    setObjectName("title-bar");
    setFixedHeight(36);
    setCursor(Qt::SizeAllCursor);

    auto* layout = new QHBoxLayout(this);
    layout->setContentsMargins(10, 0, 8, 0);

    auto* label = new QLabel(title, this);
    layout->addWidget(label, 1);

    m_configBtn = new QPushButton(QString::fromUtf8("⚙"), this);
    m_configBtn->setToolTip("Open config");
    m_configBtn->setVisible(false);
    layout->addWidget(m_configBtn);
}

void TitleBar::setConfigAction(const std::function<void()>& onClick)
{
    if (!m_configBtn)
    {
        return;
    }

    m_configBtn->setVisible(true);
    m_configBtn->disconnect();
    connect(m_configBtn, &QPushButton::clicked, this, [onClick]() {
        if (onClick)
        {
            onClick();
        }
    });
}

void TitleBar::mousePressEvent(QMouseEvent* event)
{
    if (event->button() == Qt::LeftButton)
    {
        m_dragOffset = event->globalPosition().toPoint() - m_window->pos();
        m_dragging = true;
        m_window->setWindowOpacity(0.8);
    }
    event->accept();
}

void TitleBar::mouseMoveEvent(QMouseEvent* event)
{
    if (m_dragging && (event->buttons() & Qt::LeftButton))
        m_window->move(event->globalPosition().toPoint() - m_dragOffset);
    event->accept();
}

void TitleBar::mouseReleaseEvent(QMouseEvent* event)
{
    if (event->button() == Qt::LeftButton && m_dragging)
    {
        m_dragging = false;
        m_window->setWindowOpacity(1.0);
        m_window->snapToGrid();
    }
    event->accept();
}
