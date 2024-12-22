from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QSizePolicy
from components.title_bar import CustomTitleBar  # Import custom title bar


class Test(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("test1 Window")
        self.setGeometry(100, 100, 400, 300)
        self.original_geometry = self.geometry()


        self.w1 = QWidget()
        self.w1.setStyleSheet("background-color: #a00; font-size: 8px;")
        self.l1 = QVBoxLayout(self.w1)
        self.l1.setContentsMargins(0, 0, 0, 0)
        self.l1.setSpacing(0)

        self.title_bar = CustomTitleBar("Custom Title Bar", self)
        self.l1.addWidget(self.title_bar)

        self.w2 = QWidget()
        self.w2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.w2.setStyleSheet("background-color: blue;")
        self.l1.addWidget(self.w2)

        self.w3 = QWidget()
        self.w3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.w3.setStyleSheet("background-color: green;")
        self.l1.addWidget(self.w3)

        self.setCentralWidget(self.w1)

