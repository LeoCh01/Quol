from pynput import mouse
from PySide6.QtCore import QTimer, QSize
from PySide6.QtGui import QPixmap, QColor, QGuiApplication, QCursor, QPainter, Qt
from PySide6.QtWidgets import QLabel, QGroupBox, QGridLayout, QPushButton

from components.custom_window import CustomWindow


class ColorPicker(CustomWindow):

    def __init__(self, geometry):
        super().__init__("Color", geometry)

        self.grid_layout = QGridLayout()

        self.color_label = QLabel()
        self.grid_layout.addWidget(self.color_label, 0, 0)

        self.hex = QLabel()
        self.grid_layout.addWidget(self.hex, 0, 1)

        self.pixmap_label = QLabel()
        self.grid_layout.addWidget(self.pixmap_label, 1, 0, 2, 2)

        self.copy_btn = QPushButton("copy")
        self.copy_btn.clicked.connect(self.copy_color)
        self.grid_layout.addWidget(self.copy_btn, 0, 2)

        self.select_btn = QPushButton("pick color")
        self.select_btn.setCheckable(True)
        self.select_btn.clicked.connect(self.select_color)
        self.grid_layout.addWidget(self.select_btn, 1, 2)

        self.layout.addLayout(self.grid_layout)
        self.sf = QGuiApplication.primaryScreen().devicePixelRatio()
        self.timer = QTimer()
        self.update_color()

    def copy_color(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.hex.text())

    def select_color(self):
        self.timer.timeout.connect(self.update_color)
        self.timer.start(100)
        self.mouse_listener = mouse.Listener(win32_event_filter=self.on_click)
        self.mouse_listener.start()

    def on_click(self, msg, data):
        if msg == 513 and self.select_btn.isChecked():
            self.timer.stop()
            self.select_btn.setChecked(False)
            self.mouse_listener.stop()
            self.mouse_listener.suppress_event()

    def update_color(self):
        pos = QCursor.pos()
        screen = QGuiApplication.primaryScreen()

        pixmap = screen.grabWindow(0, pos.x() - 2.5 / self.sf, pos.y() - 2.5 / self.sf, 5 / self.sf, 5 / self.sf)
        image = pixmap.toImage()
        scaled_pixmap = QPixmap.fromImage(image).scaled(QSize(75 * self.sf, 75 * self.sf))

        self.draw_frame(scaled_pixmap)
        self.pixmap_label.setPixmap(scaled_pixmap)

        center_color = QColor(image.pixel(2, 2))  # The center of the 5x5 image
        self.hex.setText(center_color.name())

        self.color_label.setFixedSize(15, 15)
        self.color_label.setStyleSheet(f"background-color: {center_color.name()}; border: 1px solid black;")

    def draw_frame(self, pixmap):
        painter = QPainter(pixmap)
        pen = painter.pen()
        pen.setColor("white")
        pen.setWidth(2)
        painter.setPen(pen)

        cx = pixmap.width() / (self.sf * 2)
        cy = pixmap.height() / (self.sf * 2)
        sq = pixmap.width() / self.sf

        painter.drawRect(sq / 5 * 2, sq / 5 * 2, sq / 5 + 2, sq / 5 + 2)
        painter.drawRect(0, 0, sq, sq)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(cx, 0, cx, cx - sq / 10 - 1)
        painter.drawLine(0, cy, cy - sq / 10 - 1, cy)
        painter.drawLine(cx, sq, cx, cx + sq / 10 + 1)
        painter.drawLine(sq, cy, cy + sq / 10 + 1, cy)
        painter.end()
