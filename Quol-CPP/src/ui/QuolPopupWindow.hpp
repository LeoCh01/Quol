#pragma once

#include <QWidget>
#include <functional>

class TitleBar;
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

private:
    void updateMask();

    TitleBar *m_titleBar = nullptr;
    QVBoxLayout *m_bodyLayout = nullptr;
};
