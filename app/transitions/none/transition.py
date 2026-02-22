from qlib.windows.quol_window import QuolBaseWindow
from qlib.transitions.quol_transition import QuolTransition
from qlib.transitions.transition_loader import TransitionInfo


class Transition(QuolTransition):
    def __init__(self, transition_info: TransitionInfo, window: QuolBaseWindow):
        super().__init__(transition_info, window)

    def enter(self):
        self.window.show()

    def exit(self):
        self.window.hide()
