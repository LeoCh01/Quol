from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QPushButton

from components.custom_window import CustomWindow


class Info(CustomWindow):
    def __init__(self, title, geometry):
        super().__init__(title, geometry)

        self.ver = QPushButton("Version 0.1")
        self.ver.clicked.connect(self.open_url)
        self.layout.addWidget(self.ver)

    def open_url(self):
        QDesktopServices.openUrl(QUrl("https://github.com/LeoCh01/windows-helper"))
