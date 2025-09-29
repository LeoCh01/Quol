import winreg
from typing import List, Optional

from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from lib.global_input_manager import GlobalInputManager
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

        self.windows_dir = self.settings.get('windows_dir', './windows')
        self.is_hidden: bool = False
        self.is_reset: bool = self.settings.get('is_default_pos', True)

        self.input_manager = GlobalInputManager()
        self.input_manager.start()

        self.load_style_sheet()
        self.load_windows()
        self.setup_tray_icon()

        self.toggle_key: str = str(self.settings.get('toggle_key', '`'))
        self.toggle_key_id = None
        self.reset_hotkey(self.toggle_key)

    def save_settings(self):
        write_json('settings.json', self.settings)

    def load_settings(self):
        self.settings = read_json('settings.json')

    def load_style_sheet(self):
        stylesheet = read_text(f'res/styles/{self.settings.get("style")}/styles.qss')
        QApplication.instance().setStyleSheet(stylesheet)

    def load_transition(self):
        name = self.settings['transition']
        t = TransitionLoader(name)
        t.load()
        return t

    def get_is_hidden(self):
        return self.is_hidden

    def load_windows(self):
        transition_plugin = self.load_transition()
        context = WindowContext(self.toggle, self.toggle_windows, self.toggle_windows_instant, self.settings, transition_plugin, self.get_is_hidden, self.input_manager)

        plugin = SystemWindowLoader()
        plugin.load()
        self.windows.append(plugin.create_window(context, self))
        working_windows = []

        for name in self.settings.get('windows'):
            print('loading ' + name)
            plugin = WindowLoader(name, self.windows_dir)
            if not plugin.load():
                print(f'Failed to load window {name}. Skipping...')
                continue
            working_windows.append(name)
            self.windows.append(plugin.create_window(context))

        self.settings['windows'] = working_windows
        self.save_settings()

        for window in self.windows:
            self.toggle.connect(window.toggle_windows)
            window.show()

    def reset_hotkey(self, new_key: str):
        self.input_manager.remove_hotkey(self.toggle_key_id)
        self.toggle_key = new_key
        self.toggle_key_id = self.input_manager.add_hotkey(new_key, self.toggle_windows, suppressed=True)

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

        close_all_action = QAction('Close', self)
        close_all_action.triggered.connect(self.close_all)
        tray_menu.addAction(close_all_action)

        reload_action = QAction('Reload', self)
        reload_action.triggered.connect(self.reload)
        tray_menu.addAction(reload_action)

        quit_action = QAction('Quit', self)
        quit_action.triggered.connect(self.exit_app)
        tray_menu.addAction(quit_action)

        tray_icon.setContextMenu(tray_menu)
        tray_icon.show()

    def exit_app(self):
        self.close_all()
        QApplication.quit()

    def close_all(self):
        for w in self.windows:
            self.toggle.disconnect(w.toggle_windows)
            w.close()

        self.windows.clear()
        self.toggle_key_id = None
        self.input_manager.stop()

    def reload(self):
        self.close_all()

        self.load_settings()
        self.load_style_sheet()

        self.input_manager.start()
        self.reset_hotkey(str(self.settings.get('toggle_key', '`')))
        self.is_reset = self.settings.get('is_default_pos', True)
        self.is_hidden = False

        self.load_windows()

    @staticmethod
    def add_to_startup(app_name: str, app_path: str) -> bool:
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Failed to add to startup: {e}")
            return False

    @staticmethod
    def remove_from_startup(app_name: str) -> bool:
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_ALL_ACCESS
            )
            winreg.DeleteValue(key, app_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return True
        except Exception as e:
            print(f"Failed to remove from startup: {e}")
            return False

    @staticmethod
    def is_in_startup(app_name: str) -> bool:
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            value, regtype = winreg.QueryValueEx(key, app_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error checking startup: {e}")
            return False
