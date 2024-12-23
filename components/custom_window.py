from PySide6.QtCore import QPropertyAnimation, QPoint, QEasingCurve, Qt
from PySide6.QtGui import QPainterPath, QRegion
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

from components.title_bar import CustomTitleBar


class CustomWindow(QWidget):
    def __init__(self, title="Custom Window", geometry=(20, 20, 200, 200)):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

        self.setGeometry(*geometry)
        self.geo = self.geometry()
        self.init_geo = self.geometry()

        self.l1 = QVBoxLayout(self)
        self.l1.setContentsMargins(0, 0, 0, 0)
        self.l1.setSpacing(0)

        self.title_bar = CustomTitleBar(title, self)
        self.l1.addWidget(self.title_bar)

        self.w1 = QWidget()
        self.w1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.w1.setObjectName("content")
        self.l1.addWidget(self.w1)

        self.layout = QVBoxLayout(self.w1)
        self.layout.setAlignment(Qt.AlignTop)


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
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def hideContent(self):
        title_bar_height = self.title_bar.sizeHint().height()
        self.w1.hide()
        self.setFixedHeight(title_bar_height)

    def showContent(self):
        self.w1.show()
        self.setFixedHeight(self.init_geo.height())
