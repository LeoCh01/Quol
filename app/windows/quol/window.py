import os
import sys

from PySide6.QtCore import QSettings, QUrl, QSize
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QGridLayout, QListWidget, QPushButton, QHBoxLayout, QListWidgetItem, QWidget, QLabel, \
    QCheckBox, QTabWidget, QVBoxLayout
from qasync import asyncSlot

from lib.io_helpers import write_json
from lib.quol_window import QuolMainWindow, QuolSubWindow
from lib.window_loader import WindowInfo, WindowContext
from lib.api import get_store_items, download_item, update_item

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

        self.app_name = self.config['_']['name']
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
        self.setGeometry(300, 300, 400, 400)

        self.tabs = QTabWidget()
        self.installed_tab = QWidget()
        self.store_tab = QWidget()

        self.tabs.addTab(self.installed_tab, "Installed")
        self.tabs.addTab(self.store_tab, "Store")

        self.layout.addWidget(self.tabs)

        self.setup_installed_tab()
        self.setup_store_tab()

    def setup_installed_tab(self):
        self.installed_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.installed_layout.addWidget(self.list_widget)
        self.installed_tab.setLayout(self.installed_layout)
        self.refresh_list()

    def setup_store_tab(self):
        self.store_layout = QVBoxLayout()
        self.store_list_widget = QListWidget()
        self.store_layout.addWidget(self.store_list_widget)
        self.store_tab.setLayout(self.store_layout)
        self.refresh_store_list()

    def refresh_list(self):
        windows_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        installed = [name for name in os.listdir(windows_dir)
                     if os.path.isdir(os.path.join(windows_dir, name))
                     and not name.startswith('__') and name != 'quol']
        active = self.main_window.config['_']['windows']

        self.list_widget.clear()

        for window in sorted(installed):
            if '-v' in window:
                name_part, version = window.rsplit('-v', 1)
                version = 'v' + version
            else:
                name_part = window
                version = 'v0'

            display_name = f"{name_part} ({version})"

            item_widget = QWidget()
            layout = QHBoxLayout(item_widget)
            layout.setContentsMargins(5, 2, 5, 2)

            name_label = QLabel(display_name)
            status_label = QLabel("Active" if window in active else "Inactive")
            checkbox = QCheckBox()
            checkbox.setChecked(window in active)

            checkbox.stateChanged.connect(lambda s, w=window, sl=status_label: self.on_update_checkbox(s, w, sl))

            layout.addWidget(name_label)
            layout.addStretch()
            layout.addWidget(status_label)
            layout.addWidget(checkbox)

            item = QListWidgetItem(self.list_widget)
            item.setSizeHint(QSize(0, 35))
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)

    def on_update_checkbox(self, checked, w, status_label):
        status_label.setText("Active" if checked else "Inactive")

        if checked and w not in self.main_window.config['_']['windows']:
            self.main_window.config['_']['windows'].append(w)
        elif not checked and w in self.main_window.config['_']['windows']:
            self.main_window.config['_']['windows'].remove(w)

        self.main_window.config_to_settings()

    @asyncSlot()
    async def refresh_store_list(self):
        store_items = await get_store_items()

        windows_dir = os.path.join(os.path.dirname(__file__), '..')
        windows_dir = os.path.abspath(windows_dir)
        installed = [name for name in os.listdir(windows_dir)
                     if os.path.isdir(os.path.join(windows_dir, name))
                     and not name.startswith('__') and name != 'quol']

        self.store_list_widget.clear()

        for entry in sorted(store_items, key=lambda x: x['name']):
            raw_name = entry['name']
            if not raw_name.endswith('.zip'):
                continue

            full_tool_name = raw_name[:-4]  # Remove '.zip'

            if '-v' in full_tool_name:
                name_part, version = full_tool_name.rsplit('-v', 1)
                version = 'v' + version
            else:
                name_part = full_tool_name
                version = 'v0'

            matching_installed = [x for x in installed if x.startswith(name_part + '-v')]
            current_version_installed = name_part + '-' + version in matching_installed

            item_widget = QWidget()
            layout = QHBoxLayout(item_widget)
            layout.setContentsMargins(5, 2, 5, 2)

            name_label = QLabel(f"{name_part} ({version})")

            if current_version_installed:
                status_label = QLabel("Installed")
                layout.addWidget(name_label)
                layout.addStretch()
                layout.addWidget(status_label)
            elif matching_installed:
                update_button = QPushButton("Update")
                update_button.setStyleSheet("padding: 5px;")
                update_button.clicked.connect(lambda _, new_name=full_tool_name, old_name=matching_installed[0]: self.on_update(new_name, old_name))
                layout.addWidget(name_label)
                layout.addStretch()
                layout.addWidget(update_button)
            else:
                install_button = QPushButton("Install")
                install_button.setStyleSheet("padding: 5px;")
                install_button.clicked.connect(lambda _, name=full_tool_name: self.on_install(name))
                layout.addWidget(name_label)
                layout.addStretch()
                layout.addWidget(install_button)

            item = QListWidgetItem(self.store_list_widget)
            item.setSizeHint(QSize(0, 35))
            self.store_list_widget.addItem(item)
            self.store_list_widget.setItemWidget(item, item_widget)

    @asyncSlot()
    async def on_install(self, name):
        print(f"Install clicked for: {name}")
        await download_item(name)
        self.refresh_list()
        await self.refresh_store_list()

    @asyncSlot()
    async def on_update(self, new_name, old_name):
        print(f"Update clicked for: {new_name} (old: {old_name})")
        await update_item(new_name, old_name)
        self.refresh_list()
        await self.refresh_store_list()
