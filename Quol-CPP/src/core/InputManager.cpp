#include "core/InputManager.hpp"

#include <QCoreApplication>
#include <algorithm>

#ifdef Q_OS_WIN
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

namespace {
InputManager *g_inputManager = nullptr;

const QHash<QString, quint32> &modifierFlagMap() {
#ifdef Q_OS_WIN
    static const QHash<QString, quint32> map = {
        {QStringLiteral("ctrl"), MOD_CONTROL},
        {QStringLiteral("control"), MOD_CONTROL},
        {QStringLiteral("shift"), MOD_SHIFT},
        {QStringLiteral("alt"), MOD_ALT},
        {QStringLiteral("win"), MOD_WIN},
        {QStringLiteral("meta"), MOD_WIN}
    };
#else
    static const QHash<QString, quint32> map;
#endif
    return map;
}

const QHash<QString, quint32> &keyMap() {
#ifdef Q_OS_WIN
    static const QHash<QString, quint32> map = []() {
        QHash<QString, quint32> m = {
            {QStringLiteral("ctrl"), VK_CONTROL},
            {QStringLiteral("control"), VK_CONTROL},
            {QStringLiteral("shift"), VK_SHIFT},
            {QStringLiteral("alt"), VK_MENU},
            {QStringLiteral("win"), VK_LWIN},
            {QStringLiteral("meta"), VK_LWIN},

            {QStringLiteral("backtick"), VK_OEM_3},
            {QStringLiteral("grave"), VK_OEM_3},
            {QStringLiteral("tilde"), VK_OEM_3},
            {QStringLiteral("minus"), VK_OEM_MINUS},
            {QStringLiteral("dash"), VK_OEM_MINUS},
            {QStringLiteral("hyphen"), VK_OEM_MINUS},
            {QStringLiteral("equals"), VK_OEM_PLUS},
            {QStringLiteral("equal"), VK_OEM_PLUS},
            {QStringLiteral("plus"), VK_OEM_PLUS},
            {QStringLiteral("left_bracket"), VK_OEM_4},
            {QStringLiteral("right_bracket"), VK_OEM_6},
            {QStringLiteral("backslash"), VK_OEM_5},
            {QStringLiteral("semicolon"), VK_OEM_1},
            {QStringLiteral("quote"), VK_OEM_7},
            {QStringLiteral("apostrophe"), VK_OEM_7},
            {QStringLiteral("comma"), VK_OEM_COMMA},
            {QStringLiteral("period"), VK_OEM_PERIOD},
            {QStringLiteral("dot"), VK_OEM_PERIOD},
            {QStringLiteral("slash"), VK_OEM_2},
            {QStringLiteral("esc"), VK_ESCAPE},
            {QStringLiteral("escape"), VK_ESCAPE},
            {QStringLiteral("space"), VK_SPACE},
            {QStringLiteral("tab"), VK_TAB},
            {QStringLiteral("enter"), VK_RETURN},
            {QStringLiteral("return"), VK_RETURN},
            {QStringLiteral("left"), VK_LEFT},
            {QStringLiteral("right"), VK_RIGHT},
            {QStringLiteral("up"), VK_UP},
            {QStringLiteral("down"), VK_DOWN},
            {QStringLiteral("insert"), VK_INSERT},
            {QStringLiteral("delete"), VK_DELETE},
            {QStringLiteral("home"), VK_HOME},
            {QStringLiteral("end"), VK_END},
            {QStringLiteral("pageup"), VK_PRIOR},
            {QStringLiteral("pagedown"), VK_NEXT}
        };

        for (QChar ch = 'a'; ch <= 'z'; ch = QChar(ch.unicode() + 1)) {
            m.insert(QString(ch), static_cast<quint32>(ch.toUpper().unicode()));
        }

        for (QChar ch = '0'; ch <= '9'; ch = QChar(ch.unicode() + 1)) {
            m.insert(QString(ch), static_cast<quint32>(ch.unicode()));
        }

        for (int i = 1; i <= 24; ++i) {
            m.insert(QString("f%1").arg(i), static_cast<quint32>(VK_F1 + (i - 1)));
        }

        return m;
    }();
#else
    static const QHash<QString, quint32> map;
#endif
    return map;
}

bool tokenToVK(const QString &key, quint32 &vk, bool &isModifierToken) {
    isModifierToken = modifierFlagMap().contains(key);
    vk = keyMap().value(key, 0);
    return vk != 0;
}

QString VKToToken(quint32 vk) {
#ifdef Q_OS_WIN
    if (vk >= 'A' && vk <= 'Z') {
        return QString(QChar(static_cast<ushort>(vk))).toLower();
    }

    if (vk >= '0' && vk <= '9') {
        return QString(QChar(static_cast<ushort>(vk)));
    }

    if (vk >= VK_F1 && vk <= VK_F24) {
        return QString(QStringLiteral("f%1")).arg(static_cast<int>(vk - VK_F1 + 1));
    }

    static const QHash<quint32, QString> map = {
        {VK_BACK, QStringLiteral("backspace")},
        {VK_TAB, QStringLiteral("tab")},
        {VK_RETURN, QStringLiteral("enter")},
        {VK_PAUSE, QStringLiteral("pause")},
        {VK_CAPITAL, QStringLiteral("caps_lock")},
        {VK_ESCAPE, QStringLiteral("esc")},
        {VK_SPACE, QStringLiteral("space")},
        {VK_PRIOR, QStringLiteral("pageup")},
        {VK_NEXT, QStringLiteral("pagedown")},
        {VK_END, QStringLiteral("end")},
        {VK_HOME, QStringLiteral("home")},
        {VK_LEFT, QStringLiteral("left")},
        {VK_UP, QStringLiteral("up")},
        {VK_RIGHT, QStringLiteral("right")},
        {VK_DOWN, QStringLiteral("down")},
        {VK_SNAPSHOT, QStringLiteral("print_screen")},
        {VK_INSERT, QStringLiteral("insert")},
        {VK_DELETE, QStringLiteral("delete")},
        {VK_NUMPAD0, QStringLiteral("0")},
        {VK_NUMPAD1, QStringLiteral("1")},
        {VK_NUMPAD2, QStringLiteral("2")},
        {VK_NUMPAD3, QStringLiteral("3")},
        {VK_NUMPAD4, QStringLiteral("4")},
        {VK_NUMPAD5, QStringLiteral("5")},
        {VK_NUMPAD6, QStringLiteral("6")},
        {VK_NUMPAD7, QStringLiteral("7")},
        {VK_NUMPAD8, QStringLiteral("8")},
        {VK_NUMPAD9, QStringLiteral("9")},
        {VK_MULTIPLY, QStringLiteral("*")},
        {VK_ADD, QStringLiteral("+")},
        {VK_SUBTRACT, QStringLiteral("-")},
        {VK_DECIMAL, QStringLiteral(".")},
        {VK_DIVIDE, QStringLiteral("/")},
        {VK_OEM_1, QStringLiteral("semicolon")},
        {VK_OEM_PLUS, QStringLiteral("equals")},
        {VK_OEM_COMMA, QStringLiteral("comma")},
        {VK_OEM_MINUS, QStringLiteral("minus")},
        {VK_OEM_PERIOD, QStringLiteral("period")},
        {VK_OEM_2, QStringLiteral("slash")},
        {VK_OEM_3, QStringLiteral("backtick")},
        {VK_OEM_4, QStringLiteral("left_bracket")},
        {VK_OEM_5, QStringLiteral("backslash")},
        {VK_OEM_6, QStringLiteral("right_bracket")},
        {VK_OEM_7, QStringLiteral("quote")},
        {VK_SHIFT, QStringLiteral("shift")},
        {VK_LSHIFT, QStringLiteral("shift")},
        {VK_RSHIFT, QStringLiteral("shift_r")},
        {VK_CONTROL, QStringLiteral("ctrl")},
        {VK_LCONTROL, QStringLiteral("ctrl")},
        {VK_RCONTROL, QStringLiteral("ctrl_r")},
        {VK_MENU, QStringLiteral("alt")},
        {VK_LMENU, QStringLiteral("alt")},
        {VK_RMENU, QStringLiteral("alt_r")}
    };

    return map.value(vk);
#else
    Q_UNUSED(vk)
    return {};
#endif
}

QStringList splitCombo(const QString &combo) {
    const QStringList rawParts = combo.toLower().split('+', Qt::SkipEmptyParts);
    QStringList parts;
    for (const QString &token : rawParts) {
        const QString key = token.trimmed();
        if (!key.isEmpty()) {
            parts.append(key);
        }
    }
    return parts;
}

bool isModifierDown(quint32 modifier) {
#ifdef Q_OS_WIN
    if ((modifier & MOD_CONTROL) && !(GetAsyncKeyState(VK_CONTROL) & 0x8000))
        return false;

    if ((modifier & MOD_SHIFT) && !(GetAsyncKeyState(VK_SHIFT) & 0x8000))
        return false;

    if ((modifier & MOD_ALT) && !(GetAsyncKeyState(VK_MENU) & 0x8000))
        return false;

    if ((modifier & MOD_WIN) && !((GetAsyncKeyState(VK_LWIN) & 0x8000) || (GetAsyncKeyState(VK_RWIN) & 0x8000)))
        return false;

    return true;
#else
    Q_UNUSED(modifier)
    return false;
#endif
}

bool isVirtualKeyDown(quint32 vk) {
#ifdef Q_OS_WIN
    return (GetAsyncKeyState(static_cast<int>(vk)) & 0x8000) != 0;
#else
    Q_UNUSED(vk)
    return false;
#endif
}

#ifdef Q_OS_WIN
LRESULT CALLBACK keyboardHookProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (!g_inputManager || nCode < 0) {
        return CallNextHookEx(nullptr, nCode, wParam, lParam);
    }

