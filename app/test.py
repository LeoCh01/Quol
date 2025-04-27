import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QColorDialog
from PySide6.QtGui import QPainter, QPen, QMouseEvent, QColor, QPixmap
from PySide6.QtCore import Qt, QPoint

class DrawingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)
        self.setFixedSize(600, 400)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)  # Ensures the drawing is not cleared
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor("black")  # Default pen color is black
        self.pen_width = 2

        self.image = QPixmap(self.size())
        self.image.fill(Qt.transparent)  # Use transparent background for the pixmap

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
        self.image.fill(Qt.transparent)  # Clear to transparent background
        self.update()

    def change_pen_color(self):
        color = QColorDialog.getColor(self.pen_color, self)
        if color.isValid():
            self.pen_color = color

class DrawingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple PySide6 Drawing App")
        layout = QVBoxLayout()

        self.drawing_widget = DrawingWidget()
        layout.addWidget(self.drawing_widget)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.drawing_widget.clear_canvas)
        layout.addWidget(clear_button)

        color_button = QPushButton("Change Pen Color")
        color_button.clicked.connect(self.drawing_widget.change_pen_color)
        layout.addWidget(color_button)

        self.setLayout(layout)

        # Set the window opacity here (for the whole app window, not just the drawing widget)
        self.setWindowOpacity(1.0)  # Keep window fully opaque to prevent affecting drawing lines

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DrawingApp()
    window.show()
    sys.exit(app.exec())
