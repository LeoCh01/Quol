from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QBrush, QColor, QPen
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton


class CustomTitleBar(QWidget):
    def __init__(self, title="Custom Title Bar", parent=None):
        super().__init__(parent)
        self.parent = parent
        self.parent.setWindowFlags(Qt.FramelessWindowHint)

        self.setStyleSheet("QWidget {background-color: #333; color: white; font-size: 16px;}")

        self.l1 = QHBoxLayout(self)
        # self.l1.setContentsMargins(0, 0, 0, 0)
        # self.l1.setSpacing(0)

        self.title_label = QLabel(title)
        self.l1.addWidget(self.title_label)

        self.collapse_button = QPushButton("▼")
        self.collapse_button.clicked.connect(self.toggleCollapse)
        self.l1.addWidget(self.collapse_button)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(51, 51, 51)))
        painter.drawRect(self.rect())

    def toggleCollapse(self):
        if self.collapse_button.text() == "▼":
            self.collapse_button.setText("▲")
            self.hideContent()
        else:
            self.collapse_button.setText("▼")
            self.showContent()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPosition().toPoint() - self.window().pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self.offset)
            event.accept()

    def hideContent(self):
        # self.parent.w1.setVisible(False)
        title_bar_height = self.parent.title_bar.sizeHint().height()
        self.parent.setFixedHeight(title_bar_height)

    def showContent(self):
        # self.parent.w1.setVisible(True)
        self.parent.setFixedHeight(self.parent.original_geometry.height())