    const KBDLLHOOKSTRUCT *data = reinterpret_cast<KBDLLHOOKSTRUCT *>(lParam);
    if (!data) {
        return CallNextHookEx(nullptr, nCode, wParam, lParam);
    }

    const bool suppress = g_inputManager->handleKeyEvent(static_cast<unsigned long>(wParam), data->vkCode);
    if (suppress) {
        return 1;
    }

    return CallNextHookEx(nullptr, nCode, wParam, lParam);
}

LRESULT CALLBACK mouseHookProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (!g_inputManager || nCode < 0) {
        return CallNextHookEx(nullptr, nCode, wParam, lParam);
    }

    const MSLLHOOKSTRUCT *data = reinterpret_cast<MSLLHOOKSTRUCT *>(lParam);
    if (!data) {
        return CallNextHookEx(nullptr, nCode, wParam, lParam);
    }

    const int wheelDelta =
        (wParam == WM_MOUSEWHEEL) ? static_cast<int>(static_cast<short>(HIWORD(data->mouseData))) : 0;
    g_inputManager->handleMouseEvent(static_cast<unsigned long>(wParam), data->pt.x, data->pt.y, wheelDelta);
    return CallNextHookEx(nullptr, nCode, wParam, lParam);
}

void sendVirtualKey(quint32 vk, bool isDown) {
    INPUT input{};
    input.type = INPUT_KEYBOARD;
    input.ki.wVk = static_cast<WORD>(vk);
    input.ki.dwFlags = isDown ? 0 : KEYEVENTF_KEYUP;
    SendInput(1, &input, sizeof(INPUT));
}
#endif
}  // namespace

