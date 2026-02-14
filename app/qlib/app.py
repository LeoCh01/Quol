from types import SimpleNamespace
from typing import List, Optional

from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, QObject, QSettings
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from qlib.input_manager import GlobalInputManager
from qlib.io_helpers import read_text, read_json, write_json
from qlib.windows.quol_window import QuolMainWindow
from qlib.transitions.transition_loader import TransitionLoader
from qlib.windows.tool_loader import ToolLoader, SystemToolLoader
from globals import BASE_DIR

import logging

logger = logging.getLogger(__name__)
RUN_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"


class App(QObject):
    toggle = Signal(bool, bool)

    def __init__(self):
        super().__init__()

        self.tools: List[QuolMainWindow] = []
        self.settings: Optional[dict] = None
        self.load_settings()

        self.tools_dir = self.settings.get('tools_dir', './tools')
        self.is_hidden: bool = False
        self.is_reset: bool = self.settings.get('is_default_pos', True)
        self.tray_icon: Optional[QSystemTrayIcon] = None

        self.input_manager = GlobalInputManager()
        self.input_manager.start()

        self.load_style_sheet()
        self.load_tools()
        self.setup_tray_icon()

        self.toggle_key: str = str(self.settings.get('toggle_key', '`'))
        self.toggle_key_id = None
        self.reset_hotkey(self.toggle_key)

    def save_settings(self):
        write_json(BASE_DIR + '/settings.json', self.settings)

    def load_settings(self):
        self.settings = read_json(BASE_DIR + '/settings.json')

    def load_style_sheet(self):
        stylesheet = read_text(BASE_DIR + f'/res/styles/{self.settings.get("style")}/styles.qss')
        QApplication.instance().setStyleSheet(stylesheet)

    def load_transition(self):
        name = self.settings['transition']
        t = TransitionLoader(name)
        t.load()
        return t

    def get_is_hidden(self):
        return self.is_hidden

    def load_tools(self):
        transition_plugin = self.load_transition()

        context = SimpleNamespace()
        context.toggle = self.toggle
        context.toggle_tools = self.toggle_tools
        context.toggle_tools_instant = self.toggle_tools_instant
        context.transition_plugin = transition_plugin
        context.settings = self.settings
        context.get_is_hidden = self.get_is_hidden
        context.input_manager = self.input_manager

        plugin = SystemToolLoader()
        plugin.load()
        self.tools.append(plugin.create_window(context, self))
        working_tools = []

        for name in self.settings.get('tools'):
            logger.info('loading %s', name)
            plugin = ToolLoader(name, self.tools_dir)
            if not plugin.load():
                logger.warning('Failed to load window %s. Skipping...', name)
                continue
            working_tools.append(name)
            self.tools.append(plugin.create_window(context))

        self.settings['tools'] = working_tools
        self.save_settings()

        for window in self.tools:
            self.toggle.connect(window.toggle_windows)
            window.show()

    def reset_hotkey(self, new_key: str):
        self.input_manager.remove_hotkey(self.toggle_key_id)
        self.toggle_key = new_key
        self.toggle_key_id = self.input_manager.add_hotkey(new_key, self.toggle_tools, suppressed=True)

    def toggle_tools(self):
        self.toggle.emit(self.is_hidden, False)
        self.is_hidden = not self.is_hidden

    def toggle_tools_instant(self, show):
        self.toggle.emit(show, True)

    def set_toggle_key(self, key):
        key = str(key)
        logger.info('Changing toggle key from %s to %s', self.toggle_key, key)
        if self.toggle_key == key:
            return

        self.reset_hotkey(key)

        self.settings['toggle_key'] = key
        self.save_settings()

    def setup_tray_icon(self):
        if self.tray_icon:
            self.tray_icon.hide()
            self.tray_icon.deleteLater()

        self.tray_icon = QSystemTrayIcon(QIcon('res/icons/icon.ico'), parent=self)
        self.tray_icon.setToolTip('Quol')
        tray_menu = QMenu()

        self.toggle_close_action = QAction('Toggle OFF', self)
        self.toggle_close_action.triggered.connect(self.toggle_close)
        tray_menu.addAction(self.toggle_close_action)

        self.reload_action = QAction('Reload', self)
        self.reload_action.triggered.connect(self.reload)
        tray_menu.addAction(self.reload_action)

        self.quit_action = QAction('Quit', self)
        self.quit_action.triggered.connect(self.exit_app)
        tray_menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def exit_app(self):
        self.close_all()
        QApplication.quit()

    def close_all(self):
        for w in self.tools:
            try:
                self.toggle.disconnect(w.toggle_windows)
            except RuntimeError:
                pass
            
            if hasattr(w, 'config_window') and w.config_window:
                w.config_window.close()
                w.config_window.deleteLater()
                w.config_window = None
            
            if hasattr(w, 'transition') and w.transition:
                w.transition = None
            
            w.close()
            w.deleteLater()

        self.tools.clear()
        self.toggle_key_id = None
        self.input_manager.stop()

    def toggle_close(self):
        if self.toggle_close_action.text() == 'Toggle OFF':
            self.toggle_close_action.setText('Toggle ON')
            self.close_all()
        else:
            self.reload()

    def reload(self):
        self.close_all()

        self.load_settings()
        self.load_style_sheet()

        self.input_manager.start()
        self.reset_hotkey(str(self.settings.get('toggle_key', '`')))
        self.is_reset = self.settings.get('is_default_pos', True)
        self.is_hidden = False
        self.toggle_close_action.setText('Toggle OFF')

        self.load_tools()

    @staticmethod
    def add_to_startup(app_name: str, app_path: str) -> bool:
        q_settings = QSettings(RUN_PATH, QSettings.Format.NativeFormat)
        q_settings.setValue(app_name, f'"{app_path}"')
        return True

    @staticmethod
    def remove_from_startup(app_name: str) -> bool:
        q_settings = QSettings(RUN_PATH, QSettings.Format.NativeFormat)
        q_settings.remove(app_name)
        return True

    @staticmethod
    def is_in_startup(app_name: str) -> bool:
        q_settings = QSettings(RUN_PATH, QSettings.Format.NativeFormat)
        return q_settings.contains(app_name)
