from pynput import mouse
from PySide6.QtCore import QTimer, QSize
from PySide6.QtGui import QPixmap, QColor, QGuiApplication, QCursor, QPainter
from PySide6.QtWidgets import QLabel, QGroupBox, QGridLayout, QPushButton

from components.custom_window import CustomWindow


class ColorPicker(CustomWindow):
    s = 3

    def __init__(self, geometry):
        super().__init__("Color", geometry)
        self.box = QGroupBox()
        self.layout.addWidget(self.box)

        self.box_layout = QGridLayout(self.box)

        self.color_label = QLabel()
        self.box_layout.addWidget(self.color_label, 0, 0)

        self.hex = QLabel()
        self.box_layout.addWidget(self.hex, 0, 1)

        self.pixmap_label = QLabel()
        self.box_layout.addWidget(self.pixmap_label, 1, 0, 2, 2)

        self.copy_btn = QPushButton("copy")
        self.copy_btn.clicked.connect(self.copy_color)
        self.box_layout.addWidget(self.copy_btn, 0, 2)

        self.select_btn = QPushButton("pick color")
        self.select_btn.setCheckable(True)
        self.select_btn.clicked.connect(self.select_color)
        self.box_layout.addWidget(self.select_btn, 1, 2)

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
        pixmap = screen.grabWindow(0, pos.x() - self.s, pos.y() - self.s, self.s, self.s)
        image = pixmap.toImage()
        scaled_pixmap = QPixmap.fromImage(image).scaled(QSize(100, 100))

        self.draw_frame(scaled_pixmap)
        self.pixmap_label.setPixmap(scaled_pixmap)

        center_color = QColor(image.pixel(self.s - 1, self.s - 1))
        self.hex.setText(center_color.name())
        self.color_label.setFixedSize(15, 15)
        self.color_label.setStyleSheet(f"background-color: {center_color.name()}; border: 1px solid black;")

    def draw_frame(self, pixmap):
        painter = QPainter(pixmap)
        pen = painter.pen()
        pen.setColor("white")
        pen.setWidth(2)
        painter.setPen(pen)

        cx = pixmap.width() // 3
        cy = pixmap.height() // 3
        sq = pixmap.width() // (self.s * 3)
        painter.drawRect(cx - sq // 2, cy - sq // 2, sq, sq)
        painter.drawRect(0, 0, cx * 2, cy * 2)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(cx, cy - sq // 2, cx, 0)
        painter.drawLine(cx, cy + sq // 2 + 1, cx, pixmap.height())
        painter.drawLine(cx - sq // 2, cy, 0, cy)
        painter.drawLine(cx + sq // 2 + 1, cy, pixmap.width(), cy)
        painter.end()
