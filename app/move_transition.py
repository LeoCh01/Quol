import random

from PySide6.QtCore import QPoint, QByteArray, QEasingCurve, QPropertyAnimation

from quol_window import QuolBaseWindow
from transition import Transition
from transition_plugin import TransitionPluginInfo


class MoveTransition(Transition):
    def __init__(self, plugin_info: TransitionPluginInfo, window: QuolBaseWindow, direction: str):
        super().__init__(plugin_info, window)
        self.direction = direction
        self.animation = QPropertyAnimation(self.window, QByteArray(b'pos'))
        self.old_pos = None

    def generate_pos(self):
        screen_geometry = self.window.screen().geometry()

        if self.direction == 'up':
            x = (screen_geometry.width() - self.window.width()) // 2
            y = -self.window.geometry().height()
        elif self.direction == 'down':
            x = (screen_geometry.width() - self.window.width()) // 2
            y = screen_geometry.height()
        elif self.direction == 'left':
            x = -self.window.width()
            y = (screen_geometry.height() - self.window.height()) // 2
        elif self.direction == 'right':
            x = screen_geometry.width()
            y = (screen_geometry.height() - self.window.height()) // 2
        else:
            side = random.randint(0, 1)
            if side:
                x = random.randint(0, screen_geometry.width() - self.window.width())
                y = random.choice([-self.window.height(), screen_geometry.height()])
            else:
                x = random.choice([-self.window.width(), screen_geometry.width()])
                y = random.randint(0, screen_geometry.height() - self.window.height())

        return QPoint(x, y)

    def begin(self):
        start_pos = self.window.pos()
        end_pos = self.generate_pos()

        self.old_pos = start_pos

        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()

    def end(self):
        start_pos = self.window.pos()
        end_pos = self.old_pos

        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()