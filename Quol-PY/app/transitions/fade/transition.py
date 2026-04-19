from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QByteArray
from qlib.windows.quol_window import QuolBaseWindow
from qlib.transitions.quol_transition import QuolTransition
from qlib.transitions.transition_loader import TransitionInfo


class Transition(QuolTransition):
    def __init__(self, transition_info: TransitionInfo, window: QuolBaseWindow):
        super().__init__(transition_info, window)

        self.animation = QPropertyAnimation(self.window, QByteArray(b'windowOpacity'))
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.finished.connect(self._on_animation_finished)

        self._hide_on_finish = False

    def _on_animation_finished(self):
        if self._hide_on_finish:
            self.window.hide()
            self._hide_on_finish = False

    def enter(self):
        if self.animation.state() == QPropertyAnimation.Running:
            self.animation.stop()

        self._hide_on_finish = False

        self.window.setWindowOpacity(0.0)
        self.window.show()

        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

    def exit(self):
        if self.animation.state() == QPropertyAnimation.Running:
            self.animation.stop()

        self._hide_on_finish = True

        self.animation.setStartValue(self.window.windowOpacity())
        self.animation.setEndValue(0.0)
        self.animation.start()
