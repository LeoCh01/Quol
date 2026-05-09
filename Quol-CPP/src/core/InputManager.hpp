#pragma once

#include <QAbstractNativeEventFilter>
#include <QHash>
#include <QList>
#include <QObject>
#include <QString>
#include <QStringList>

class InputManager : public QObject, public QAbstractNativeEventFilter {
    Q_OBJECT

public:
    explicit InputManager(QObject *parent = nullptr);
    ~InputManager() override;

    void start();
    void stop();

    Q_INVOKABLE int addHotkey(const QString &combo, bool suppressed = true);
    Q_INVOKABLE void removeHotkey(int id);
    Q_INVOKABLE void clearHotkeys();
    Q_INVOKABLE QStringList availableKeys() const;

    void sendKeys(const QString &combo);
    void sendPress(const QString &combo);
    void sendRelease(const QString &combo);

    bool handleKeyEvent(unsigned long wParam, quint32 vkCode);

    bool nativeEventFilter(const QByteArray &eventType, void *message, qintptr *result) override;

signals:
    void hotkeyTriggered(const QString &combo);
    void keyPressed(const QString &key);
    void keyReleased(const QString &key);

private:
    struct HotkeyEntry {
        int id;
        QString combo;
        quint32 registerModifiers;
        quint32 vk;
        quint32 requiredModifiers;
        QList<quint32> requiredKeys;
        bool suppressed;
    };

    bool parseHotkey(
        const QString &combo,
        quint32 &registerModifiers,
        quint32 &vk,
        quint32 &requiredModifiers,
        QList<quint32> &requiredKeys
    ) const;

    bool m_running;
    int m_nextId;
    QHash<int, HotkeyEntry> m_hotkeys;
    bool m_sendEvent = false;

#ifdef Q_OS_WIN
    void *m_keyboardHook = nullptr;
#endif
};
