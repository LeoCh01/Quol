#pragma once

#include <QWidget>

class SplashScreen : public QWidget {
public:
    explicit SplashScreen(const QString &imagePath, QWidget *parent = nullptr);
};
