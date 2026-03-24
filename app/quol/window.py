import logging
import os
import sys

from PySide6.QtCore import QUrl, QSize
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import QGridLayout, QListWidget, QPushButton, QHBoxLayout, QListWidgetItem, QWidget, QLabel, \
    QCheckBox, QTabWidget, QVBoxLayout

from globals import BASE_DIR
from qlib.io_helpers import read_json
from qlib.windows.quol_window import QuolMainWindow, QuolSubWindow
from qlib.windows.tool_loader import ToolSpec
from lib.api import get_store_items, download_item, update_item
from lib.worker import Worker
from lib.notes import NotesWindow

logger = logging.getLogger(__name__)


class MainWindow(QuolMainWindow):
    def __init__(self, app, tool_spec: ToolSpec):
        super().__init__('Quol', tool_spec, default_geometry=(10, 10, 180, 1))

        self.app = app
        self.tools_dir = app.tools_dir
        self.settings_to_config()

        self.manager = QPushButton('Manage Tools')
        self.manager.clicked.connect(self.show_manage_tools)

        self.ver_icon = QIcon(tool_spec.path + '/res/img/code.svg')
        self.ver = QPushButton()
        self.ver.setIcon(self.ver_icon)
        self.ver.clicked.connect(self.open_url)

        self.msg_board = NotesWindow(self, tool_spec.settings.get('admin_key'))
        self.msg_board_icon = QIcon(tool_spec.path + '/res/img/news.svg')
        self.msg_board_btn = QPushButton()
        self.msg_board_btn.clicked.connect(self.on_msg_board)
        self.msg_board_btn.setIcon(self.msg_board_icon)

        self.folder_location_icon = QIcon(tool_spec.path + '/res/img/folder.svg')
        self.folder_location_btn = QPushButton()
        self.folder_location_btn.setIcon(self.folder_location_icon)
        self.folder_location_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(BASE_DIR)))

        self.reload_icon = QIcon(tool_spec.path + '/res/img/reload.svg')
        self.reload = QPushButton()
        self.reload.setIcon(self.reload_icon)
        self.reload.clicked.connect(self.app.reload)

        self.q = QPushButton('Quit')
        self.q.setStyleSheet('background-color: #c44; color: white;')
        self.q.clicked.connect(self.app.exit_app)

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.manager, 0, 0, 1, 3)
        self.grid_layout.addWidget(self.ver, 1, 0, 1, 1)
        self.grid_layout.addWidget(self.msg_board_btn, 1, 1, 1, 1)
        self.grid_layout.addWidget(self.folder_location_btn, 1, 2, 1, 1)
        self.grid_layout.addWidget(self.reload, 2, 0)
        self.grid_layout.addWidget(self.q, 2, 1, 1, 2)

        self.layout.addLayout(self.grid_layout)

        self.manage_tools_tool = None

        self.app_name = self.config['_']['name']
        self.app_path = self.get_app_path()

    def show_manage_tools(self):
        if self.manage_tools_tool is None:
            self.manage_tools_tool = ManageWindow(self)
        self.manage_tools_tool.show()

    def on_update_config(self):
        self.toggle_startup()
        self.config_to_settings()
        self.app.reload()

    def on_msg_board(self):
        self.msg_board.show()
        self.msg_board.raise_()
        self.msg_board.activateWindow()

    @staticmethod
    def open_url():
        QDesktopServices.openUrl(QUrl('https://github.com/LeoCh01/quol'))

    @staticmethod
    def get_app_path():
        return sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]

    def config_to_settings(self):
        self.app.settings['is_default_pos'] = self.config['reset_pos']
        self.app.settings['toggle_key'] = self.config['toggle_key']
        self.app.settings['transition'] = self.config['transition'][0][self.config['transition'][1]]
        self.app.settings['startup'] = self.config['startup']
        self.app.settings['tools'] = self.config['_']['tools']
        self.app.save_settings()

    def settings_to_config(self):
        self.config['reset_pos'] = self.app.settings['is_default_pos']
        self.config['toggle_key'] = self.app.settings['toggle_key']
        self.config['startup'] = self.app.settings['startup']
        self.config['_']['name'] = self.app.settings['name']
        self.config['_']['tools'] = self.app.settings['tools']

        self.tool_spec.save_config(self.config)

    def toggle_startup(self):
        if self.config['startup'] == self.app.settings['startup']:
            return

        if self.config['startup']:
            self.app.add_to_startup(self.app_name, self.app_path)
            logger.info(f'Added {self.app_name} to startup with path: {self.app_path}')
        else:
            self.app.remove_from_startup(self.app_name)
            logger.info(f'Removed {self.app_name} from startup')

    def closeEvent(self, event):
        super().closeEvent(event)
        if self.manage_tools_tool is not None:
            self.manage_tools_tool.close()


