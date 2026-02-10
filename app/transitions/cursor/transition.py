from PySide6.QtCore import QPropertyAnimation, QByteArray, QEasingCurve, QPoint, QParallelAnimationGroup
from PySide6.QtGui import QCursor

from qlib.windows.quol_window import QuolBaseWindow
from qlib.transitions.quol_transition import QuolTransition
from qlib.transitions.transition_loader import TransitionInfo


class Transition(QuolTransition):
    def __init__(self, transition_info: TransitionInfo, window: QuolBaseWindow):
        super().__init__(transition_info, window)

        self.animation = QPropertyAnimation(self.window, QByteArray(b'pos'))
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.animation_2 = QPropertyAnimation(self.window, QByteArray(b'windowOpacity'))
        self.animation_2.setDuration(200)
        self.animation_2.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.animation)
        self.animation_group.addAnimation(self.animation_2)
        self.animation_group.finished.connect(self._on_animation_finished)

        self._hide_on_finish = False
        self.temp = None

    def _on_animation_finished(self):
        if self._hide_on_finish:
            self.window.hide()
            self._hide_on_finish = False

    def _get_cursor_point(self):
        return QCursor.pos() - QPoint(self.window.width() // 2, self.window.height() // 2)

    def enter(self):
        start_pos = self._get_cursor_point()
        if self.animation_group.state() == QPropertyAnimation.State.Running:
            self.animation_group.stop()

        self.window.show()
        self._hide_on_finish = False

        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(self.old_pos)
        self.window.setWindowOpacity(0.0)
        self.window.show()
        self.animation_2.setStartValue(0.0)
        self.animation_2.setEndValue(1.0)

        self.animation_group.start()

    def exit(self):
        end_pos = self._get_cursor_point()
        if self.animation_group.state() == QPropertyAnimation.State.Running:
            self.animation_group.stop()

        self._hide_on_finish = True

        self.animation.setStartValue(self.old_pos)
        self.animation.setEndValue(end_pos)
        self.animation_2.setStartValue(self.window.windowOpacity())
        self.animation_2.setEndValue(0.0)

        self.animation_group.start()
