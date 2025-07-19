import random

from PySide6.QtCore import QPoint, QByteArray, QEasingCurve, QPropertyAnimation

from lib.quol_window import QuolBaseWindow
from lib.quol_transition import QuolTransition
from lib.transition_loader import TransitionPluginInfo


class MoveTransition(QuolTransition):
    def __init__(self, window_info: TransitionPluginInfo, window: QuolBaseWindow, direction: str):
        super().__init__(window_info, window)
        self.direction = direction
        self.animation = QPropertyAnimation(self.window, QByteArray(b'pos'))
        self.old_pos = self.window.pos()

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

    def exit(self):
        end_pos = self.generate_pos()
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()

        self.animation.setStartValue(self.old_pos)
        self.animation.setEndValue(end_pos)
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()

    def enter(self):
        start_pos = self.window.pos()
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()

        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(self.old_pos)
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()


class Transition(MoveTransition):
    def __init__(self, window_info: TransitionPluginInfo, window: QuolBaseWindow):
        super().__init__(window_info, window, 'random')
