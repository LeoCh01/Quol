from lib.quol_window import QuolBaseWindow
from lib.transition_loader import TransitionInfo


class QuolTransition:
    def __init__(self, transition_info: TransitionInfo, window: QuolBaseWindow):
        self.transition_info = transition_info
        self.window = window
        self.old_pos = window.pos()

    def exit(self):
        pass

    def enter(self):
        pass
