from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QBrush, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton


class CustomTitleBar(QWidget):
    def __init__(self, title="Custom Title Bar", parent=None):
        super().__init__(parent)
        self.parent = parent
        self.parent.setWindowFlags(Qt.FramelessWindowHint)

        self.setObjectName("title-bar")
        self.bar_color = QColor("#222")

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
        if self.collapse_btn.text() == "▼":
            self.collapse_btn.setText("▲")
            self.hideContent()
        else:
            self.collapse_btn.setText("▼")
            self.showContent()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPosition().toPoint() - self.window().pos()
            self.bar_color = QColor("#111")
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        self.bar_color = QColor("#222")
        self.parent.geo = self.parent.geometry()
        self.update()

    def hideContent(self):
        title_bar_height = self.parent.title_bar.sizeHint().height()
        self.parent.setFixedHeight(title_bar_height)

    def showContent(self):
        self.parent.setFixedHeight(self.parent.geo.height())


