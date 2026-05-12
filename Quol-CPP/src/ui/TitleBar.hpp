#pragma once

#include <QFrame>
#include <QPoint>
#include <functional>

class QuolWindow;
class QPushButton;

class TitleBar : public QFrame {
    Q_OBJECT

public:
    explicit TitleBar(QWidget *window, const QString &title, QWidget *parent = nullptr);
    void setConfigAction(const std::function<void()> &onClick);
    void setCloseAction(const std::function<void()> &onClick);
    void setDragReleaseAction(const std::function<void()> &onRelease);

protected:
    void mousePressEvent(QMouseEvent *event) override;
    void mouseMoveEvent(QMouseEvent *event) override;
    void mouseReleaseEvent(QMouseEvent *event) override;

private:
    QWidget *m_window;
    QPoint m_dragOffset;
    bool m_dragging = false;
    std::function<void()> m_onDragRelease;
    QPushButton *m_configBtn = nullptr;
    QPushButton *m_closeBtn = nullptr;
};
