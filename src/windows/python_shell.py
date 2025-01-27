from PySide6 import QtCore
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QPushButton, QLabel, QGridLayout, QApplication
from PySide6.QtGui import QPixmap, Qt, QMovie
from components.custom_window import CustomWindow


class PythonShell(CustomWindow):
    def __init__(self, geometry, wid):
        super().__init__('Python', geometry, wid)
        self.grid_layout = QGridLayout()

