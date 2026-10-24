#include "ui/QuolWindowLayout.hpp"
#include "ui/TitleBar.hpp"

#include <QGuiApplication>
#include <QPainterPath>
#include <QRegion>
#include <QScreen>
#include <QVBoxLayout>
#include <QWidget>

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

void quolApplyRoundedMask(QWidget *widget) {
    QPainterPath path;
    path.addRoundedRect(widget->rect(), 6, 6);
    widget->setMask(QRegion(path.toFillPolygon().toPolygon()));
}

void quolCenterOnScreen(QWidget *widget) {
    const QScreen *screen = widget->screen() ? widget->screen() : QGuiApplication::primaryScreen();
    if (!screen)
        return;
    const QRect area = screen->availableGeometry();
    widget->move(area.center().x() - widget->width() / 2,
                 area.center().y() - widget->height() / 2);
}