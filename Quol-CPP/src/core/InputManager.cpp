#include "core/InputManager.hpp"

#include <QCoreApplication>

#ifdef Q_OS_WIN
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

InputManager::InputManager(QObject* parent)
    : QObject(parent),
      m_running(false),
      m_nextId(1)
{
}

InputManager::~InputManager()
{
    stop();
}

void InputManager::start()
{
    if (m_running)
    {
        return;
    }

    QCoreApplication::instance()->installNativeEventFilter(this);
    m_running = true;
}

void InputManager::stop()
{
    if (!m_running)
    {
        return;
    }

    clearHotkeys();
    QCoreApplication::instance()->removeNativeEventFilter(this);
    m_running = false;
}

int InputManager::addHotkey(const QString& combo, bool suppressed)
{
#ifdef Q_OS_WIN
    quint32 modifiers = 0;
    quint32 vk = 0;

    if (!parseHotkey(combo, modifiers, vk))
    {
        return -1;
    }

    start();

    const int id = m_nextId++;
    if (!RegisterHotKey(nullptr, id, modifiers, vk))
    {
        return -1;
    }

    m_hotkeys.insert(id, HotkeyEntry{id, combo.toLower(), modifiers, vk, suppressed});
    return id;
#else
    Q_UNUSED(combo)
    Q_UNUSED(suppressed)
    return -1;
#endif
}

void InputManager::removeHotkey(int id)
{
#ifdef Q_OS_WIN
    if (m_hotkeys.contains(id))
    {
        UnregisterHotKey(nullptr, id);
        m_hotkeys.remove(id);
    }
#else
    Q_UNUSED(id)
#endif
}

void InputManager::clearHotkeys()
{
#ifdef Q_OS_WIN
    const auto ids = m_hotkeys.keys();
    for (const int id : ids)
    {
        UnregisterHotKey(nullptr, id);
    }
#endif
    m_hotkeys.clear();
}

bool InputManager::nativeEventFilter(const QByteArray& eventType, void* message, qintptr* result)
{
#ifdef Q_OS_WIN
    Q_UNUSED(eventType)

    MSG* msg = static_cast<MSG*>(message);
    if (!msg || msg->message != WM_HOTKEY)
    {
        return false;
    }

    const int id = static_cast<int>(msg->wParam);
    if (!m_hotkeys.contains(id))
    {
        return false;
    }

    const auto hotkey = m_hotkeys.value(id);
    emit hotkeyTriggered(hotkey.combo);

    if (hotkey.suppressed)
    {
        if (result)
        {
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

bool InputManager::parseHotkey(const QString& combo, quint32& modifiers, quint32& vk) const
{
#ifdef Q_OS_WIN
    QStringList parts = combo.toLower().split('+', Qt::SkipEmptyParts);
    if (parts.isEmpty())
    {
        return false;
    }

    modifiers = 0;
    vk = 0;

    static const QHash<QString, quint32> modifierMap = {
        {"ctrl", MOD_CONTROL},
        {"control", MOD_CONTROL},
        {"shift", MOD_SHIFT},
        {"alt", MOD_ALT},
        {"win", MOD_WIN},
        {"meta", MOD_WIN}
    };

    static const QHash<QString, quint32> specialMap = {
        {"`", VK_OEM_3},
        {"esc", VK_ESCAPE},
        {"space", VK_SPACE},
        {"tab", VK_TAB},
        {"enter", VK_RETURN},
        {"left", VK_LEFT},
        {"right", VK_RIGHT},
        {"up", VK_UP},
        {"down", VK_DOWN}
    };

    for (const QString& token : parts)
    {
        const QString key = token.trimmed();

        if (modifierMap.contains(key))
        {
            modifiers |= modifierMap.value(key);
            continue;
        }

        if (specialMap.contains(key))
        {
            vk = specialMap.value(key);
            continue;
        }

        if (key.size() == 1)
        {
            const QChar ch = key.at(0).toUpper();
            if (ch.isLetterOrNumber())
            {
                vk = static_cast<quint32>(ch.unicode());
                continue;
            }
        }

        if (key.startsWith('f'))
        {
            bool ok = false;
            const int fn = key.mid(1).toInt(&ok);
            if (ok && fn >= 1 && fn <= 24)
            {
                vk = static_cast<quint32>(VK_F1 + (fn - 1));
                continue;
            }
        }

        return false;
    }

    return vk != 0;
#else
    Q_UNUSED(combo)
    Q_UNUSED(modifiers)
    Q_UNUSED(vk)
    return false;
#endif
}
