import keyboard
from typing import List, Optional

from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from lib.io_helpers import read_text, read_json, write_json
from lib.quol_window import QuolMainWindow
from lib.transition_loader import TransitionLoader
from lib.window_loader import WindowLoader, WindowContext, SystemWindowLoader


class App(QObject):
    toggle = Signal(bool, bool)

    def __init__(self):
        super().__init__()

        self.windows: List[QuolMainWindow] = []
        self.settings: Optional[dict] = None

        self.load_settings()
        self.load_style_sheet()
        self.load_windows()
        self.setup_tray_icon()

        self.toggle_key: str = str(self.settings.get('toggle_key', '`'))
        self.reset_hotkey(self.toggle_key)

        self.is_hidden: bool = False
        self.is_reset: bool = self.settings.get('is_default_pos', True)

    def save_settings(self):
        write_json('res/settings.json', self.settings)

    def load_settings(self):
        self.settings = read_json('res/settings.json')

    def load_style_sheet(self):
        stylesheet = read_text(f'res/styles/{self.settings.get("style")}/styles.qss')
        QApplication.instance().setStyleSheet(stylesheet)

    def load_transition(self):
        name = self.settings['transition']
        t = TransitionLoader(name)
        t.load()
        return t

    def load_windows(self):
        transition_plugin = self.load_transition()
        context = WindowContext(self.toggle, self.toggle_windows, self.toggle_windows_instant, self.settings, transition_plugin)

        for name in self.settings.get('windows'):
            if name == 'info':
                plugin = SystemWindowLoader('info')
                plugin.load()
                window = plugin.create_window(context, self)
            else:
                print('loading ' + name)
                plugin = WindowLoader(name)
                plugin.load()
                window = plugin.create_window(context)

            self.windows.append(window)

        for window in self.windows:
            self.toggle.connect(window.toggle_windows)
            window.show()

    def reset_hotkey(self, new_key: str):
        keyboard.unhook_all()
        self.toggle_key = new_key
        keyboard.add_hotkey(new_key, self.toggle_windows, suppress=True)

    def toggle_windows(self):
        self.toggle.emit(self.is_hidden, False)
        self.is_hidden = not self.is_hidden

    def toggle_windows_instant(self, show):
        self.toggle.emit(show, True)

    def set_toggle_key(self, key):
        key = str(key)
        print(f'Changing toggle key from {self.toggle_key} to {key}')
        if self.toggle_key == key:
            return

        self.reset_hotkey(key)

        self.settings['toggle_key'] = key
        self.save_settings()

    def setup_tray_icon(self):
        tray_icon = QSystemTrayIcon(QIcon('res/icons/icon.ico'), parent=self)
        tray_icon.setToolTip('Quol')
        tray_menu = QMenu()

        hide_action = QAction('Hide', self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)

        reload_action = QAction('Reload', self)
        reload_action.triggered.connect(self.restart)
        tray_menu.addAction(reload_action)

        quit_action = QAction('Quit', self)
        quit_action.triggered.connect(self.exit_app)
        tray_menu.addAction(quit_action)

        tray_icon.setContextMenu(tray_menu)
        tray_icon.show()

    def exit_app(self):
        self.hide()
        QApplication.quit()

    def hide(self):
        for w in self.windows:
            self.toggle.disconnect(w.toggle_windows)
            w.close()

        self.windows.clear()
        keyboard.unhook_all()

    def restart(self):
        self.hide()

        self.load_settings()
        self.load_style_sheet()

        self.reset_hotkey(str(self.settings.get('toggle_key', '`')))
        self.is_reset = self.settings.get('is_default_pos', True)
        self.is_hidden = False

        self.load_windows()
