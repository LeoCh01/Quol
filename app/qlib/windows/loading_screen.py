from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)

        pixmap = QPixmap("res/icons/splash.png")
        label = QLabel(self)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setFixedSize(pixmap.size())
