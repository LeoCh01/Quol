from PySide6.QtWidgets import QWidget, QSizePolicy

from components.custom_window import CustomWindow


class Test(CustomWindow):
    def __init__(self):
        super().__init__("Test Window")

        self.setGeometry(20, 20, 200, 200)
        self.geo = self.geometry()

        self.w1 = QWidget()
        self.w1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.w1.setStyleSheet("background-color: #444;")
        self.l1.addWidget(self.w1)
