import json
import os
import sys

from PySide6.QtCore import QSettings, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QPushButton, QLabel, QGridLayout

from res.paths import SETTINGS_PATH
from windows.custom_widgets import CustomWindow

RUN_PATH = 'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'
BASE_PATH = os.path.dirname(__file__)


class MainWindow(CustomWindow):
    def __init__(self, wid, geometry=(10, 10, 180, 1)):
        super().__init__('Info', wid, geometry, path=BASE_PATH)
        self.settings_to_config()
        CustomWindow.toggle_direction = str(self.config['toggle_direction'])

        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
            version = settings['version']
        self.ver = QPushButton(f'v{version}')
        self.ver.clicked.connect(self.open_url)

        self.reload = QPushButton('Reload')
        self.reload.clicked.connect(self.reload_app)

        self.q = QPushButton('Quit')
        self.q.setStyleSheet('background-color: #c44; color: white;')
        self.q.clicked.connect(lambda _: sys.exit())

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.ver, 0, 0, 1, 2)
        self.grid_layout.addWidget(self.reload, 1, 0)
        self.grid_layout.addWidget(self.q, 1, 1)

        self.layout.addLayout(self.grid_layout)

        self.app_name = self.get_app_name()
        self.app_path = self.get_app_path()
        self.settings = QSettings(RUN_PATH, QSettings.Format.NativeFormat)

    def on_update_config(self):
        self.set_toggle_key(str(self.config['toggle_key']))
        CustomWindow.toggle_direction = str(self.config['toggle_direction'])
        self.toggle_startup()
        self.config_to_settings()

    @staticmethod
    def open_url():
        QDesktopServices.openUrl(QUrl('https://github.com/LeoCh01/quol'))

    @staticmethod
    def get_app_path():
        return sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]

    @staticmethod
    def get_app_name():
        return 'WindowsHelper'

    def config_to_settings(self):
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)

        settings['toggle_key'] = self.config['toggle_key']
        settings['startup'] = self.config['startup']
        settings['toggle_direction'] = self.config['toggle_direction']

        with open(SETTINGS_PATH, 'w') as f:
            json.dump(settings, f, indent=2)

    def settings_to_config(self):
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)

        self.config['toggle_key'] = settings['toggle_key']
        self.config['startup'] = settings['startup']
        self.config['toggle_direction'] = settings['toggle_direction']

        with open(BASE_PATH + '/config.json', 'w') as f:
            json.dump(self.config, f, indent=2)

    def toggle_startup(self):
        is_startup = self.config['startup']

        if is_startup:
            self.settings.setValue(self.app_name, self.app_path)
            print(f'Added {self.app_name} to startup with path: {self.app_path}')
        else:
            self.settings.remove(self.app_name)
            print(f'Removed {self.app_name} from startup')
