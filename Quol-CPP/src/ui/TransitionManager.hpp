#pragma once

#include <QHash>
#include <QList>
#include <QObject>
#include <QPoint>

class QWidget;
class QAbstractAnimation;
class QLibrary;
class ITransition;

/// Manages show/hide transitions for a set of tracked windows.
///
/// Built-in transitions (registered automatically):
///   "none"        — instant
///   "fade"        — opacity fade
///   "slide-left"  — slide toward left edge
///   "slide-right" — slide toward right edge
///   "slide-up"    — slide toward top edge
///   "slide-down"  — slide toward bottom edge
///   "rand"        — random direction + fade (original behavior)
///
/// Custom transitions can be loaded from DLLs placed next to Quol.exe in a
/// "transitions/" subdirectory. Each DLL must export:
///
///   extern "C" Q_DECL_EXPORT ITransition* createTransition();
///
/// The DLL will be found automatically when setType() is called with its name.
class TransitionManager : public QObject {
    Q_OBJECT

public:
    explicit TransitionManager(const QString &type, QObject *parent = nullptr);
    ~TransitionManager() override;

    void addWindow(QWidget *window);
    void toggleAll();
    bool isHidden() const;
    void setType(const QString &type);

    /// Override the directory searched for transition DLLs.
    /// Default: "<exeDir>/transitions/"
    void setSearchPath(const QString &path);

    /// Names of all currently registered transitions (built-ins + any loaded DLLs).
    QStringList registeredNames() const;

private:
    void hideAll();
    void showAll();
    void doHide(QWidget *w, int idx, ITransition *t);
    void doShow(QWidget *w, int idx, ITransition *t);
    void trackAnimation(QWidget *w, QAbstractAnimation *anim);
    void stopAnimation(QWidget *w);
    ITransition *resolve(const QString &type);
    void registerBuiltins();
    ITransition *tryLoadDll(const QString &name);

    QString m_type;
    QList<QWidget *> m_windows;
    QList<QPoint> m_savedPositions;
    QHash<QWidget *, QAbstractAnimation *> m_activeAnimations;
    bool m_hidden = false;

    QString m_searchPath;
    QHash<QString, ITransition *> m_registry;
    QList<ITransition *> m_ownedTransitions;  // owns built-ins and DLL-created instances
    QList<QLibrary *> m_libraries;
};
