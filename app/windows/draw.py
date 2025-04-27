from PySide6.QtGui import QColor, QMouseEvent, QPainter, Qt, QPixmap, QPen
from PySide6.QtWidgets import QPushButton, QColorDialog, QHBoxLayout, QWidget, QApplication
from PySide6.QtCore import QPoint

from windows.lib.custom_widgets import CustomWindow


class MainWindow(CustomWindow):
    def __init__(self, wid, geometry=(730, 10, 150, 1)):
        super().__init__('Draw', wid, geometry)

        self.drawing_widget = DrawingWidget()

        self.color_button = QPushButton("Color")
        self.color_button.clicked.connect(self.drawing_widget.change_pen_color)
        self.layout.addWidget(self.color_button)
        self.color_picker = QColorDialog()

        self.button_layout = QHBoxLayout()

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.drawing_widget.clear_canvas)
        self.button_layout.addWidget(self.clear_button)

        self.start_button = QPushButton("Start")
        self.button_layout.addWidget(self.start_button)
        self.start_button.clicked.connect(self.on_start_clicked)

        self.layout.addLayout(self.button_layout)

    def on_start_clicked(self):
        if self.start_button.text() == "Start":
            self.start_button.setText("Stop")
            self.drawing_widget.show()
        else:
            self.start_button.setText("Start")
            self.drawing_widget.hide()


class DrawingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)
        self.setWindowFlags(Qt.FramelessWindowHint)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setFixedSize(screen_geometry.width(), screen_geometry.height())
        self.setWindowOpacity(0.3)

        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor("red")
        self.pen_width = 2

        self.image = QPixmap(self.size())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            painter = QPainter(self.image)
            pen = QPen(self.pen_color, self.pen_width, Qt.SolidLine)
            painter.setPen(pen)
            current_point = event.position().toPoint()
            painter.drawLine(self.last_point, current_point)
            self.last_point = current_point
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        canvas_painter = QPainter(self)
        canvas_painter.drawPixmap(self.rect(), self.image)

    def clear_canvas(self):
        self.image.fill(Qt.black)
        self.update()

    def change_pen_color(self):
        color = QColorDialog.getColor(self.pen_color, self)
        if color.isValid():
            self.pen_color = color
