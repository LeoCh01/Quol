#pragma once

#include <QAbstractNativeEventFilter>
#include <QHash>
#include <QObject>
#include <QString>

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

    bool nativeEventFilter(const QByteArray &eventType, void *message, qintptr *result) override;

signals:
    void hotkeyTriggered(const QString &combo);

private:
    struct HotkeyEntry {
        int id;
        QString combo;
        quint32 modifiers;
        quint32 vk;
        bool suppressed;
    };

    bool parseHotkey(const QString &combo, quint32 &modifiers, quint32 &vk) const;

    bool m_running;
    int m_nextId;
    QHash<int, HotkeyEntry> m_hotkeys;
};
