import sys

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QPushButton, QHBoxLayout

from components.custom_window import CustomWindow
import json


class Info(CustomWindow):
    def __init__(self, title, geometry):
        super().__init__(title, geometry)

        self.ver = QPushButton(f"v{self.get_version(self)}")
        self.ver.clicked.connect(self.open_url)
        self.layout.addWidget(self.ver)

        self.startup = QPushButton("Startup App")
        self.startup.setCheckable(True)
        self.startup.clicked.connect(self.add_startup)

        self.q = QPushButton("Quit")
        self.q.clicked.connect(self.quit)

        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.startup, stretch=2)
        self.h_layout.addWidget(self.q , stretch=1)
        self.layout.addLayout(self.h_layout)

    @staticmethod
    def get_version(self):
        with open('res/settings.json', 'r') as file:
            data = json.load(file)
            version = data.get('version', 'xxx')
        return version

    @staticmethod
    def open_url(self):
        QDesktopServices.openUrl(QUrl("https://github.com/LeoCh01/windows-helper"))

    @staticmethod
    def quit(self):
        print("Quitting")
        sys.exit()

    def add_startup(self):
        if self.startup.isChecked():
            print("Adding to startup")
        else:
            print("Removing from startup")
