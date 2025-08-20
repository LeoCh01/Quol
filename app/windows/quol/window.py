import json
import os
import sys

from PySide6.QtCore import QSettings, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QGridLayout, QListWidget, QPushButton, QHBoxLayout, QListWidgetItem, QWidget, QLabel, QCheckBox

from lib.io_helpers import write_json
from lib.quol_window import QuolMainWindow, QuolSubWindow
from lib.window_loader import WindowInfo, WindowContext

RUN_PATH = 'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'


class MainWindow(QuolMainWindow):
    def __init__(self, app, window_info: WindowInfo, window_context: WindowContext):
        super().__init__('Quol', window_info, window_context, default_geometry=(10, 10, 180, 1))

        self.app = app
        self.settings_to_config()

        self.ver = QPushButton(f'v{self.app.settings['version']}')
        self.ver.clicked.connect(self.open_url)

        self.reload = QPushButton('Reload')
        self.reload.clicked.connect(self.app.restart)

        self.q = QPushButton('Quit')
        self.q.setStyleSheet('background-color: #c44; color: white;')
        self.q.clicked.connect(self.app.exit_app)

        self.manager = QPushButton('Manage Windows')
        self.manager.clicked.connect(self.show_manage_windows)

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.ver, 0, 0, 1, 2)
        self.grid_layout.addWidget(self.manager, 1, 0, 1, 2)
        self.grid_layout.addWidget(self.reload, 2, 0)
        self.grid_layout.addWidget(self.q, 2, 1)

        self.layout.addLayout(self.grid_layout)

        self.manage_windows_window = None

        self.app_name = self.config['name']
        self.app_path = self.get_app_path()
        self.settings = QSettings(RUN_PATH, QSettings.Format.NativeFormat)

    def show_manage_windows(self):
        if self.manage_windows_window is None:
            self.manage_windows_window = ManageWindow(self)
        self.manage_windows_window.show()

    def on_update_config(self):
        self.toggle_startup()
        self.config_to_settings()
        self.app.restart()

    @staticmethod
    def open_url():
        QDesktopServices.openUrl(QUrl('https://github.com/LeoCh01/quol'))

    @staticmethod
    def get_app_path():
        return sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]

    def config_to_settings(self):
        self.app.settings['toggle_key'] = self.config['toggle_key']
        self.app.settings['transition'] = self.config['transition']
        self.app.settings['startup'] = self.config['startup']
        self.app.settings['windows'] = self.config['_']['windows']
        self.app.save_settings()

    def settings_to_config(self):
        self.config['toggle_key'] = self.app.settings['toggle_key']
        self.config['transition'] = self.app.settings['transition']
        self.config['startup'] = self.app.settings['startup']
        self.config['_']['name'] = self.app.settings['name']
        self.config['_']['windows'] = self.app.settings['windows']

        write_json(self.window_info.config_path, self.config)

    def toggle_startup(self):
        if self.config['startup'] == self.app.settings['startup']:
            return

        if self.config['startup']:
            self.settings.setValue(self.app_name, self.app_path)
            print(f'Added {self.app_name} to startup with path: {self.app_path}')
        else:
            self.settings.remove(self.app_name)
            print(f'Removed {self.app_name} from startup')


class ManageWindow(QuolSubWindow):
    def __init__(self, main_window):
        super().__init__(main_window, "Manage Windows")
        self.setGeometry(300, 300, 300, 300)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        self.refresh_list()

    def refresh_list(self):
        windows_dir = os.path.join(os.path.dirname(__file__), '..')
        windows_dir = os.path.abspath(windows_dir)

        installed = [name for name in os.listdir(windows_dir)
                     if os.path.isdir(os.path.join(windows_dir, name))
                     and not name.startswith('__') and name != 'quol']
        active = self.main_window.config['_']['windows']

        self.list_widget.clear()

        for window in installed:
            item_widget = QWidget()
            layout = QHBoxLayout(item_widget)
            layout.setContentsMargins(5, 2, 5, 2)

            label = QLabel(window)
            checkbox = QCheckBox()
            checkbox.setChecked(window in active)
            checkbox.setText("Active" if window in active else "Inactive")

            checkbox.stateChanged.connect(lambda state, cb=checkbox, w=window: self.on_update_checkbox(state, cb, w))
            layout.addWidget(label)
            layout.addStretch()
            layout.addWidget(checkbox)

            item = QListWidgetItem(self.list_widget)
            item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)

    def on_update_checkbox(self, checked, cb, w):
        cb.setText("Active" if checked else "Inactive")

        if checked and w not in self.main_window.config['_']['windows']:
            self.main_window.config['_']['windows'].append(w)
        elif not checked and w in self.main_window.config['_']['windows']:
            self.main_window.config['_']['windows'].remove(w)
        self.main_window.config_to_settings()