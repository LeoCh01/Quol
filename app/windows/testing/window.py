from PySide6.QtWidgets import QLabel, QPushButton

from windows.testing.tri import RainbowTriangleWidget
from windows.custom_widgets import CustomWindow


class MainWindow(CustomWindow):
    def __init__(self, app, wid, geometry=(300, 300, 100, 1)):
        super().__init__('Temp', wid, geometry)

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
