#include "ui/SplashScreen.hpp"

#include <QGuiApplication>
#include <QLabel>
#include <QPixmap>
#include <QScreen>
#include <QVBoxLayout>

SplashScreen::SplashScreen(const QString &imagePath, QWidget *parent) : QWidget(parent) {
    setWindowFlags(
        Qt::FramelessWindowHint | Qt::WindowStaysOnTopHint | Qt::SplashScreen | Qt::WindowTransparentForInput
    );
    setAttribute(Qt::WA_TranslucentBackground);

    QPixmap pixmap(imagePath);
    auto *label = new QLabel(this);
    label->setPixmap(pixmap);
    label->setAlignment(Qt::AlignCenter);

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->addWidget(label);

    if (!pixmap.isNull()) {
        setFixedSize(pixmap.size());
        const QRect screen = QGuiApplication::primaryScreen()->geometry();
        move(screen.center() - rect().center());
    }
}