class ManageWindow(QuolSubWindow):
    def __init__(self, main_window):
        super().__init__(main_window, "Manage Tools")
        self.setGeometry(300, 300, 400, 400)
        self.tools_dir = main_window.tools_dir

        self.tabs = QTabWidget()
        self.installed_tab = QWidget()
        self.store_tab = QWidget()

        self.tabs.addTab(self.installed_tab, "Installed")
        self.tabs.addTab(self.store_tab, "Store")

        self.layout.addWidget(self.tabs)

        self.workers = []
        self.setup_installed_tab()
        self.setup_store_tab()

    def setup_installed_tab(self):
        self.installed_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        select_all_checkbox = QCheckBox(" Select All")
        select_all_checkbox.stateChanged.connect(self.on_update_checkbox_all)
        self.installed_layout.addWidget(select_all_checkbox)
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
        if not os.path.exists(self.tools_dir):
            os.makedirs(self.tools_dir)

        installed = [name for name in os.listdir(self.tools_dir) if os.path.isdir(os.path.join(self.tools_dir, name))]
        active = self.main_window.config['_']['tools']

        self.list_widget.clear()

        self.checkbox_list = []

        for tool in sorted(installed):
            config = read_json(os.path.join(self.tools_dir, tool, 'res/config.json'))
            version = config['_'].get('version', 0)
            display_name = f"{tool} (v{version})"

            item_widget = QWidget()
            layout = QHBoxLayout(item_widget)
            layout.setContentsMargins(5, 2, 5, 2)

            name_label = QLabel(display_name)
            status_label = QLabel("Active" if tool in active else "Inactive")
            checkbox = QCheckBox()
            checkbox.setChecked(tool in active)
            checkbox.stateChanged.connect(lambda s, t=tool, sl=status_label: self.on_update_checkbox(s, t, sl))
            self.checkbox_list.append(checkbox)

            layout.addWidget(name_label)
            layout.addStretch()
            layout.addWidget(status_label)
            layout.addWidget(checkbox)

            item = QListWidgetItem(self.list_widget)
            item.setSizeHint(QSize(0, 35))
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)

    def on_update_checkbox(self, checked, t, status_label):
        status_label.setText("Active" if checked else "Inactive")

        if checked and t not in self.main_window.config['_']['tools']:
            self.main_window.config['_']['tools'].append(t)
        elif not checked and t in self.main_window.config['_']['tools']:
            self.main_window.config['_']['tools'].remove(t)

        self.main_window.config_to_settings()

    def on_update_checkbox_all(self, state):
        for checkbox in self.checkbox_list:
            checkbox.setChecked(state == 2)

    def refresh_store_list(self):
        worker = Worker(get_store_items)
        self.workers.append(worker)

        def on_finished(store_items):
            self.store_list_widget.clear()

            installed = [name for name in os.listdir(self.tools_dir) if os.path.isdir(os.path.join(self.tools_dir, name))]

            for entry in sorted(store_items, key=lambda x: x['name']):
                raw_name = entry['name']
                if not raw_name.endswith('.zip'):
                    continue

                tool_and_ver = raw_name[:-4]  # Remove '.zip'

                if '--v' in tool_and_ver:
                    tool_name, version = tool_and_ver.rsplit('--v', 1)
                    version = int(version)
                else:
                    tool_name = tool_and_ver
                    version = 0

                is_installed = bool(tool_name in installed)
                is_matching_installed = False

                if is_installed:
                    config = read_json(os.path.join(self.tools_dir, str(tool_name), 'res/config.json'))
                    is_matching_installed = bool(version == config['_'].get('version', -1))

                item_widget = QWidget()
                layout = QHBoxLayout(item_widget)
                layout.setContentsMargins(5, 2, 5, 2)

                name_label = QLabel(f"{tool_name} (v{version})")

                if is_matching_installed:
                    status_label = QLabel("Installed")
                    status_label.setStyleSheet("color: #4CAF50;")
                    layout.addWidget(name_label)
                    layout.addStretch()
                    layout.addWidget(status_label)
                elif is_installed:
                    update_button = QPushButton("Update")
                    update_button.setStyleSheet("padding: 5px; color: yellow;")
                    update_button.clicked.connect(lambda _, name=tool_name, ver=version, b=update_button: self.on_update(name, ver, b))
                    layout.addWidget(name_label)
                    layout.addStretch()
                    layout.addWidget(update_button)
                else:
                    install_button = QPushButton("Install")
                    install_button.setStyleSheet("padding: 5px;")
                    install_button.clicked.connect(lambda _, name=tool_and_ver, b=install_button: self.on_install(name, b))

                    layout.addWidget(name_label)
                    layout.addStretch()
                    layout.addWidget(install_button)

                item = QListWidgetItem(self.store_list_widget)
                item.setSizeHint(QSize(0, 35))
                self.store_list_widget.addItem(item)
                self.store_list_widget.setItemWidget(item, item_widget)

        worker.finished.connect(on_finished)
        worker.error.connect(lambda e: logger.error(f"Error fetching store items: {e}"))
        worker.start()

    def on_install(self, name, button):
        button.setDisabled(True)
        button.setText("Installing...")

        worker = Worker(download_item, name, self.tools_dir)
        self.workers.append(worker)

        def on_finished(result):
            self.refresh_list()
            self.refresh_store_list()

        worker.finished.connect(on_finished)
        worker.error.connect(lambda e: logger.error(f"Error installing {name}: {e}"))
        worker.start()

    def on_update(self, name, ver, button):

        button.setDisabled(True)
        button.setText("Updating...")

        worker = Worker(update_item, name, ver, self.tools_dir)
        self.workers.append(worker)

        def on_finished(result):
            self.refresh_list()
            self.refresh_store_list()
            self.workers.remove(worker)

        worker.finished.connect(on_finished)
        worker.error.connect(lambda e: logger.error(f"Error updating {name}: {e}"))
        worker.start()
