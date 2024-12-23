from PySide6.QtCore import QPropertyAnimation, QPoint, QEasingCurve
from PySide6.QtGui import QPainterPath, QRegion
from PySide6.QtWidgets import QWidget, QVBoxLayout

from components.title_bar import CustomTitleBar


class CustomWindow(QWidget):
    def __init__(self, title="Custom Window"):
        super().__init__()

        self.l1 = QVBoxLayout(self)
        self.l1.setContentsMargins(0, 0, 0, 0)
        self.l1.setSpacing(0)

        self.title_bar = CustomTitleBar(title, self)
        self.l1.addWidget(self.title_bar)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setMask(self.generateRoundedMask())

    def generateRoundedMask(self):
        rect = self.rect()
        path = QPainterPath()
        radius = 10
        path.addRoundedRect(rect, radius, radius)
        return QRegion(path.toFillPolygon().toPolygon())

    def toggle_windows(self, is_hidden):
        self.animation = QPropertyAnimation(self, b"pos")
        start_pos = self.pos()
        end_pos = QPoint(self.geo.x(), self.geo.y() if is_hidden else 0 - self.geo.height())

        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()
