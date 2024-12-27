import sys

import keyboard
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QPushButton, QLabel

from components.custom_window import CustomWindow
import json
from PySide6.QtWidgets import QGridLayout


class Info(CustomWindow):
    def __init__(self, geometry, set_toggle_key=None, key='`'):
        super().__init__('Info', geometry)

        self.grid_layout = QGridLayout()
        self.set_toggle_key = set_toggle_key

        self.ver = QPushButton(f'v{self.get_version(self)}')
        self.ver.clicked.connect(self.open_url)
        self.grid_layout.addWidget(self.ver, 0, 0, 1, 2)

        self.set_key = QPushButton('Edit Toggle Key')
        self.set_key.setCheckable(True)
        self.set_key.clicked.connect(self.select_key)
        self.grid_layout.addWidget(self.set_key, 1, 0)

        self.key_label = QLabel(' Key = ' + key)
        self.grid_layout.addWidget(self.key_label, 1, 1)

        self.startup = QPushButton('Startup App')
        self.startup.setCheckable(True)
        self.startup.clicked.connect(self.add_startup)
        self.grid_layout.addWidget(self.startup, 3, 0)

        self.q = QPushButton('Quit')
        self.q.clicked.connect(self.quit)
        self.grid_layout.addWidget(self.q, 3, 1)

        self.grid_layout.setColumnStretch(0, 3)
        self.grid_layout.setColumnStretch(1, 1)
        self.layout.addLayout(self.grid_layout)

    def select_key(self):
        def on_key_press(event):
            key = event.name
            self.set_key.setChecked(False)
            self.key_label.setText(f' Key = {key}')
            self.set_toggle_key(key)
            keyboard.unhook(self.key_hook)

        self.set_key.setChecked(True)
        self.set_key.setText('Press a key')
        self.key_hook = keyboard.on_press(on_key_press)

    @staticmethod
    def get_version(self):
        with open('res/settings.json', 'r') as file:
            data = json.load(file)
            version = data.get('version', 'xxx')
        return version

    @staticmethod
    def open_url(self):
        QDesktopServices.openUrl(QUrl('https://github.com/LeoCh01/windows-helper'))

    @staticmethod
    def quit(self):
        print('Quitting')
        sys.exit()

    def add_startup(self):
        if self.startup.isChecked():
            print('Adding to startup')
        else:
            print('Removing from startup')
