#pragma once

#include "ui/transitions/ITransition.hpp"

#include <QWidget>

/// Instant show/hide with no animation.
class NoneTransition final : public ITransition {
public:
    QString name() const override {
        return QStringLiteral("none");
    }

    QAbstractAnimation *createHideAnimation(QWidget *, const QPoint &) const override {
        return nullptr;  // caller will call w->hide() immediately
    }

    QAbstractAnimation *createShowAnimation(QWidget *w, const QPoint &savedPos) const override {
        w->move(savedPos);
        w->show();
        return nullptr;
    }
};
