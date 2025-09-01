from lib.quol_window import QuolBaseWindow
from lib.transition_loader import TransitionInfo
from lib.move_transition import MoveTransition


class Transition(MoveTransition):
    def __init__(self, transition_info: TransitionInfo, window: QuolBaseWindow):
        super().__init__(transition_info, window, 'left')
