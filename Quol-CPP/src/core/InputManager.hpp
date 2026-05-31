#pragma once

#include <QAbstractNativeEventFilter>
#include <QHash>
#include <QList>
#include <QObject>
#include <QPoint>
#include <QString>
#include <QStringList>
#include <functional>

// InputManager is a singleton-style service owned by main() and shared with
// all plugins via QuolServices. It manages:
//   - Global hotkeys (Win32 RegisterHotKey)
//   - Low-level keyboard event listeners (WH_KEYBOARD_LL)
//   - Low-level mouse event listeners  (WH_MOUSE_LL)
//
// All add* methods return a handle ID that must be passed to the matching
// remove* method when the listener is no longer needed. An empty QString
// means registration failed.
class InputManager : public QObject, public QAbstractNativeEventFilter {
    Q_OBJECT

public:
    // Describes a single mouse event delivered to mouse listeners.
    struct MouseEvent {
        enum class Type {
            Move,
            LeftDown,
            LeftUp,
            RightDown,
            RightUp,
            MiddleDown,
            MiddleUp,
            WheelUp,
            WheelDown,
        };
        Type type = Type::Move;
        QPoint globalPos;
        int wheelDelta = 0;  // non-zero for WheelUp / WheelDown
    };

signals:
    // Emitted for every mouse event received by the low-level hook.
    // Connect with Qt::QueuedConnection to safely update UI from the hook callback.
    void mouseEventReceived(InputManager::MouseEvent event);

public:
    explicit InputManager(QObject *parent = nullptr);
    ~InputManager() override;

    void start();
    void stop();

    // --- Hotkeys ---
    // Registers a global hotkey for the given combo string (e.g. "ctrl+shift+a").
    // callback is invoked on the main thread each time the hotkey fires.
    // suppressed = true prevents the keystroke from reaching other applications.
    // Returns a handle ID, or an empty QString on failure.
    QString addHotkey(const QString &combo, std::function<void()> callback, bool suppressed = false);
    void removeHotkey(const QString &id);

    // --- Key listeners ---
    // callback(key, isPressed) is fired for every key event from the low-level hook.
    // Returns a handle ID.
    QString addKeyListener(std::function<void(const QString &key, bool pressed)> callback);
    void removeKeyListener(const QString &id);

    // --- Key remaps ---
    // Remaps a single key (or combo) to another at the low-level hook, suppressing
    // the source and injecting the destination.  Works for plain keys (no modifier
    // required), unlike RegisterHotKey-based hotkeys.  Injection is marked with
    // m_sendEvent so it does NOT re-trigger other remaps (no chaining).
    // Returns a handle ID, or empty on failure (unknown key name).
    QString addKeyRemap(const QString &srcKey, const QString &dstCombo);
    void removeKeyRemap(const QString &id);

    // --- Mouse listeners ---
    // callback(event) is fired for every mouse event from the low-level hook.
    // Returns a handle ID.
    QString addMouseListener(std::function<void(const MouseEvent &)> callback);
    void removeMouseListener(const QString &id);

    // --- Key injection ---
    void sendKeys(const QString &combo);
    void sendPress(const QString &combo);
    void sendRelease(const QString &combo);

    QStringList availableKeys() const;

    // Called by the global hook callbacks (public for hook proc access).
    bool handleKeyEvent(unsigned long wParam, quint32 vkCode, bool injected);
    void handleMouseEvent(unsigned long wParam, long x, long y, int wheelDelta);

    bool nativeEventFilter(const QByteArray &eventType, void *message, qintptr *result) override;

private:
    QString nextId();

    bool parseHotkey(
        const QString &combo,
        quint32 &registerModifiers,
        quint32 &vk,
        quint32 &requiredModifiers,
        QList<quint32> &requiredKeys
    ) const;

    struct HotkeyEntry {
        int nativeId = 0;
        QString combo;
        quint32 registerModifiers = 0;
        quint32 vk = 0;
        quint32 requiredModifiers = 0;
        QList<quint32> requiredKeys;
        bool suppressed = false;
        std::function<void()> callback;
    };

    struct KeyListenerEntry {
        std::function<void(const QString &, bool)> callback;
    };

    struct KeyRemapEntry {
        quint32 srcVk = 0;
        QString dstCombo;
    };

    struct MouseListenerEntry {
        std::function<void(const MouseEvent &)> callback;
    };

    int m_idCounter = 0;
    bool m_running = false;

    QHash<QString, HotkeyEntry> m_hotkeys;
    QHash<QString, KeyListenerEntry> m_keyListeners;
    QHash<QString, KeyRemapEntry> m_keyRemaps;
    QHash<QString, MouseListenerEntry> m_mouseListeners;

#ifdef Q_OS_WIN
    void *m_keyboardHook = nullptr;
    void *m_mouseHook = nullptr;
#endif
};
