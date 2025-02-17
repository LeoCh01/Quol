from PySide6.QtWidgets import QLabel

from src.windows.custom_window import CustomWindow


class MainWindow(CustomWindow):
    def __init__(self, wid, geometry=(0, 0, 0, 0)):
        super().__init__('Temp', wid, geometry)
        self.layout.addWidget(QLabel('Temp'))