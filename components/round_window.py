from PySide6.QtGui import QPainterPath, QRegion
from PySide6.QtWidgets import QMainWindow


class RoundWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 250, 400)
        self.original_geometry = self.geometry()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setMask(self.generateRoundedMask())

    def generateRoundedMask(self):
        rect = self.rect()
        path = QPainterPath()
        radius = 10
        path.addRoundedRect(rect, radius, radius)
        return QRegion(path.toFillPolygon().toPolygon())