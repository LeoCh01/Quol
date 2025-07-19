from lib.quol_window import QuolBaseWindow
from lib.transition_loader import TransitionPluginInfo


class QuolTransition:
    def __init__(self, window_info: TransitionPluginInfo, window: QuolBaseWindow):
        self.window_info = window_info
        self.window = window

    def exit(self):
        pass

    def enter(self):
        pass