InputManager::InputManager(QObject *parent) : QObject(parent) {
}

InputManager::~InputManager() {
    // Skip explicit Win32 cleanup (UnhookWindowsHookEx / UnregisterHotKey).
    // The OS removes all hooks and registered hotkeys when the process exits,
    // and doing it synchronously here causes noticeable shutdown lag because
    // UnhookWindowsHookEx blocks until any in-progress hook callback finishes.
    m_hotkeys.clear();
    m_keyListeners.clear();
    m_mouseListeners.clear();
#ifdef Q_OS_WIN
    g_inputManager = nullptr;
#endif
}

QString InputManager::nextId() {
    return QStringLiteral("im_%1").arg(++m_idCounter);
}

void InputManager::start() {
    if (m_running) {
        return;
    }

    QCoreApplication::instance()->installNativeEventFilter(this);
#ifdef Q_OS_WIN
    g_inputManager = this;
    m_keyboardHook = SetWindowsHookEx(WH_KEYBOARD_LL, keyboardHookProc, GetModuleHandle(nullptr), 0);
    // Mouse hook is installed lazily in addMouseListener.
#endif
    m_running = true;
}

void InputManager::stop() {
    if (!m_running) {
        return;
    }

#ifdef Q_OS_WIN
    for (auto it = m_hotkeys.cbegin(); it != m_hotkeys.cend(); ++it) {
        UnregisterHotKey(nullptr, it.value().nativeId);
    }
#endif
    m_hotkeys.clear();
    m_keyListeners.clear();
    m_mouseListeners.clear();

    QCoreApplication::instance()->removeNativeEventFilter(this);
#ifdef Q_OS_WIN
    if (m_keyboardHook) {
        UnhookWindowsHookEx(reinterpret_cast<HHOOK>(m_keyboardHook));
        m_keyboardHook = nullptr;
    }
    // m_mouseHook is managed lazily; already removed when last listener was removed.
    g_inputManager = nullptr;
#endif
    m_running = false;
}

