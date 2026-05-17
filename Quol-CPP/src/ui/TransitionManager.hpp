#pragma once

#include <QHash>
#include <QList>
#include <QObject>
#include <QPoint>

class QWidget;
class QAbstractAnimation;

/// Manages show/hide transitions for a set of tracked windows.
///
/// Supported types: "none", "fade", "slide-left", "slide-right",
///                  "slide-up", "slide-down", "rand"
class TransitionManager : public QObject {
    Q_OBJECT

public:
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
    void trackAnimation(QWidget *w, QAbstractAnimation *anim);
    void stopAnimation(QWidget *w);

    QString m_type;
    QList<QWidget *> m_windows;
    QList<QPoint> m_savedPositions;
    QHash<QWidget *, QAbstractAnimation *> m_activeAnimations;
    bool m_hidden = false;
};
