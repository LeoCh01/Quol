import sys

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QPushButton, QSizePolicy

from components.custom_window import CustomWindow


class Info(CustomWindow):
    def __init__(self, title, geometry):
        super().__init__(title, geometry)

        self.ver = QPushButton("Version 0.1")
        self.ver.clicked.connect(self.open_url)
        self.layout.addWidget(self.ver)

        self.q = QPushButton("Quit")
        self.q.clicked.connect(self.quit)
        self.layout.addWidget(self.q)

    @staticmethod
    def open_url(self):
        QDesktopServices.openUrl(QUrl("https://github.com/LeoCh01/windows-helper"))

    @staticmethod
    def quit(self):
        print("Quitting")
        sys.exit()
