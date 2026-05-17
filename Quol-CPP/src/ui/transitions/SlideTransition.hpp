#pragma once

#include "ui/transitions/ITransition.hpp"

#include <QGuiApplication>
#include <QPropertyAnimation>
#include <QScreen>
#include <QWidget>

enum class SlideDirection { Left, Right, Up, Down };

/// Slides the window off/onto the screen in the given direction.
///
/// On hide: window slides from its current position toward the screen edge.
/// On show: window slides from the off-screen edge back to savedPos.
class SlideTransition final : public ITransition {
public:
    explicit SlideTransition(SlideDirection dir, int durationMs = 200) : m_dir(dir), m_duration(durationMs) {
    }

    QString name() const override {
        switch (m_dir) {
            case SlideDirection::Left:
                return QStringLiteral("slide-left");
            case SlideDirection::Right:
                return QStringLiteral("slide-right");
            case SlideDirection::Up:
                return QStringLiteral("slide-up");
            default:
                return QStringLiteral("slide-down");
        }
    }

    QAbstractAnimation *createHideAnimation(QWidget *w, const QPoint &savedPos) const override {
        auto *anim = new QPropertyAnimation(w, "pos");
        anim->setDuration(m_duration);
        anim->setStartValue(w->pos());
        anim->setEndValue(offScreenPos(w, savedPos));
        return anim;
    }

    QAbstractAnimation *createShowAnimation(QWidget *w, const QPoint &savedPos) const override {
        // w is hidden, currently positioned at the off-screen target from the last hide
        w->show();
        auto *anim = new QPropertyAnimation(w, "pos");
        anim->setDuration(m_duration);
        anim->setStartValue(w->pos());  // current off-screen position
        anim->setEndValue(savedPos);
        return anim;
    }

private:
    QPoint offScreenPos(QWidget *w, const QPoint &from) const {
        QScreen *screen = QGuiApplication::primaryScreen();
        const QRect r = screen ? screen->availableGeometry() : QRect(0, 0, 1920, 1080);
        switch (m_dir) {
            case SlideDirection::Left:
                return {r.left() - w->width() - 30, from.y()};
            case SlideDirection::Right:
                return {r.right() + 31, from.y()};
            case SlideDirection::Up:
                return {from.x(), r.top() - w->height() - 30};
            default:
                return {from.x(), r.bottom() + 31};
        }
    }

    SlideDirection m_dir;
    int m_duration;
};
