#pragma once

#include <QObject>
#include <QList>
#include <QPoint>
#include <QHash>

class QWidget;
class QAbstractAnimation;
class QParallelAnimationGroup;

class TransitionManager : public QObject
{
    Q_OBJECT

public:
    explicit TransitionManager(const QString &type, QObject *parent = nullptr);

    void addWindow(QWidget *window);
    void toggleAll();
    bool isHidden() const;

private:
    void hideAll();
    void showAll();

    void fadeHide(QWidget *w);
    void fadeShow(QWidget *w);
    void randHide(QWidget *w, const QPoint &target);
    void randShow(QWidget *w, const QPoint &savedPos);

    QPoint randomTarget(QWidget *w) const;
    void trackAnimation(QWidget *w, QAbstractAnimation *animation);
    void stopAnimation(QWidget *w);

    QString m_type;
    QList<QWidget *> m_windows;
    QList<QPoint> m_savedPositions;
    QHash<QWidget *, QAbstractAnimation *> m_activeAnimations;
    bool m_hidden = false;
};
