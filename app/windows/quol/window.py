import sys

from PySide6.QtCore import QSettings, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QPushButton, QGridLayout

from lib.io_helpers import write_json
from lib.quol_window import QuolMainWindow
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

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.ver, 0, 0, 1, 2)
        self.grid_layout.addWidget(self.reload, 1, 0)
        self.grid_layout.addWidget(self.q, 1, 1)

        self.layout.addLayout(self.grid_layout)

        self.app_name = self.get_app_name()
        self.app_path = self.get_app_path()
        self.settings = QSettings(RUN_PATH, QSettings.Format.NativeFormat)

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

    @staticmethod
    def get_app_name():
        return 'Quol'

    def config_to_settings(self):
        self.app.settings['toggle_key'] = self.config['toggle_key']
        self.app.settings['transition'] = self.config['transition']
        self.app.settings['startup'] = self.config['startup']
        self.app.save_settings()

    def settings_to_config(self):
        self.config['toggle_key'] = self.app.settings['toggle_key']
        self.config['transition'] = self.app.settings['transition']
        self.config['startup'] = self.app.settings['startup']

        write_json(self.window_info.config_path, self.config)

    def toggle_startup(self):
        is_startup = self.config['startup']

        if is_startup:
            self.settings.setValue(self.app_name, self.app_path)
            print(f'Added {self.app_name} to startup with path: {self.app_path}')
        else:
            self.settings.remove(self.app_name)
            print(f'Removed {self.app_name} from startup')

