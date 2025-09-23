import threading
from pynput import keyboard, mouse
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener

VK_TO_STR = {
    0x08: 'backspace',
    0x09: 'tab',
    0x0D: 'enter',
    0x10: 'shift',
    0x11: 'ctrl',
    0x12: 'alt',
    0x13: 'pause',
    0x14: 'caps_lock',
    0x1B: 'esc',
    0x20: ' ',
    0x21: 'page_up',
    0x22: 'page_down',
    0x23: 'end',
    0x24: 'home',
    0x25: 'left',
    0x26: 'up',
    0x27: 'right',
    0x28: 'down',
    0x2C: 'print_screen',
    0x2D: 'insert',
    0x2E: 'delete',

    # Numbers 0-9
    0x30: '0',
    0x31: '1',
    0x32: '2',
    0x33: '3',
    0x34: '4',
    0x35: '5',
    0x36: '6',
    0x37: '7',
    0x38: '8',
    0x39: '9',

    # Letters a-z
    0x41: 'a',
    0x42: 'b',
    0x43: 'c',
    0x44: 'd',
    0x45: 'e',
    0x46: 'f',
    0x47: 'g',
    0x48: 'h',
    0x49: 'i',
    0x4A: 'j',
    0x4B: 'k',
    0x4C: 'l',
    0x4D: 'm',
    0x4E: 'n',
    0x4F: 'o',
    0x50: 'p',
    0x51: 'q',
    0x52: 'r',
    0x53: 's',
    0x54: 't',
    0x55: 'u',
    0x56: 'v',
    0x57: 'w',
    0x58: 'x',
    0x59: 'y',
    0x5A: 'z',

    # Function keys F1-F12
    0x70: 'f1',
    0x71: 'f2',
    0x72: 'f3',
    0x73: 'f4',
    0x74: 'f5',
    0x75: 'f6',
    0x76: 'f7',
    0x77: 'f8',
    0x78: 'f9',
    0x79: 'f10',
    0x7A: 'f11',
    0x7B: 'f12',

    # Numpad keys
    0x60: '0',
    0x61: '1',
    0x62: '2',
    0x63: '3',
    0x64: '4',
    0x65: '5',
    0x66: '6',
    0x67: '7',
    0x68: '8',
    0x69: '9',
    0x6A: '*',
    0x6B: '+',
    0x6D: '-',
    0x6E: '.',
    0x6F: '/',

    # Other punctuation keys
    0xBA: ';',
    0xBB: '=',
    0xBC: ',',
    0xBD: '-',
    0xBE: '.',
    0xBF: '/',
    0xC0: '`',
    0xDB: '[',
    0xDC: '\\',
    0xDD: ']',
    0xDE: '\'',

    # Modifier keys
    0xA0: 'shift',
    0xA1: 'shift_r',
    0xA2: 'ctrl',
    0xA3: 'ctrl_r',
    0xA4: 'alt',
    0xA5: 'alt_r',
}

STR_TO_VK = {v: k for k, v in VK_TO_STR.items()}


class GlobalInputManager:
    def __init__(self):
        self.hotkey_callbacks = {}  # {'ctrl+shift+a': callback_fn}
        self.key_press_callbacks = []  # [(callback_fn, (suppressed))]
        self.key_release_callbacks = []  # [(callback_fn, (suppressed))]
        self.mouse_move_callbacks = []  # [callback_fn]
        self.mouse_click_callbacks = []  # [callback_fn]

        self._pressed_keys = set()
        self._keyboard_listener = None
        self._mouse_listener = None
        self._listeners_thread = None
        self._running = False

    def _win32_event_filter(self, msg, data):

        def run(callbacks):
            key = VK_TO_STR.get(data.vkCode, '')
            for callback, suppressed in callbacks:
                callback(key)
                if key in suppressed:
                    self._keyboard_listener.suppress_event()

        if msg == 256:  # WM_KEYDOWN
            run(self.key_press_callbacks)
        elif msg == 257:  # WM_KEYUP
            run(self.key_release_callbacks)

    def _on_mouse_move(self, x, y):
        for callback in self.mouse_move_callbacks:
            callback(x, y)

    def _on_mouse_click(self, x, y, button, pressed):
        for callback in self.mouse_click_callbacks:
            callback(x, y, button.name if button else None, pressed)

    def add_hotkey(self, combo, callback):  # TODO: add to on_press
        combo = combo.lower()
        if combo not in self.hotkey_callbacks:
            self.hotkey_callbacks[combo] = []
        self.hotkey_callbacks[combo].append(callback)

    def add_key_press_listener(self, callback, suppressed=tuple()):
        self.key_press_callbacks.append((callback, suppressed))

    def add_key_release_listener(self, callback, suppressed=tuple()):
        self.key_release_callbacks.append((callback, suppressed))

    def add_mouse_move_listener(self, callback):
        self.mouse_move_callbacks.append(callback)

    def add_mouse_click_listener(self, callback):
        self.mouse_click_callbacks.append(callback)

    def start(self):
        if self._running:
            return
        self._running = True

        self._listeners_thread = threading.Thread(target=self._run_listeners, daemon=True)
        self._listeners_thread.start()

    def stop(self):
        self._running = False
        if self._keyboard_listener:
            self._keyboard_listener.stop()
        if self._mouse_listener:
            self._mouse_listener.stop()
        if self._listeners_thread:
            self._listeners_thread.join()

    def _run_listeners(self):
        with KeyboardListener(
            win32_event_filter=self._win32_event_filter,
        ) as k_listener, MouseListener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click
        ) as m_listener:
            self._keyboard_listener = k_listener
            self._mouse_listener = m_listener
            k_listener.join()
            m_listener.join()
