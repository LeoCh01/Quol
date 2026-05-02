#include "ui/TransitionManager.hpp"

#include <QGuiApplication>
#include <QParallelAnimationGroup>
#include <QPropertyAnimation>
#include <QRandomGenerator>
#include <QScreen>
#include <QWidget>

TransitionManager::TransitionManager(const QString& type, QObject* parent)
    : QObject(parent)
    , m_type(type.toLower())
{
}

void TransitionManager::addWindow(QWidget* window)
{
    m_windows.append(window);
    m_savedPositions.append(window->pos());
}

bool TransitionManager::isHidden() const
{
    return m_hidden;
}

void TransitionManager::toggleAll()
{
    if (!m_hidden)
    {
        hideAll();
        m_hidden = true;
    }
    else
    {
        showAll();
        m_hidden = false;
    }
}

void TransitionManager::hideAll()
{
    for (int i = 0; i < m_windows.size(); ++i)
        m_savedPositions[i] = m_windows[i]->pos();

    for (QWidget* w : m_windows)
    {
        if (m_type == "rand" || m_type == "random")
            randHide(w, randomTarget(w));
        else if (m_type == "fade")
            fadeHide(w);
        else
            w->hide();
    }
}

void TransitionManager::showAll()
{
    for (int i = 0; i < m_windows.size(); ++i)
    {
        QWidget* w = m_windows[i];
        if (m_type == "rand" || m_type == "random")
            randShow(w, m_savedPositions[i]);
        else if (m_type == "fade")
            fadeShow(w);
        else
            w->show();
    }
}

void TransitionManager::fadeHide(QWidget* w)
{
    auto* anim = new QPropertyAnimation(w, "windowOpacity", this);
    anim->setDuration(200);
    anim->setStartValue(1.0);
    anim->setEndValue(0.0);
    connect(anim, &QPropertyAnimation::finished, w, [w]() {
        w->hide();
        w->setWindowOpacity(1.0);
    });
    anim->start(QAbstractAnimation::DeleteWhenStopped);
}

void TransitionManager::fadeShow(QWidget* w)
{
    w->setWindowOpacity(0.0);
    w->show();
    auto* anim = new QPropertyAnimation(w, "windowOpacity", this);
    anim->setDuration(200);
    anim->setStartValue(0.0);
    anim->setEndValue(1.0);
    anim->start(QAbstractAnimation::DeleteWhenStopped);
}

void TransitionManager::randHide(QWidget* w, const QPoint& target)
{
    auto* posAnim = new QPropertyAnimation(w, "pos", this);
    posAnim->setDuration(200);
    posAnim->setStartValue(w->pos());
    posAnim->setEndValue(target);

    auto* opAnim = new QPropertyAnimation(w, "windowOpacity", this);
    opAnim->setDuration(200);
    opAnim->setStartValue(1.0);
    opAnim->setEndValue(0.0);

    auto* group = new QParallelAnimationGroup(this);
    group->addAnimation(posAnim);
    group->addAnimation(opAnim);
    connect(group, &QParallelAnimationGroup::finished, w, [w]() {
        w->hide();
        w->setWindowOpacity(1.0);
    });
    group->start(QAbstractAnimation::DeleteWhenStopped);
}

void TransitionManager::randShow(QWidget* w, const QPoint& savedPos)
{
    w->setWindowOpacity(0.0);
    w->show();

    auto* posAnim = new QPropertyAnimation(w, "pos", this);
    posAnim->setDuration(200);
    posAnim->setStartValue(w->pos());
    posAnim->setEndValue(savedPos);

    auto* opAnim = new QPropertyAnimation(w, "windowOpacity", this);
    opAnim->setDuration(200);
    opAnim->setStartValue(0.0);
    opAnim->setEndValue(1.0);

    auto* group = new QParallelAnimationGroup(this);
    group->addAnimation(posAnim);
    group->addAnimation(opAnim);
    group->start(QAbstractAnimation::DeleteWhenStopped);
}

QPoint TransitionManager::randomTarget(QWidget* w) const
{
    QScreen* screen = QGuiApplication::primaryScreen();
    const QRect screenRect = screen ? screen->geometry() : QRect(0, 0, 1920, 1080);

    switch (QRandomGenerator::global()->bounded(4))
    {
    case 0: return {-w->width() - 30, w->y()};
    case 1: return {screenRect.width() + 30, w->y()};
    case 2: return {w->x(), -w->height() - 30};
    default: return {w->x(), screenRect.height() + 30};
    }
}
