import math
import random

from PySide6.QtCore import Qt, QTimer, QPointF, QPoint
from PySide6.QtGui import QPainter, QColor, QPolygonF, QLinearGradient, QCursor, QGuiApplication
from PySide6.QtWidgets import QWidget


class RainbowTriangleWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rainbow Triangle")
        self.setGeometry(random.randint(0, QGuiApplication.primaryScreen().geometry().width() - 400),
                         random.randint(0, QGuiApplication.primaryScreen().geometry().height() - 400),
                         400, 400)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gradient)
        self.timer.start(10)

        self.gradient = self.create_gradient()

        self.angle = 0
        self.angle_speed = random.uniform(0.5, 4)
        self.angle_dir = random.choice([-1, 1])

        self.dragging = False
        self.prev_pos = None

    def create_gradient(self):
        """Create a gradient that will smoothly cycle through vibrant colors."""
        gradient = QLinearGradient(0, 0, 0, self.height())

        colors = [
            QColor(255, 0, 0),    # Red
            QColor(255, 165, 0),  # Orange
            QColor(255, 255, 0),  # Yellow
            QColor(0, 255, 0),    # Green
            QColor(0, 0, 255),    # Blue
            QColor(75, 0, 130)    # Indigo
        ]

        for i, color in enumerate(random.sample(colors, len(colors))):
            pos = i / (len(colors) - 1)
            gradient.setColorAt(pos, color)

        return gradient

    def update_gradient(self):
        """Update the gradient smoothly by shifting the colors."""
        stops = self.gradient.stops()

        # Shift colors by a small increment to make them move smoothly
        new_stops = []
        for i, (pos, color) in enumerate(stops):
            new_pos = (pos + 0.01) % 1.0  # Move each color stop by 1% along the gradient axis
            new_stops.append((new_pos, color))

        # Apply the new stops to the gradient
        self.gradient = QLinearGradient(0, 0, 0, self.height())
        for pos, color in new_stops:
            self.gradient.setColorAt(pos, color)

        # Trigger a repaint to update the triangle's gradient
        self.update()

    def paintEvent(self, event):
        """Override paint event to draw the rotating rainbow triangle with a dynamic gradient."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # move window
        if self.dragging:
            global_pos = QCursor.pos()
            self.move(global_pos.x() - 200, global_pos.y() - 200)

        # Define the triangle points
        width, height = self.width(), self.height()
        center = QPointF(width / 2, height / 2)

        size = min(width, height) / 10  # Reduce the size of the triangle
        points = [
            QPointF(center.x(), center.y() - size),  # Top vertex
            QPointF(center.x() - size * math.sqrt(3) / 2, center.y() + size / 2),  # Bottom-left vertex
            QPointF(center.x() + size * math.sqrt(3) / 2, center.y() + size / 2)   # Bottom-right vertex
        ]

        if self.prev_pos and self.dragging:
            # increase angle_vel
            dx = self.prev_pos.x() - QCursor.pos().x()
            dy = self.prev_pos.y() - QCursor.pos().y()
            self.angle_speed += abs(dx + dy) * 0.01
        self.prev_pos = QCursor.pos()

        # Apply rotation to the triangle points
        self.rotate_triangle(points, self.angle)
        self.angle += self.angle_speed * self.angle_dir
        self.angle_speed -= 0.01 * self.angle_speed

        # Draw the triangle with the gradient
        painter.setBrush(self.gradient)
        painter.setPen(Qt.NoPen)

        # Draw the triangle as a polygon
        triangle = QPolygonF(points)
        painter.drawPolygon(triangle)

    def rotate_triangle(self, points, angle):
        """Rotate the triangle points around the center"""
        radian_angle = math.radians(angle)
        cos_theta = math.cos(radian_angle)
        sin_theta = math.sin(radian_angle)

        # Rotate each point around the center
        for i in range(len(points)):
            x = points[i].x() - self.width() / 2
            y = points[i].y() - self.height() / 2
            new_x = cos_theta * x - sin_theta * y + self.width() / 2
            new_y = sin_theta * x + cos_theta * y + self.height() / 2
            points[i] = QPointF(new_x, new_y)

    def mousePressEvent(self, event):
        """Rotate the triangle when the mouse is clicked"""
        if event.button() == Qt.LeftButton:
            self.prev_pos = None
            self.dragging = True

    def mouseReleaseEvent(self, event):
        """Stop dragging when mouse is released"""
        if event.button() == Qt.LeftButton:
            self.dragging = False

