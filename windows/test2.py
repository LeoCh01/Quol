from PySide6.QtWidgets import QMainWindow


class Test2(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("test2 Window")
        self.setGeometry(100, 100, 400, 300)
