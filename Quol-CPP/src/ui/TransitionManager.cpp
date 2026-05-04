#include "ui/TransitionManager.hpp"

#include <QAbstractAnimation>
#include <QGuiApplication>
#include <QParallelAnimationGroup>
#include <QPropertyAnimation>
#include <QRandomGenerator>
#include <QScreen>
#include <QWidget>

TransitionManager::TransitionManager(const QString &type, QObject *parent) : QObject(parent), m_type(type.toLower()) {
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
        QWidget *w = m_windows[i];
        if (!m_activeAnimations.contains(w) && w->isVisible())
            m_savedPositions[i] = w->pos();
    }

    for (QWidget *w : m_windows) {
        if (m_type == "rand" || m_type == "random")
            randHide(w, randomTarget(w));
        else if (m_type == "fade")
            fadeHide(w);
        else
            w->hide();
    }
}

void TransitionManager::showAll() {
    for (int i = 0; i < m_windows.size(); ++i) {
        QWidget *w = m_windows[i];
        if (m_type == "rand" || m_type == "random")
            randShow(w, m_savedPositions[i]);
        else if (m_type == "fade")
            fadeShow(w);
        else
            w->show();
    }
}

void TransitionManager::fadeHide(QWidget *w) {
    stopAnimation(w);

    auto *anim = new QPropertyAnimation(w, "windowOpacity", this);
    anim->setDuration(200);
    anim->setStartValue(1.0);
    anim->setEndValue(0.0);
    trackAnimation(w, anim);
    connect(anim, &QPropertyAnimation::finished, w, [this, w, anim]() {
        if (m_activeAnimations.value(w) != anim)
            return;

        m_activeAnimations.remove(w);
        w->hide();
        w->setWindowOpacity(1.0);
        anim->deleteLater();
    });
    anim->start();
}

void TransitionManager::fadeShow(QWidget *w) {
    stopAnimation(w);

    w->setWindowOpacity(0.0);
    w->show();

    auto *anim = new QPropertyAnimation(w, "windowOpacity", this);
    anim->setDuration(200);
    anim->setStartValue(0.0);
    anim->setEndValue(1.0);
    trackAnimation(w, anim);
    connect(anim, &QPropertyAnimation::finished, w, [this, w, anim]() {
        if (m_activeAnimations.value(w) != anim)
            return;

        m_activeAnimations.remove(w);
        anim->deleteLater();
    });
    anim->start();
}

void TransitionManager::randHide(QWidget *w, const QPoint &target) {
    stopAnimation(w);

    auto *posAnim = new QPropertyAnimation(w, "pos", this);
    posAnim->setDuration(200);
    posAnim->setStartValue(w->pos());
    posAnim->setEndValue(target);

    auto *opAnim = new QPropertyAnimation(w, "windowOpacity", this);
    opAnim->setDuration(200);
    opAnim->setStartValue(1.0);
    opAnim->setEndValue(0.0);

    auto *group = new QParallelAnimationGroup(this);
    group->addAnimation(posAnim);
    group->addAnimation(opAnim);
    trackAnimation(w, group);
    connect(group, &QParallelAnimationGroup::finished, w, [this, w, group]() {
        if (m_activeAnimations.value(w) != group)
            return;

        m_activeAnimations.remove(w);
        w->hide();
        w->setWindowOpacity(1.0);
        group->deleteLater();
    });
    group->start();
}

void TransitionManager::randShow(QWidget *w, const QPoint &savedPos) {
    stopAnimation(w);

    w->setWindowOpacity(0.0);
    w->show();

    auto *posAnim = new QPropertyAnimation(w, "pos", this);
    posAnim->setDuration(200);
    posAnim->setStartValue(w->pos());
    posAnim->setEndValue(savedPos);

    auto *opAnim = new QPropertyAnimation(w, "windowOpacity", this);
    opAnim->setDuration(200);
    opAnim->setStartValue(0.0);
    opAnim->setEndValue(1.0);

    auto *group = new QParallelAnimationGroup(this);
    group->addAnimation(posAnim);
    group->addAnimation(opAnim);
    trackAnimation(w, group);
    connect(group, &QParallelAnimationGroup::finished, w, [this, w, group]() {
        if (m_activeAnimations.value(w) != group)
            return;

        m_activeAnimations.remove(w);
        group->deleteLater();
    });
    group->start();
}

QPoint TransitionManager::randomTarget(QWidget *w) const {
    QScreen *screen = QGuiApplication::primaryScreen();
    const QRect screenRect = screen ? screen->availableGeometry() : QRect(0, 0, 1920, 1080);

    switch (QRandomGenerator::global()->bounded(4)) {
        case 0:
            return {screenRect.left() - w->width() - 30, w->y()};
        case 1:
            return {screenRect.right() + 31, w->y()};
        case 2:
            return {w->x(), screenRect.top() - w->height() - 30};
        default:
            return {w->x(), screenRect.bottom() + 31};
    }
}

void TransitionManager::trackAnimation(QWidget *w, QAbstractAnimation *animation) {
    m_activeAnimations.insert(w, animation);
}

void TransitionManager::stopAnimation(QWidget *w) {
    if (!m_activeAnimations.contains(w))
        return;

    QAbstractAnimation *animation = m_activeAnimations.take(w);
    if (!animation)
        return;

    animation->stop();
    animation->deleteLater();
}
