#include "ui/TransitionManager.hpp"

#include <QAbstractAnimation>
#include <QGuiApplication>
#include <QParallelAnimationGroup>
#include <QPropertyAnimation>
#include <QRandomGenerator>
#include <QScreen>
#include <QWidget>

// -- helpers
// -------------------------------------------------------------------------
static QPoint offScreenPos(QWidget *w, const QPoint &from, int dir) {
    // dir: 0=left 1=right 2=up 3=down
    QScreen *screen = QGuiApplication::primaryScreen();
    const QRect r = screen ? screen->availableGeometry() : QRect(0, 0, 1920, 1080);
    switch (dir) {
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

// -- TransitionManager
// -------------------------------------------------------------------------
TransitionManager::TransitionManager(const QString &type, QObject *parent) : QObject(parent) {
    setType(type);
}

TransitionManager::~TransitionManager() = default;

void TransitionManager::setType(const QString &type) {
    const QString n = type.trimmed().toLower();
    m_type = n.isEmpty() ? QStringLiteral("none") : n;
}

void TransitionManager::addWindow(QWidget *window) {
    m_windows.append(window);
    m_savedPositions.append(window->pos());
}

bool TransitionManager::isHidden() const {
    return m_hidden;
}

void TransitionManager::toggleAll() {
    if (!m_hidden) {
        hideAll();
        m_hidden = true;
    } else {
        showAll();
        m_hidden = false;
    }
}

void TransitionManager::hideAll() {
    for (int i = 0; i < m_windows.size(); ++i) {
        // Only update saved position when the window is not mid-animation
        // (during a slide the window is at an offscreen/intermediate position)
        if (!m_activeAnimations.contains(m_windows[i]))
            m_savedPositions[i] = m_windows[i]->pos();
        doHide(m_windows[i], i);
    }
}

void TransitionManager::showAll() {
    for (int i = 0; i < m_windows.size(); ++i)
        doShow(m_windows[i], i);
}

// -- doHide
// -------------------------------------------------------------------------
void TransitionManager::doHide(QWidget *w, int idx) {
    stopAnimation(w);

    QString type = m_type;
    if (type == QLatin1String("rand-slide")) {
        static const char *const kRandTypes[] = {"slide-left", "slide-right", "slide-up", "slide-down"};
        type = QLatin1String(kRandTypes[QRandomGenerator::global()->bounded(4)]);
    }

    const QPoint from = m_savedPositions[idx];
    QAbstractAnimation *anim = nullptr;

    if (type == QLatin1String("fade")) {
        w->setWindowOpacity(1.0);
        auto *a = new QPropertyAnimation(w, "windowOpacity");
        a->setDuration(200);
        a->setStartValue(1.0);
        a->setEndValue(0.0);
        QObject::connect(a, &QAbstractAnimation::finished, w, &QWidget::hide);
        anim = a;
    } else if (type == QLatin1String("slide-left")) {
        auto *posA = new QPropertyAnimation(w, "pos");
        posA->setDuration(200);
        posA->setStartValue(from);
        posA->setEndValue(offScreenPos(w, from, 0));
        auto *opA = new QPropertyAnimation(w, "windowOpacity");
        opA->setDuration(200);
        opA->setStartValue(1.0);
        opA->setEndValue(0.0);
        auto *grp = new QParallelAnimationGroup;
        grp->addAnimation(posA);
        grp->addAnimation(opA);
        QObject::connect(grp, &QAbstractAnimation::finished, w, [w, from]() {
            w->hide();
            w->move(from);
            w->setWindowOpacity(1.0);
        });
        anim = grp;
    } else if (type == QLatin1String("slide-right")) {
        auto *posA = new QPropertyAnimation(w, "pos");
        posA->setDuration(200);
        posA->setStartValue(from);
        posA->setEndValue(offScreenPos(w, from, 1));
        auto *opA = new QPropertyAnimation(w, "windowOpacity");
        opA->setDuration(200);
        opA->setStartValue(1.0);
        opA->setEndValue(0.0);
        auto *grp = new QParallelAnimationGroup;
        grp->addAnimation(posA);
        grp->addAnimation(opA);
        QObject::connect(grp, &QAbstractAnimation::finished, w, [w, from]() {
            w->hide();
            w->move(from);
            w->setWindowOpacity(1.0);
        });
        anim = grp;
    } else if (type == QLatin1String("slide-up")) {
        auto *posA = new QPropertyAnimation(w, "pos");
        posA->setDuration(200);
        posA->setStartValue(from);
        posA->setEndValue(offScreenPos(w, from, 2));
        auto *opA = new QPropertyAnimation(w, "windowOpacity");
        opA->setDuration(200);
        opA->setStartValue(1.0);
        opA->setEndValue(0.0);
        auto *grp = new QParallelAnimationGroup;
        grp->addAnimation(posA);
        grp->addAnimation(opA);
        QObject::connect(grp, &QAbstractAnimation::finished, w, [w, from]() {
            w->hide();
            w->move(from);
            w->setWindowOpacity(1.0);
        });
        anim = grp;
    } else if (type == QLatin1String("slide-down")) {
        auto *posA = new QPropertyAnimation(w, "pos");
        posA->setDuration(200);
        posA->setStartValue(from);
        posA->setEndValue(offScreenPos(w, from, 3));
        auto *opA = new QPropertyAnimation(w, "windowOpacity");
        opA->setDuration(200);
        opA->setStartValue(1.0);
        opA->setEndValue(0.0);
        auto *grp = new QParallelAnimationGroup;
        grp->addAnimation(posA);
        grp->addAnimation(opA);
        QObject::connect(grp, &QAbstractAnimation::finished, w, [w, from]() {
            w->hide();
            w->move(from);
            w->setWindowOpacity(1.0);
        });
        anim = grp;
    } else {
        w->hide();
        return;
    }

    trackAnimation(w, anim);
    QObject::connect(anim, &QAbstractAnimation::finished, this, [this, w, anim]() {
        if (m_activeAnimations.value(w) != anim)
            return;
        m_activeAnimations.remove(w);
        anim->deleteLater();
    });
    anim->start();
}

// -- doShow
// -------------------------------------------------------------------------
void TransitionManager::doShow(QWidget *w, int idx) {
    stopAnimation(w);

    QString type = m_type;
    if (type == QLatin1String("rand-slide")) {
        static const char *const kRandTypes[] = {"slide-left", "slide-right", "slide-up", "slide-down"};
        type = QLatin1String(kRandTypes[QRandomGenerator::global()->bounded(4)]);
    }

    const QPoint saved = m_savedPositions[idx];
    QAbstractAnimation *anim = nullptr;

    if (type == QLatin1String("fade")) {
        w->setWindowOpacity(0.0);
        w->move(saved);
        w->show();
        auto *a = new QPropertyAnimation(w, "windowOpacity");
        a->setDuration(200);
        a->setStartValue(0.0);
        a->setEndValue(1.0);
        anim = a;
    } else if (type == QLatin1String("slide-left")) {
        w->move(offScreenPos(w, saved, 0));
        w->setWindowOpacity(0.0);
        w->show();
        auto *posA = new QPropertyAnimation(w, "pos");
        posA->setDuration(200);
        posA->setStartValue(w->pos());
        posA->setEndValue(saved);
        auto *opA = new QPropertyAnimation(w, "windowOpacity");
        opA->setDuration(200);
        opA->setStartValue(0.0);
        opA->setEndValue(1.0);
        auto *grp = new QParallelAnimationGroup;
        grp->addAnimation(posA);
        grp->addAnimation(opA);
        anim = grp;
    } else if (type == QLatin1String("slide-right")) {
        w->move(offScreenPos(w, saved, 1));
        w->setWindowOpacity(0.0);
        w->show();
        auto *posA = new QPropertyAnimation(w, "pos");
        posA->setDuration(200);
        posA->setStartValue(w->pos());
        posA->setEndValue(saved);
        auto *opA = new QPropertyAnimation(w, "windowOpacity");
        opA->setDuration(200);
        opA->setStartValue(0.0);
        opA->setEndValue(1.0);
        auto *grp = new QParallelAnimationGroup;
        grp->addAnimation(posA);
        grp->addAnimation(opA);
        anim = grp;
    } else if (type == QLatin1String("slide-up")) {
        w->move(offScreenPos(w, saved, 2));
        w->setWindowOpacity(0.0);
        w->show();
        auto *posA = new QPropertyAnimation(w, "pos");
        posA->setDuration(200);
        posA->setStartValue(w->pos());
        posA->setEndValue(saved);
        auto *opA = new QPropertyAnimation(w, "windowOpacity");
        opA->setDuration(200);
        opA->setStartValue(0.0);
        opA->setEndValue(1.0);
        auto *grp = new QParallelAnimationGroup;
        grp->addAnimation(posA);
        grp->addAnimation(opA);
        anim = grp;
    } else if (type == QLatin1String("slide-down")) {
        w->move(offScreenPos(w, saved, 3));
        w->setWindowOpacity(0.0);
        w->show();
        auto *posA = new QPropertyAnimation(w, "pos");
        posA->setDuration(200);
        posA->setStartValue(w->pos());
        posA->setEndValue(saved);
        auto *opA = new QPropertyAnimation(w, "windowOpacity");
        opA->setDuration(200);
        opA->setStartValue(0.0);
        opA->setEndValue(1.0);
        auto *grp = new QParallelAnimationGroup;
        grp->addAnimation(posA);
        grp->addAnimation(opA);
        anim = grp;
    } else {
        w->move(saved);
        w->show();
        return;
    }

    trackAnimation(w, anim);
    QObject::connect(anim, &QAbstractAnimation::finished, this, [this, w, anim]() {
        if (m_activeAnimations.value(w) != anim)
            return;
        m_activeAnimations.remove(w);
        anim->deleteLater();
    });
    anim->start();
}

// -- internal helpers
// -------------------------------------------------------------------------
void TransitionManager::trackAnimation(QWidget *w, QAbstractAnimation *anim) {
    m_activeAnimations.insert(w, anim);
}

void TransitionManager::stopAnimation(QWidget *w) {
    QAbstractAnimation *anim = m_activeAnimations.take(w);
    if (!anim)
        return;
    anim->stop();
    anim->deleteLater();
    w->setWindowOpacity(1.0);
}