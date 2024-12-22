from PySide6.QtWidgets import QVBoxLayout, QWidget, QSizePolicy

from components.round_window import RoundWindow
from components.title_bar import CustomTitleBar


class Test2(RoundWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(500, 200, 250, 400)
        self.original_geometry = self.geometry()

        self.w1 = QWidget()
        self.l1 = QVBoxLayout(self.w1)
        self.l1.setContentsMargins(0, 0, 0, 0)
        self.l1.setSpacing(0)

        self.title_bar = CustomTitleBar("Custom Title Bar", self)
        self.l1.addWidget(self.title_bar)

        self.w2 = QWidget()
        self.w2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.w2.setStyleSheet("background-color: #444;")
        self.l1.addWidget(self.w2)

        self.setCentralWidget(self.w1)
