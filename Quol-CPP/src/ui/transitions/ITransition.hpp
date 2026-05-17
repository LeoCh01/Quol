#pragma once

#include <QPoint>
#include <QString>

class QWidget;
class QAbstractAnimation;

/// Abstract interface for show/hide transition effects on a QWidget window.
///
/// Built-in transitions are registered automatically by TransitionManager.
/// To add a new transition as a DLL, implement this class and export a factory:
///
///   extern "C" Q_DECL_EXPORT ITransition* createTransition() {
///       return new MyTransition();
///   }
///
/// Place the DLL in the "transitions/" folder next to Quol.exe.
class ITransition {
public:
    virtual ~ITransition() = default;

    /// Unique name used to identify this transition (e.g. "fade", "slide-left").
    virtual QString name() const = 0;

    /// Creates an animation that moves w toward off-screen (hide direction).
    /// Returns nullptr to hide instantly.
    ///
    /// The caller (TransitionManager) will call w->hide() and reset windowOpacity
    /// after the animation finishes, so the transition must NOT do those itself.
    virtual QAbstractAnimation *createHideAnimation(QWidget *w, const QPoint &savedPos) const = 0;

    /// Creates an animation that brings w back to savedPos (show direction).
    /// The implementation MUST call w->show() and set up initial state (e.g. opacity=0)
    /// before returning the animation object.
    /// Returns nullptr to show instantly (implementation must also call w->show()).
    virtual QAbstractAnimation *createShowAnimation(QWidget *w, const QPoint &savedPos) const = 0;
};

/// DLL factory function signature.
/// Each transition DLL must export this symbol.
using CreateTransitionFn = ITransition *(*) ();
