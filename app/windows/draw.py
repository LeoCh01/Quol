from PySide6.QtGui import QColor, QMouseEvent, QPainter, Qt, QPixmap, QPen, QShortcut, QKeySequence
from PySide6.QtWidgets import QPushButton, QColorDialog, QHBoxLayout, QWidget, QApplication
from PySide6.QtCore import QPoint

from res.paths import IMG_PATH
from windows.lib.custom_widgets import CustomWindow


class MainWindow(CustomWindow):
    def __init__(self, wid, geometry=(730, 10, 150, 1)):
        super().__init__('Draw', wid, geometry)

        self.drawing_widget = DrawingWidget(self.toggle_windows_2)

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
            self.drawing_widget.start_drawing()
        else:
            self.start_button.setText("Start")
            self.drawing_widget.stop_drawing()


class DrawingWidget(QWidget):
    def __init__(self, toggle_windows_2):
        super().__init__()
        self.toggle_windows_2 = toggle_windows_2
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)
        self.setWindowFlags(Qt.FramelessWindowHint)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setFixedSize(screen_geometry.width(), screen_geometry.height() - 20)

        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor("red")
        self.pen_width = 2

        self.image = QPixmap(self.size())

        self.undo_stack = []
        self.max_undo = 20

        self.undo_sc = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.undo_sc.activated.connect(self.undo)
        self.close_sc = QShortcut(QKeySequence("Esc"), self)
        self.close_sc.activated.connect(self.hide)

        self.screenshot = QPixmap()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.save_undo_state()
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
        self.save_undo_state()
        painter = QPainter(self.image)
        painter.drawPixmap(0, 0, self.screenshot)
        self.update()

    def change_pen_color(self):
        color = QColorDialog.getColor(self.pen_color, self)
        if color.isValid():
            self.pen_color = color

    def save_undo_state(self):
        if len(self.undo_stack) >= self.max_undo:
            self.undo_stack.pop(0)
        self.undo_stack.append(self.image.copy())

    def undo(self):
        if self.undo_stack:
            self.image = self.undo_stack.pop()
            self.update()

    def start_drawing(self):
        screen = QApplication.primaryScreen()
        g = screen.geometry()
        g2 = g.adjusted(0, 0, 0, -20)

        self.toggle_windows_2(True)
        self.screenshot = screen.grabWindow(0, g2.x(), g2.y(), g2.width(), g2.height())
        self.toggle_windows_2(False)

        pixmap = self.screenshot.scaled(self.size() * screen.devicePixelRatio())
        self.image = pixmap.copy()

        painter = QPainter(self.image)
        painter.drawPixmap(0, 0, self.screenshot)
        self.update()
        self.show()

    def stop_drawing(self):
        self.hide()