QString InputManager::addHotkey(const QString &combo, std::function<void()> callback, bool suppressed) {
#ifdef Q_OS_WIN
    quint32 registerModifiers = 0;
    quint32 vk = 0;
    quint32 requiredModifiers = 0;
    QList<quint32> requiredKeys;

    if (!parseHotkey(combo, registerModifiers, vk, requiredModifiers, requiredKeys)) {
        return {};
    }

    start();

    const int minNativeId = 1;
    const int maxNativeId = 0xBFFF;
    int nativeId = static_cast<int>(qHash(combo.toLower()) % maxNativeId);
    if (nativeId < minNativeId) {
        nativeId = minNativeId;
    }

    bool registered = false;
    for (int attempts = 0; attempts < maxNativeId; ++attempts) {
        bool nativeIdTaken = false;
        for (auto it = m_hotkeys.cbegin(); it != m_hotkeys.cend(); ++it) {
            if (it.value().nativeId == nativeId) {
                nativeIdTaken = true;
                break;
            }
        }

        if (!nativeIdTaken && RegisterHotKey(nullptr, nativeId, registerModifiers, vk)) {
            registered = true;
            break;
        }

        ++nativeId;
        if (nativeId > maxNativeId) {
            nativeId = minNativeId;
        }
    }

    if (!registered) {
        return {};
    }

    const QString id = nextId();
    m_hotkeys.insert(
        id,
        HotkeyEntry{
            nativeId,
            combo.toLower(),
            registerModifiers,
            vk,
            requiredModifiers,
            requiredKeys,
            suppressed,
            std::move(callback)
        }
    );
    return id;
#else
    Q_UNUSED(combo)
    Q_UNUSED(callback)
    Q_UNUSED(suppressed)
    return {};
#endif
}

void InputManager::removeHotkey(const QString &id) {
#ifdef Q_OS_WIN
    if (m_hotkeys.contains(id)) {
        const int nativeId = m_hotkeys.value(id).nativeId;
        UnregisterHotKey(nullptr, nativeId);
        m_hotkeys.remove(id);
    }
#else
    Q_UNUSED(id)
#endif
}

QString InputManager::addKeyListener(std::function<void(const QString &, bool)> callback) {
    start();
    const QString id = nextId();
    m_keyListeners.insert(id, KeyListenerEntry{std::move(callback)});
    return id;
}

