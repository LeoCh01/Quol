import keyboard

from PySide6.QtCore import QTimer, QSize
from PySide6.QtGui import QPixmap, QColor, QGuiApplication, QCursor, QPainter
from PySide6.QtWidgets import QLabel, QGridLayout, QPushButton

from windows.custom_widgets import CustomWindow


class MainWindow(CustomWindow):
    def __init__(self, wid, geometry=(200, 10, 180, 1)):
        super().__init__('Color', wid, geometry)

        self.grid_layout = QGridLayout()

        self.color_label = QLabel()
        self.grid_layout.addWidget(self.color_label, 0, 0)

        self.hex = QLabel()
        self.grid_layout.addWidget(self.hex, 0, 1)

        self.pixmap_label = QLabel()
        self.grid_layout.addWidget(self.pixmap_label, 1, 0, 2, 2)

        self.copy_btn = QPushButton('copy')
        self.copy_btn.clicked.connect(self.copy_color)
        self.grid_layout.addWidget(self.copy_btn, 0, 2)

        self.select_btn = QPushButton('pick color')
        self.select_btn.setCheckable(True)
        self.select_btn.clicked.connect(self.select_color)
        self.grid_layout.addWidget(self.select_btn, 1, 2)

        self.layout.addLayout(self.grid_layout)
        self.sf = QGuiApplication.primaryScreen().devicePixelRatio()
        self.timer = QTimer()
        self.update_color()

    def close(self):
        super().close()

    def copy_color(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.hex.text())

    def select_color(self):
        self.select_btn.setText('Esc to stop')
        self.select_btn.setStyleSheet('background-color: #eee; color: #000')
        self.select_btn.setChecked(True)
        self.timer.timeout.connect(self.update_color)
        self.timer.start(100)
        keyboard.on_press_key('esc', lambda _: self.on_color_select())

    def on_color_select(self):
        keyboard.unhook_key('esc')
        self.timer.stop()
        self.select_btn.setText('pick color')
        self.select_btn.setStyleSheet('')
        self.select_btn.setChecked(False)

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
        self.color_label.setStyleSheet(f'background-color: {center_color.name()}; border: 1px solid black;')

    def draw_frame(self, pixmap):
        painter = QPainter(pixmap)
        pen = painter.pen()
        pen.setColor('white')
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
