#pragma once

#include <QHash>
#include <QList>
#include <QObject>
#include <QPoint>

class QWidget;
class QAbstractAnimation;

/// Manages show/hide transitions for a set of tracked windows.
class TransitionManager : public QObject {
    Q_OBJECT

public:
    enum class Type { None, Fade, SlideLeft, SlideRight, SlideUp, SlideDown, RandSlide };

    explicit TransitionManager(const QString &type, QObject *parent = nullptr);
    ~TransitionManager() override;

    void addWindow(QWidget *window);
    void toggleAll();
    bool isHidden() const;
    void setType(const QString &type);

private:
    void hideAll();
    void showAll();
    void doHide(QWidget *w, int idx);
    void doShow(QWidget *w, int idx);
    QAbstractAnimation *createSlideAnimation(QWidget *w, const QPoint &target, int dir, bool isHide);
    void trackAnimation(QWidget *w, QAbstractAnimation *anim);
    void stopAnimation(QWidget *w);
    static Type parseType(const QString &type);
    static int randomSlideDir();

    Type m_type = Type::None;
    QList<QWidget *> m_windows;
    QList<QPoint> m_savedPositions;
    QHash<QWidget *, QAbstractAnimation *> m_activeAnimations;
    bool m_hidden = false;
};
