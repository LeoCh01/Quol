from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtGui import QScreen, QPixmap, QColor, QGuiApplication, QCursor
from PySide6.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QGridLayout, QWidget

from components.custom_window import CustomWindow


class ColorPicker(CustomWindow):
    def __init__(self, geometry):
        super().__init__("Color Picker", geometry)

        self.box = QGroupBox()
        self.layout.addWidget(self.box)

        self.box_layout = QVBoxLayout(self.box)

        self.label = QLabel("Color: ")
        self.box_layout.addWidget(self.label)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(3)
        self.box_layout.addLayout(self.grid_layout)

        self.color_displays = []
        for i in range(7):
            row = []
            for j in range(7):
                color_display = QLabel()
                color_display.setFixedSize(20, 20)
                self.grid_layout.addWidget(color_display, i, j)
                row.append(color_display)
            self.color_displays.append(row)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_color)
        self.timer.start(100)

    def update_color(self):
        pos = QCursor.pos()
        screen = QGuiApplication.primaryScreen()
        pixmap = screen.grabWindow(0, pos.x() - 3, pos.y() - 3, 7, 7)
        image = pixmap.toImage()

        for i in range(7):
            for j in range(7):
                color = QColor(image.pixel(j, i))
                self.color_displays[i][j].setStyleSheet(f"background-color: {color.name()};")

        center_color = QColor(image.pixel(3, 3))
        self.label.setText(f"Color: {center_color.name()}")
