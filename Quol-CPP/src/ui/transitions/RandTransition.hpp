#pragma once

#include "ui/transitions/ITransition.hpp"

#include <QGuiApplication>
#include <QParallelAnimationGroup>
#include <QPropertyAnimation>
#include <QRandomGenerator>
#include <QScreen>
#include <QWidget>

/// Random-direction slide combined with a fade — matching the original "rand" behavior.
///
/// On hide: window slides to a random off-screen edge while fading out.
/// On show: window slides back from wherever it was while fading in.
class RandTransition final : public ITransition {
public:
    explicit RandTransition(int durationMs = 200) : m_duration(durationMs) {
    }

    QString name() const override {
        return QStringLiteral("rand");
    }

    QAbstractAnimation *createHideAnimation(QWidget *w, const QPoint &savedPos) const override {
        const QPoint target = randomOffScreenPos(w, savedPos);

        auto *posAnim = new QPropertyAnimation(w, "pos");
        posAnim->setDuration(m_duration);
        posAnim->setStartValue(w->pos());
        posAnim->setEndValue(target);

        auto *opAnim = new QPropertyAnimation(w, "windowOpacity");
        opAnim->setDuration(m_duration);
        opAnim->setStartValue(1.0);
        opAnim->setEndValue(0.0);

        auto *group = new QParallelAnimationGroup;
        group->addAnimation(posAnim);
        group->addAnimation(opAnim);
        return group;
    }

    QAbstractAnimation *createShowAnimation(QWidget *w, const QPoint &savedPos) const override {
        // w is hidden at the random off-screen position from the last hide
        w->setWindowOpacity(0.0);
        w->show();

        auto *posAnim = new QPropertyAnimation(w, "pos");
        posAnim->setDuration(m_duration);
        posAnim->setStartValue(w->pos());
        posAnim->setEndValue(savedPos);

        auto *opAnim = new QPropertyAnimation(w, "windowOpacity");
        opAnim->setDuration(m_duration);
        opAnim->setStartValue(0.0);
        opAnim->setEndValue(1.0);

        auto *group = new QParallelAnimationGroup;
        group->addAnimation(posAnim);
        group->addAnimation(opAnim);
        return group;
    }

private:
    QPoint randomOffScreenPos(QWidget *w, const QPoint &from) const {
        QScreen *screen = QGuiApplication::primaryScreen();
        const QRect r = screen ? screen->availableGeometry() : QRect(0, 0, 1920, 1080);
        switch (QRandomGenerator::global()->bounded(4)) {
            case 0:
                return {r.left() - w->width() - 30, from.y()};
            case 1:
                return {r.right() + 31, from.y()};
            case 2:
                return {from.x(), r.top() - w->height() - 30};
            default:
                return {from.x(), r.bottom() + 31};
        }
    }

    int m_duration;
};
