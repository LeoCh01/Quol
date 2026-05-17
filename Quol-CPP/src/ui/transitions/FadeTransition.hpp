#pragma once

#include "ui/transitions/ITransition.hpp"

#include <QPropertyAnimation>
#include <QWidget>

/// Fade in/out by animating windowOpacity.
class FadeTransition final : public ITransition {
public:
    explicit FadeTransition(int durationMs = 200) : m_duration(durationMs) {
    }

    QString name() const override {
        return QStringLiteral("fade");
    }

    QAbstractAnimation *createHideAnimation(QWidget *w, const QPoint &) const override {
        auto *anim = new QPropertyAnimation(w, "windowOpacity");
        anim->setDuration(m_duration);
        anim->setStartValue(1.0);
        anim->setEndValue(0.0);
        return anim;
    }

    QAbstractAnimation *createShowAnimation(QWidget *w, const QPoint &savedPos) const override {
        w->move(savedPos);
        w->setWindowOpacity(0.0);
        w->show();
        auto *anim = new QPropertyAnimation(w, "windowOpacity");
        anim->setDuration(m_duration);
        anim->setStartValue(0.0);
        anim->setEndValue(1.0);
        return anim;
    }

private:
    int m_duration;
};
