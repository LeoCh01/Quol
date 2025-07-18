from move_transition import MoveTransition
from quol_window import QuolBaseWindow
from transition_plugin import TransitionPluginInfo


class Transition(MoveTransition):
    def __init__(self, plugin_info: TransitionPluginInfo, window: QuolBaseWindow):
        super().__init__(plugin_info, window, 'random')