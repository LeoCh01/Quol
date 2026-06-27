#pragma once

#include "ui/TitleBar.hpp"

#include <QWidget>
#include <functional>

class QVBoxLayout;
class QJsonObject;

class QuolPopupWindow : public QWidget {
    Q_OBJECT

public:
    explicit QuolPopupWindow(const QString &title, QWidget *parent = nullptr);

    TitleBar *titleBar() const;
    void addContent(QWidget *widget);
    void addContent(QLayout *layout);

protected:
    void resizeEvent(QResizeEvent *event) override;
    void showEvent(QShowEvent *event) override;

private:
    void centerOnScreen();
    void updateMask();

    bool m_centered = false;
    TitleBar *m_titleBar = nullptr;
    QVBoxLayout *m_bodyLayout = nullptr;
};
