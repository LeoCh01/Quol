#pragma once

#include <QString>

class QVBoxLayout;
class TitleBar;
class QWidget;

void quolInitBaseLayout(QWidget *widget, const QString &title, TitleBar *&titleBarOut, QVBoxLayout *&bodyLayoutOut);