void InputManager::removeKeyListener(const QString &id) {
    m_keyListeners.remove(id);
}

QString InputManager::addMouseListener(std::function<void(const MouseEvent &)> callback) {
    start();
    const QString id = nextId();
    m_mouseListeners.insert(id, MouseListenerEntry{std::move(callback)});
#ifdef Q_OS_WIN
    if (!m_mouseHook) {
        m_mouseHook = SetWindowsHookEx(WH_MOUSE_LL, mouseHookProc, GetModuleHandle(nullptr), 0);
    }
#endif
    return id;
}

void InputManager::removeMouseListener(const QString &id) {
    m_mouseListeners.remove(id);
#ifdef Q_OS_WIN
    if (m_mouseListeners.isEmpty() && m_mouseHook) {
        UnhookWindowsHookEx(reinterpret_cast<HHOOK>(m_mouseHook));
        m_mouseHook = nullptr;
    }
#endif
}

QStringList InputManager::availableKeys() const {
    QStringList keys = keyMap().keys();
    std::sort(keys.begin(), keys.end());
    return keys;
}

void InputManager::sendKeys(const QString &combo) {
    sendPress(combo);
    sendRelease(combo);
}

void InputManager::sendPress(const QString &combo) {
#ifdef Q_OS_WIN
    const QStringList keys = splitCombo(combo);
    m_sendEvent = true;
    for (const QString &token : keys) {
        quint32 vk = 0;
        bool isModifier = false;
        if (tokenToVK(token, vk, isModifier))
            sendVirtualKey(vk, true);
    }
    m_sendEvent = false;
#else
    Q_UNUSED(combo)
#endif
}

void InputManager::sendRelease(const QString &combo) {
#ifdef Q_OS_WIN
    const QStringList keys = splitCombo(combo);
    m_sendEvent = true;
    for (int i = keys.size() - 1; i >= 0; --i) {
        quint32 vk = 0;
        bool isModifier = false;
        if (tokenToVK(keys.at(i), vk, isModifier))
            sendVirtualKey(vk, false);
    }
    m_sendEvent = false;
#else
    Q_UNUSED(combo)
#endif
}

bool InputManager::nativeEventFilter(const QByteArray &eventType, void *message, qintptr *result) {
#ifdef Q_OS_WIN
    Q_UNUSED(eventType)

    MSG *msg = static_cast<MSG *>(message);
    if (!msg || msg->message != WM_HOTKEY) {
        return false;
    }

    const int nativeId = static_cast<int>(msg->wParam);

    HotkeyEntry hotkey{};
    bool found = false;
    for (auto it = m_hotkeys.cbegin(); it != m_hotkeys.cend(); ++it) {
        if (it.value().nativeId == nativeId) {
            hotkey = it.value();
            found = true;
            break;
        }
    }

    if (!found) {
        return false;
    }

    if (!isModifierDown(hotkey.requiredModifiers)) {
        return false;
    }

    for (quint32 requiredVk : hotkey.requiredKeys) {
        if (!isVirtualKeyDown(requiredVk)) {
            return false;
        }
    }

    if (hotkey.callback) {
        hotkey.callback();
    }

    if (hotkey.suppressed) {
        if (result) {
            *result = 0;
        }
        return true;
    }

    return false;
#else
    Q_UNUSED(eventType)
    Q_UNUSED(message)
    Q_UNUSED(result)
    return false;
#endif
}

