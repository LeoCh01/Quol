from qlib.windows.quol_window import QuolBaseWindow
from qlib.transitions.transition_loader import TransitionInfo
from qlib.transitions.move_transition import MoveTransition


class Transition(MoveTransition):
    def __init__(self, transition_info: TransitionInfo, window: QuolBaseWindow):
        super().__init__(transition_info, window, 'random')
