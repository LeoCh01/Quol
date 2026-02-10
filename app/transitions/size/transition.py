from PySide6.QtCore import QPropertyAnimation, QByteArray, QEasingCurve, QSize
from qlib.windows.quol_window import QuolBaseWindow
from qlib.transitions.quol_transition import QuolTransition
from qlib.transitions.transition_loader import TransitionInfo


class Transition(QuolTransition):
    def __init__(self, transition_info: TransitionInfo, window: QuolBaseWindow):
        super().__init__(transition_info, window)
        self.old_w = self.window.width()
        self.old_h = self.window.height()

        self.animation = QPropertyAnimation(self.window, QByteArray(b"size"))
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.finished.connect(self._on_animation_finished)

        self._hide_on_finish = False

    def _on_animation_finished(self):
        if self._hide_on_finish:
            self.window.hide()
            self._hide_on_finish = False

    def enter(self):
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()

        self._hide_on_finish = False
        self.window.show()

        self.animation.setStartValue(QSize(0, 0))
        self.animation.setEndValue(QSize(self.old_w, self.old_h))
        self.animation.start()

    def exit(self):
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()

        self._hide_on_finish = True
        self.animation.setStartValue(QSize(self.old_w, self.old_h))
        self.animation.setEndValue(QSize(0, 0))
        self.animation.start()
