from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QBrush, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton


class CustomTitleBar(QWidget):
    def __init__(self, title="Custom Title Bar", parent=None):
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




