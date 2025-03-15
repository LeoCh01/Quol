from PySide6.QtWidgets import QLabel

from res.paths import RES_PATH
from windows.lib.custom_widgets import CustomWindow


class MainWindow(CustomWindow):

    def __init__(self, wid, geometry=(0, 0, 100, 1)):
        super().__init__('Chat', wid, geometry)

        self.layout.addWidget(QLabel('Temp'))
        self.layout.addWidget(QLabel('Hello'))
