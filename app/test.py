import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PySide6.QtGui import QPainter, QPen, QMouseEvent, QColor, QPixmap
from PySide6.QtCore import Qt, QPoint

class DrawingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)
        self.setFixedSize(600, 400)
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor("black")
        self.pen_width = 2

        self.image = QPixmap(self.size())
        self.image.fill(Qt.white)

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
        self.image.fill(Qt.white)
        self.update()

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

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DrawingApp()
    window.show()
    sys.exit(app.exec())
