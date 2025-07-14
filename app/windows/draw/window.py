import collections

from PySide6.QtGui import QColor, QMouseEvent, QPainter, Qt, QPixmap, QPen, QShortcut, QKeySequence, QCursor, \
    QPainterPath
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QWidget, QApplication, QSlider, QLabel, QVBoxLayout
from PySide6.QtCore import QPoint

from windows.custom_widgets import CustomWindow
from windows.draw.color_wheel import ColorWheel


class MainWindow(CustomWindow):
    def __init__(self, app, wid, geometry=(930, 10, 190, 1)):
        super().__init__('Draw', wid, geometry)

        self.drawing_widget = DrawingWidget(app.toggle_windows_2)

        self.top_layout = QHBoxLayout()
        self.layout.addLayout(self.top_layout)

        self.color_wheel = ColorWheel()
        self.color_wheel.color_changed.connect(self.drawing_widget.set_pen_color)
        self.top_layout.addWidget(self.color_wheel)

        self.control_layout = QVBoxLayout()

        self.clear_button = QPushButton('Clear')
        self.clear_button.clicked.connect(self.drawing_widget.clear_canvas)
        self.control_layout.addWidget(self.clear_button)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.on_start_clicked)
        self.control_layout.addWidget(self.start_button)
        self.drawing_widget.close_sc.activated.connect(self.on_start_clicked)

        self.stroke_slider = QSlider(Qt.Orientation.Horizontal)
        self.stroke_slider.setRange(1, 30)
        self.stroke_slider.setValue(2)
        self.stroke_slider.valueChanged.connect(self.update_stroke_size)
        self.stroke_label = QLabel("2")
        self.control_layout.addWidget(self.stroke_label)
        self.control_layout.addWidget(self.stroke_slider)

        self.top_layout.addLayout(self.control_layout)

    def on_start_clicked(self):
        if self.start_button.text() == 'Start':
            self.start_button.setText('Stop')
            self.drawing_widget.start_drawing()
        else:
            self.start_button.setText('Start')
            self.drawing_widget.stop_drawing()

    def update_stroke_size(self, value):
        # update text
        self.stroke_label.setText(f"{value}")
        self.drawing_widget.set_pen_width(value)


class DrawingWidget(QWidget):
    def __init__(self, toggle_windows_2):
        super().__init__()
        self.toggle_windows_2 = toggle_windows_2
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setFixedSize(screen_geometry.width(), screen_geometry.height() - 20)

        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor('red')
        self.pen_width = 2

        self.undo_stack = collections.deque(maxlen=30)

        self.undo_sc = QShortcut(QKeySequence('Ctrl+Z'), self)
        self.undo_sc.activated.connect(self.undo)
        self.close_sc = QShortcut(QKeySequence('Esc'), self)
        self.close_sc.activated.connect(self.hide)

        self.screenshot = QPixmap()
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

        self.strokes = []  # [(list of QPoint, QColor, width)]
        self.current_stroke = []

        self.eraser_mode = False
        self.eraser_multiplier = 3

        self.is_ctrl_pressed = False

    def mousePressEvent(self, event: QMouseEvent):
        point = event.position().toPoint()

        if event.button() == Qt.MouseButton.RightButton:
            self.eraser_mode = True
            self.erase_stroke_at(point)
            self.setCursor(QCursor(Qt.CursorShape.BlankCursor))
            self.update()
        elif event.button() == Qt.MouseButton.LeftButton:
            self.save_undo_state()
            self.drawing = True
            self.last_point = point
            self.current_stroke = [point]

    def mouseMoveEvent(self, event: QMouseEvent):
        point = event.position().toPoint()

        if self.drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            self.current_stroke.append(point)
            self.last_point = point
            self.update()
        elif event.buttons() & Qt.MouseButton.RightButton:
            self.erase_stroke_at(point)
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.drawing = False
            if len(self.current_stroke) > 1:
                self.strokes.append((list(self.current_stroke), self.pen_color, self.pen_width))
            self.current_stroke = []
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            self.eraser_mode = False
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.screenshot)

        for points, color, width in self.strokes:
            self.draw_path(painter, points, color, width)

        if len(self.current_stroke) > 1:
            self.draw_path(painter, self.current_stroke, self.pen_color, self.pen_width)

        if self.eraser_mode:
            self.draw_eraser_indicator(painter)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Control:
            self.is_ctrl_pressed = True

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Control:
            self.is_ctrl_pressed = False

    @staticmethod
    def draw_path(painter, points, color, width):
        path = QPainterPath()
        path.moveTo(points[0])
        for pt in points[1:]:
            path.lineTo(pt)

        pen = QPen(color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)

    def erase_stroke_at(self, pos: QPoint):
        for i in reversed(range(len(self.strokes))):
            points, _, width = self.strokes[i]
            for p in points:
                dx = p.x() - pos.x()
                dy = p.y() - pos.y()
                distance = (dx * dx + dy * dy) ** 0.5
                if distance <= width / 2 + (3 + self.pen_width ** 0.8) * self.eraser_multiplier:
                    self.save_undo_state()
                    del self.strokes[i]
                    self.update()
                    return

    def set_pen_color(self, color: QColor):
        self.pen_color = color
        self.update()

    def clear_canvas(self):
        self.undo_stack.clear()
        self.strokes.clear()
        self.update()

    def save_undo_state(self):
        self.undo_stack.append([(list(pts), QColor(col), w) for pts, col, w in self.strokes])

    def undo(self):
        if self.undo_stack:
            self.strokes = self.undo_stack.pop()
            self.update()

    def start_drawing(self):
        screen = QApplication.primaryScreen()
        g = screen.geometry()
        g2 = g.adjusted(0, 0, 0, -20)

        self.toggle_windows_2(True)
        self.screenshot = screen.grabWindow(0, g2.x(), g2.y(), g2.width(), g2.height())
        self.toggle_windows_2(False)

        self.current_stroke.clear()
        self.update()
        self.show()

    def stop_drawing(self):
        self.hide()

    def set_pen_width(self, width: int):
        self.pen_width = width
        self.update()

    def draw_eraser_indicator(self, painter: QPainter):
        eraser_size = (3 + self.pen_width ** 0.8) * self.eraser_multiplier
        pen = QPen(QColor(255, 255, 255), 1, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        cursor_pos = self.mapFromGlobal(QCursor.pos())
        painter.drawEllipse(cursor_pos, eraser_size, eraser_size)