bool InputManager::parseHotkey(
    const QString &combo,
    quint32 &registerModifiers,
    quint32 &vk,
    quint32 &requiredModifiers,
    QList<quint32> &requiredKeys
) const {
#ifdef Q_OS_WIN
    const QStringList parts = splitCombo(combo);

    if (parts.isEmpty()) {
        return false;
    }

    registerModifiers = 0;
    vk = 0;
    requiredModifiers = 0;
    requiredKeys.clear();

    const int triggerIndex = parts.size() - 1;

    quint32 triggerVk = 0;
    bool triggerIsModifier = false;
    if (!tokenToVK(parts.at(triggerIndex), triggerVk, triggerIsModifier)) {
        return false;
    }
    vk = triggerVk;

    for (int i = 0; i < triggerIndex; ++i) {
        quint32 tokenVk = 0;
        bool isModifierToken = false;
        if (!tokenToVK(parts.at(i), tokenVk, isModifierToken)) {
            return false;
        }

        if (isModifierToken) {
            const quint32 mod = modifierFlagMap().value(parts.at(i));
            registerModifiers |= mod;
            requiredModifiers |= mod;
        } else {
            requiredKeys.append(tokenVk);
        }
    }

    if (triggerIsModifier) {
        requiredModifiers |= modifierFlagMap().value(parts.at(triggerIndex));
        registerModifiers &= ~modifierFlagMap().value(parts.at(triggerIndex));
    }

    requiredKeys.removeAll(vk);
    std::sort(requiredKeys.begin(), requiredKeys.end());
    requiredKeys.erase(std::unique(requiredKeys.begin(), requiredKeys.end()), requiredKeys.end());

    return vk != 0;
#else
    Q_UNUSED(combo)
    Q_UNUSED(registerModifiers)
    Q_UNUSED(vk)
    Q_UNUSED(requiredModifiers)
    Q_UNUSED(requiredKeys)
    return false;
#endif
}

bool InputManager::handleKeyEvent(unsigned long wParam, quint32 vkCode) {
#ifdef Q_OS_WIN
    if (m_sendEvent) {
        return false;
    }

    const QString key = VKToToken(vkCode).toLower();
    if (key.isEmpty()) {
        return false;
    }

    const bool isKeyMessage =
        (wParam == WM_KEYDOWN || wParam == WM_SYSKEYDOWN || wParam == WM_KEYUP || wParam == WM_SYSKEYUP);
    if (isKeyMessage) {
        const bool pressed = (wParam == WM_KEYDOWN || wParam == WM_SYSKEYDOWN);
        const auto listeners = m_keyListeners;
        for (const auto &entry : listeners)
            entry.callback(key, pressed);
    }

    return false;
#else
    Q_UNUSED(wParam)
    Q_UNUSED(vkCode)
    return false;
#endif
}

void InputManager::handleMouseEvent(unsigned long wParam, long x, long y, int wheelDelta) {
    if (m_mouseListeners.isEmpty()) {
        return;
    }

    MouseEvent evt;
    evt.globalPos = QPoint(static_cast<int>(x), static_cast<int>(y));
    evt.wheelDelta = wheelDelta;

#ifdef Q_OS_WIN
    switch (wParam) {
        case WM_MOUSEMOVE:
            evt.type = MouseEvent::Type::Move;
            break;
        case WM_LBUTTONDOWN:
            evt.type = MouseEvent::Type::LeftDown;
            break;
        case WM_LBUTTONUP:
            evt.type = MouseEvent::Type::LeftUp;
            break;
        case WM_RBUTTONDOWN:
            evt.type = MouseEvent::Type::RightDown;
            break;
        case WM_RBUTTONUP:
            evt.type = MouseEvent::Type::RightUp;
            break;
        case WM_MBUTTONDOWN:
            evt.type = MouseEvent::Type::MiddleDown;
            break;
        case WM_MBUTTONUP:
            evt.type = MouseEvent::Type::MiddleUp;
            break;
        case WM_MOUSEWHEEL:
            evt.type = (wheelDelta >= 0) ? MouseEvent::Type::WheelUp : MouseEvent::Type::WheelDown;
            break;
        default:
            return;
    }
#else
    Q_UNUSED(wParam)
    return;
#endif

    // Copy map to allow listeners to safely add/remove listeners inside the callback.
    const auto listeners = m_mouseListeners;
    for (const auto &entry : listeners) {
        entry.callback(evt);
    }
}
