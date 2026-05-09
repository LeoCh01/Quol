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
        {"ctrl", MOD_CONTROL},
        {"control", MOD_CONTROL},
        {"shift", MOD_SHIFT},
        {"alt", MOD_ALT},
        {"win", MOD_WIN},
        {"meta", MOD_WIN}
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
            {"ctrl", VK_CONTROL},
            {"control", VK_CONTROL},
            {"shift", VK_SHIFT},
            {"alt", VK_MENU},
            {"win", VK_LWIN},
            {"meta", VK_LWIN},

            {"backtick", VK_OEM_3},
            {"grave", VK_OEM_3},
            {"tilde", VK_OEM_3},
            {"minus", VK_OEM_MINUS},
            {"dash", VK_OEM_MINUS},
            {"hyphen", VK_OEM_MINUS},
            {"equals", VK_OEM_PLUS},
            {"equal", VK_OEM_PLUS},
            {"plus", VK_OEM_PLUS},
            {"left_bracket", VK_OEM_4},
            {"right_bracket", VK_OEM_6},
            {"backslash", VK_OEM_5},
            {"semicolon", VK_OEM_1},
            {"quote", VK_OEM_7},
            {"apostrophe", VK_OEM_7},
            {"comma", VK_OEM_COMMA},
            {"period", VK_OEM_PERIOD},
            {"dot", VK_OEM_PERIOD},
            {"slash", VK_OEM_2},
            {"esc", VK_ESCAPE},
            {"escape", VK_ESCAPE},
            {"space", VK_SPACE},
            {"tab", VK_TAB},
            {"enter", VK_RETURN},
            {"return", VK_RETURN},
            {"left", VK_LEFT},
            {"right", VK_RIGHT},
            {"up", VK_UP},
            {"down", VK_DOWN},
            {"insert", VK_INSERT},
            {"delete", VK_DELETE},
            {"home", VK_HOME},
            {"end", VK_END},
            {"pageup", VK_PRIOR},
            {"pagedown", VK_NEXT}
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

bool tokenToVirtualKey(const QString &key, quint32 &vk, bool &isModifierToken) {
    isModifierToken = modifierFlagMap().contains(key);
    vk = keyMap().value(key, 0);
    return vk != 0;
}

