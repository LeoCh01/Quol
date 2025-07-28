from PySide6.QtWidgets import QLabel, QPushButton

from lib.window_loader import WindowInfo, WindowContext
from windows.testing.tri import RainbowTriangleWidget
from lib.quol_window import QuolMainWindow


class MainWindow(QuolMainWindow):
    def __init__(self, window_info: WindowInfo, window_context: WindowContext):
        super().__init__('Temp', window_info, window_context, default_geometry=(300, 300, 100, 1))

        self.triangles = []
        self.tr = 0
        self.button = QPushButton('Create Triangle')
        self.button.clicked.connect(self.create_tri)
        self.layout.addWidget(self.button)
        self.dbutton = QPushButton('Delete Triangle')
        self.dbutton.clicked.connect(self.delete_tri)
        self.layout.addWidget(self.dbutton)

    def create_tri(self):
        if self.tr < len(self.triangles):
            self.triangles[self.tr].show()
        else:
            t = RainbowTriangleWidget()
            t.show()
            self.triangles.append(t)
        self.tr += 1

    def delete_tri(self):
        if self.tr > 0:
            self.tr -= 1
            triangle = self.triangles[self.tr]
            triangle.hide()
        else:
            label = QLabel("No triangles to delete.")
            label.setStyleSheet("color: red;")
            self.layout.addWidget(label)
