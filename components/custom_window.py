import json

from PySide6.QtCore import QPropertyAnimation, QPoint, QEasingCurve, Qt
from PySide6.QtGui import QPainterPath, QRegion, QColor, QPainter, QBrush
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QHBoxLayout, QLabel, QPushButton, QDialog
import random


class CustomWindow(QWidget):
    def __init__(self, title="Custom Window", geometry=(0, 0, 0, 0), wid=-1):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setGeometry(*geometry)
        self.geo = self.geometry()
        self.geo_old = self.geometry()
        self.first_run = True

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

        with open('res/settings.json', 'r') as f:
            settings = json.load(f)
            self.toggle_direction = settings.get('toggle_direction', 'random')

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setMask(self.generateRoundedMask())

    def generateRoundedMask(self):
        rect = self.rect()
        path = QPainterPath()
        radius = 6
        path.addRoundedRect(rect, radius, radius)
        return QRegion(path.toFillPolygon().toPolygon())

    def generatePosition(self):
        screen_geometry = self.screen().geometry()
        x = y = 0

        if self.toggle_direction == 'up':
            x = (screen_geometry.width() - self.geo.width()) // 2
            y = -self.geo.height()
        elif self.toggle_direction == 'down':
            x = (screen_geometry.width() - self.geo.width()) // 2
            y = screen_geometry.height()
        elif self.toggle_direction == 'left':
            x = -self.geo.width()
            y = (screen_geometry.height() - self.geo.height()) // 2
        elif self.toggle_direction == 'right':
            x = screen_geometry.width()
            y = (screen_geometry.height() - self.geo.height()) // 2
        else:
            side = random.randint(0, 1)
            if side:
                x = random.randint(0, screen_geometry.width() - self.geo.width())
                y = random.choice([-self.geo.height(), screen_geometry.height()])
            else:
                x = random.choice([-self.geo.width(), screen_geometry.width()])
                y = random.randint(0, screen_geometry.height() - self.geo.height())

        return QPoint(x, y)

    def toggle_windows(self, is_hidden):
        self.geometry_bugfix()
        self.animation = QPropertyAnimation(self, b"pos")
        start_pos = self.pos()

        end_pos = QPoint(self.geo.x(), self.geo.y()) if is_hidden else self.generatePosition()

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
        self.setFixedHeight(self.geo_old.height())

    def geometry_bugfix(self):
        if self.first_run:
            self.geo = self.geometry()
            self.geo_old = self.geometry()
            self.first_run = False


class CustomDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("content")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setMask(self.generateRoundedMask())

    def generateRoundedMask(self):
        rect = self.rect()
        path = QPainterPath()
        radius = 6
        path.addRoundedRect(rect, radius, radius)
        return QRegion(path.toFillPolygon().toPolygon())


class CustomTitleBar(QWidget):
    def __init__(self, title="Custom Title Bar", parent: CustomWindow = None):
        super().__init__(parent)
        self.parent = parent

        self.setObjectName("title-bar")
        self.bar_color_default = QColor("#222")
        self.bar_color = self.bar_color_default

        self.l1 = QHBoxLayout(self)

        self.title_label = QLabel(title)
        self.l1.addWidget(self.title_label, stretch=10)

        self.collapse_btn = QPushButton("▼")
        self.collapse_btn.clicked.connect(self.toggleCollapse)
        self.l1.addWidget(self.collapse_btn, stretch=1)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(self.bar_color))
        painter.drawRect(self.rect())

    def toggleCollapse(self):
        self.parent.geometry_bugfix()
        if self.collapse_btn.text() == "▼":
            self.collapse_btn.setText("▲")
            self.parent.hideContent()
        else:
            self.collapse_btn.setText("▼")
            self.parent.showContent()
        self.parent.geo = self.parent.geometry()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPosition().toPoint() - self.window().pos()
            self.bar_color = self.bar_color.darker(150)
            self.parent.setWindowOpacity(0.5)
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        self.bar_color = self.bar_color_default
        self.parent.setWindowOpacity(1)
        self.parent.geo = self.parent.geometry()
        self.update()

        # with open('res/settings.json', 'r') as f:
        #     settings = json.load(f)
