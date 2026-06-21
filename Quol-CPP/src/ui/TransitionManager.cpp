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

TransitionManager::Type TransitionManager::parseType(const QString &type) {
    const QString n = type.trimmed().toLower();
    if (n.isEmpty() || n == QStringLiteral("none"))
        return Type::None;
    if (n == QStringLiteral("fade"))
        return Type::Fade;
    if (n == QStringLiteral("slide-left"))
        return Type::SlideLeft;
    if (n == QStringLiteral("slide-right"))
        return Type::SlideRight;
    if (n == QStringLiteral("slide-up"))
        return Type::SlideUp;
    if (n == QStringLiteral("slide-down"))
        return Type::SlideDown;
    if (n == QStringLiteral("rand-slide"))
        return Type::RandSlide;
    return Type::None;
}

int TransitionManager::randomSlideDir() {
    return QRandomGenerator::global()->bounded(4);
}

void TransitionManager::setType(const QString &type) {
    m_type = parseType(type);
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
        if (!m_activeAnimations.contains(m_windows[i]))
            m_savedPositions[i] = m_windows[i]->pos();
        doHide(m_windows[i], i);
    }
}

void TransitionManager::showAll() {
    for (int i = 0; i < m_windows.size(); ++i)
        doShow(m_windows[i], i);
}

QAbstractAnimation *TransitionManager::createSlideAnimation(QWidget *w, const QPoint &target, int dir, bool isHide) {
    if (isHide) {
        auto *posA = new QPropertyAnimation(w, "pos");
        posA->setDuration(200);
        posA->setStartValue(target);
        posA->setEndValue(offScreenPos(w, target, dir));
        auto *opA = new QPropertyAnimation(w, "windowOpacity");
        opA->setDuration(200);
        opA->setStartValue(1.0);
        opA->setEndValue(0.0);
        auto *grp = new QParallelAnimationGroup;
        grp->addAnimation(posA);
        grp->addAnimation(opA);
        QObject::connect(grp, &QAbstractAnimation::finished, w, [w, target]() {
            w->hide();
            w->move(target);
            w->setWindowOpacity(1.0);
        });
        return grp;
    }

    w->move(offScreenPos(w, target, dir));
    w->setWindowOpacity(0.0);
    w->show();
    auto *posA = new QPropertyAnimation(w, "pos");
    posA->setDuration(200);
    posA->setStartValue(w->pos());
    posA->setEndValue(target);
    auto *opA = new QPropertyAnimation(w, "windowOpacity");
    opA->setDuration(200);
    opA->setStartValue(0.0);
    opA->setEndValue(1.0);
    auto *grp = new QParallelAnimationGroup;
    grp->addAnimation(posA);
    grp->addAnimation(opA);
    return grp;
}

void TransitionManager::doHide(QWidget *w, int idx) {
    stopAnimation(w);

    Type type = m_type;
    int dir = 0;
    if (type == Type::RandSlide) {
        dir = randomSlideDir();
    }

    const QPoint from = m_savedPositions[idx];
    QAbstractAnimation *anim = nullptr;

    switch (type) {
        case Type::Fade: {
            auto *fade = new QPropertyAnimation(w, "windowOpacity");
            fade->setDuration(200);
            fade->setStartValue(1.0);
            fade->setEndValue(0.0);
            QObject::connect(fade, &QAbstractAnimation::finished, w, &QWidget::hide);
            anim = fade;
            break;
        }
        case Type::SlideLeft:
        case Type::SlideRight:
        case Type::SlideUp:
        case Type::SlideDown:
            anim = createSlideAnimation(w, from, static_cast<int>(type) - static_cast<int>(Type::SlideLeft), true);
            break;
        case Type::RandSlide:
            anim = createSlideAnimation(w, from, dir, true);
            break;
        default:
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

void TransitionManager::doShow(QWidget *w, int idx) {
    stopAnimation(w);

    Type type = m_type;
    int dir = 0;
    if (type == Type::RandSlide) {
        dir = randomSlideDir();
    }

    const QPoint saved = m_savedPositions[idx];
    QAbstractAnimation *anim = nullptr;

    switch (type) {
        case Type::Fade: {
            w->setWindowOpacity(0.0);
            w->move(saved);
            w->show();
            auto *fade = new QPropertyAnimation(w, "windowOpacity");
            fade->setDuration(200);
            fade->setStartValue(0.0);
            fade->setEndValue(1.0);
            anim = fade;
            break;
        }
        case Type::SlideLeft:
        case Type::SlideRight:
        case Type::SlideUp:
        case Type::SlideDown:
            anim = createSlideAnimation(w, saved, static_cast<int>(type) - static_cast<int>(Type::SlideLeft), false);
            break;
        case Type::RandSlide:
            anim = createSlideAnimation(w, saved, dir, false);
            break;
        default:
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