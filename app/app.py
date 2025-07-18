import importlib
import keyboard
import logging
import os
import sys
from typing import List

from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from res.paths import SETTINGS_PATH, STYLES_PATH, ICONS_PATH
from io_helpers import read_text, read_json, write_json
from quol_window import QuolMainWindow
from transition_plugin import TransitionPlugin
from window_plugin import WindowPlugin, WindowPluginContext, SystemWindowPlugin


class App(QObject):
    toggle = Signal(bool, bool)

    def __init__(self):
        super().__init__()

        self.settings: dict
        self.load_settings()

        self.load_style_sheet()

        self.toggle_key: str = str(self.settings.get('toggle_key', '`'))
        self.reset_hotkey(self.toggle_key)

        self.is_hidden: bool = False
        self.is_reset: bool = self.settings.get('is_default_pos', True)

        self.windows: List[QuolMainWindow] = []
        self.load_windows()
        self.setup_tray_icon()

    def save_settings(self):
        write_json(SETTINGS_PATH, self.settings)

    def load_settings(self):
        self.settings = read_json(SETTINGS_PATH)

    def load_style_sheet(self):
        stylesheet = read_text(f'{STYLES_PATH}/{self.settings.get("style")}/styles.qss')
        QApplication.instance().setStyleSheet(stylesheet)

    def load_transition(self):
        name = self.settings['transition']
        # try:
        plugin = TransitionPlugin(name)
        plugin.load()
        # except Exception as e:
        #     print('error :: ', e)
        #     logging.error(f'Error loading {name} :: {e}', exc_info=True)
        #     continue
        return plugin

    def load_windows(self):
        transition_plugin = self.load_transition()
        context = WindowPluginContext(self.toggle, self.toggle_windows, self.toggle_windows_instant, self.settings, transition_plugin)

        for name in self.settings.get('windows'):
            # try:
            if name == 'info':
                plugin = SystemWindowPlugin('info')
                plugin.load()
                window = plugin.create_window(self, context)
            else:
                print('loading ' + name)
                plugin = WindowPlugin(name)
                plugin.load()
                window = plugin.create_window(context)
            # except Exception as e:
            #     print('error :: ', e)
            #     logging.error(f'Error loading {name} :: {e}', exc_info=True)
            #     continue

            self.windows.append(window)

        for window in self.windows:
            self.toggle.connect(window.toggle_windows)
            window.show()

    def reset_hotkey(self, new_key: str, old_key=None):
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

        self.reset_hotkey(key, self.toggle_key)

        self.settings['toggle_key'] = key
        self.save_settings()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon(ICONS_PATH + 'icon.ico'), parent=self)
        self.tray_icon.setToolTip('Quol')
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

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def exit_app(self):
        for w in self.windows:
            self.toggle.disconnect(w.toggle_windows)
            w.close()
            del w
        QApplication.quit()

    def hide(self):
        for w in self.windows:
            self.toggle.disconnect(w.toggle_windows)
            w.close()
            del w

        self.windows = []
        keyboard.unhook_all()

    def restart(self):
        self.hide()

        self.load_settings()
        self.load_style_sheet()

        self.reset_hotkey(str(self.settings.get('toggle_key', '`')), self.toggle_key)
        self.is_hidden = False
        self.is_reset = self.settings.get('is_default_pos', True)

        self.load_windows()