QString tokenFromVirtualKey(quint32 vk) {
#ifdef Q_OS_WIN
    if (vk >= 'A' && vk <= 'Z') {
        return QString(QChar(static_cast<ushort>(vk))).toLower();
    }

    if (vk >= '0' && vk <= '9') {
        return QString(QChar(static_cast<ushort>(vk)));
    }

    if (vk >= VK_F1 && vk <= VK_F24) {
        return QString("f%1").arg(static_cast<int>(vk - VK_F1 + 1));
    }

    static const QHash<quint32, QString> map = {
        {VK_BACK, "backspace"},
        {VK_TAB, "tab"},
        {VK_RETURN, "enter"},
        {VK_PAUSE, "pause"},
        {VK_CAPITAL, "caps_lock"},
        {VK_ESCAPE, "esc"},
        {VK_SPACE, "space"},
        {VK_PRIOR, "pageup"},
        {VK_NEXT, "pagedown"},
        {VK_END, "end"},
        {VK_HOME, "home"},
        {VK_LEFT, "left"},
        {VK_UP, "up"},
        {VK_RIGHT, "right"},
        {VK_DOWN, "down"},
        {VK_SNAPSHOT, "print_screen"},
        {VK_INSERT, "insert"},
        {VK_DELETE, "delete"},
        {VK_NUMPAD0, "0"},
        {VK_NUMPAD1, "1"},
        {VK_NUMPAD2, "2"},
        {VK_NUMPAD3, "3"},
        {VK_NUMPAD4, "4"},
        {VK_NUMPAD5, "5"},
        {VK_NUMPAD6, "6"},
        {VK_NUMPAD7, "7"},
        {VK_NUMPAD8, "8"},
        {VK_NUMPAD9, "9"},
        {VK_MULTIPLY, "*"},
        {VK_ADD, "+"},
        {VK_SUBTRACT, "-"},
        {VK_DECIMAL, "."},
        {VK_DIVIDE, "/"},
        {VK_OEM_1, "semicolon"},
        {VK_OEM_PLUS, "equals"},
        {VK_OEM_COMMA, "comma"},
        {VK_OEM_MINUS, "minus"},
        {VK_OEM_PERIOD, "period"},
        {VK_OEM_2, "slash"},
        {VK_OEM_3, "backtick"},
        {VK_OEM_4, "left_bracket"},
        {VK_OEM_5, "backslash"},
        {VK_OEM_6, "right_bracket"},
        {VK_OEM_7, "quote"},
        {VK_SHIFT, "shift"},
        {VK_LSHIFT, "shift"},
        {VK_RSHIFT, "shift_r"},
        {VK_CONTROL, "ctrl"},
        {VK_LCONTROL, "ctrl"},
        {VK_RCONTROL, "ctrl_r"},
        {VK_MENU, "alt"},
        {VK_LMENU, "alt"},
        {VK_RMENU, "alt_r"}
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
    if (modifier & MOD_CONTROL) {
        if (!(GetAsyncKeyState(VK_CONTROL) & 0x8000)) {
            return false;
        }
    }

    if (modifier & MOD_SHIFT) {
        if (!(GetAsyncKeyState(VK_SHIFT) & 0x8000)) {
            return false;
        }
    }

    if (modifier & MOD_ALT) {
        if (!(GetAsyncKeyState(VK_MENU) & 0x8000)) {
            return false;
        }
    }

    if (modifier & MOD_WIN) {
        if (!((GetAsyncKeyState(VK_LWIN) & 0x8000) || (GetAsyncKeyState(VK_RWIN) & 0x8000))) {
            return false;
        }
    }

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

void sendVirtualKey(quint32 vk, bool isDown) {
    INPUT input{};
    input.type = INPUT_KEYBOARD;
    input.ki.wVk = static_cast<WORD>(vk);
    input.ki.dwFlags = isDown ? 0 : KEYEVENTF_KEYUP;
    SendInput(1, &input, sizeof(INPUT));
}
#endif
}  // namespace

InputManager::InputManager(QObject *parent) : QObject(parent), m_running(false), m_nextId(1) {
}

InputManager::~InputManager() {
    stop();
}

void InputManager::start() {
    if (m_running) {
        return;
    }

    QCoreApplication::instance()->installNativeEventFilter(this);
#ifdef Q_OS_WIN
    g_inputManager = this;
    m_keyboardHook = SetWindowsHookEx(WH_KEYBOARD_LL, keyboardHookProc, GetModuleHandle(nullptr), 0);
#endif
    m_running = true;
}

void InputManager::stop() {
    if (!m_running) {
        return;
    }

    clearHotkeys();
    QCoreApplication::instance()->removeNativeEventFilter(this);
#ifdef Q_OS_WIN
    if (m_keyboardHook) {
        UnhookWindowsHookEx(reinterpret_cast<HHOOK>(m_keyboardHook));
        m_keyboardHook = nullptr;
    }
    g_inputManager = nullptr;
#endif
    m_running = false;
}

int InputManager::addHotkey(const QString &combo, bool suppressed) {
#ifdef Q_OS_WIN
    quint32 registerModifiers = 0;
    quint32 vk = 0;
    quint32 requiredModifiers = 0;
    QList<quint32> requiredKeys;

    if (!parseHotkey(combo, registerModifiers, vk, requiredModifiers, requiredKeys)) {
        return -1;
    }

    start();

    const int id = m_nextId++;
    if (!RegisterHotKey(nullptr, id, registerModifiers, vk)) {
        return -1;
    }

    m_hotkeys.insert(
        id, HotkeyEntry{id, combo.toLower(), registerModifiers, vk, requiredModifiers, requiredKeys, suppressed}
    );
    return id;
#else
    Q_UNUSED(combo)
    Q_UNUSED(suppressed)
    return -1;
#endif
}

void InputManager::removeHotkey(int id) {
#ifdef Q_OS_WIN
    if (m_hotkeys.contains(id)) {
        UnregisterHotKey(nullptr, id);
        m_hotkeys.remove(id);
    }
#else
    Q_UNUSED(id)
#endif
}

void InputManager::clearHotkeys() {
#ifdef Q_OS_WIN
    const auto ids = m_hotkeys.keys();
    for (const int id : ids) {
        UnregisterHotKey(nullptr, id);
    }
#endif
    m_hotkeys.clear();
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
        if (tokenToVirtualKey(token, vk, isModifier)) {
            sendVirtualKey(vk, true);
        }
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
        if (tokenToVirtualKey(keys.at(i), vk, isModifier)) {
            sendVirtualKey(vk, false);
        }
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

    const int id = static_cast<int>(msg->wParam);
    if (!m_hotkeys.contains(id)) {
        return false;
    }

    const auto hotkey = m_hotkeys.value(id);

    if (!isModifierDown(hotkey.requiredModifiers)) {
        return false;
    }

    for (quint32 requiredVk : hotkey.requiredKeys) {
        if (!isVirtualKeyDown(requiredVk)) {
            return false;
        }
    }

    emit hotkeyTriggered(hotkey.combo);

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
    const QStringList rawParts = combo.toLower().split('+', Qt::SkipEmptyParts);
    QStringList parts;
    for (const QString &token : rawParts) {
        const QString key = token.trimmed();
        if (!key.isEmpty()) {
            parts.append(key);
        }
    }

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
    if (!tokenToVirtualKey(parts.at(triggerIndex), triggerVk, triggerIsModifier)) {
        return false;
    }
    vk = triggerVk;

    for (int i = 0; i < triggerIndex; ++i) {
        quint32 tokenVk = 0;
        bool isModifierToken = false;
        if (!tokenToVirtualKey(parts.at(i), tokenVk, isModifierToken)) {
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

    const QString key = tokenFromVirtualKey(vkCode).toLower();
    if (key.isEmpty()) {
        return false;
    }

    if (wParam == WM_KEYDOWN || wParam == WM_SYSKEYDOWN) {
        emit keyPressed(key);
    } else if (wParam == WM_KEYUP || wParam == WM_SYSKEYUP) {
        emit keyReleased(key);
    }

    return false;
#else
    Q_UNUSED(wParam)
    Q_UNUSED(vkCode)
    return false;
#endif
}
