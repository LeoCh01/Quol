from qlib.quol_window import QuolBaseWindow
from transitions.shader_transition import ShaderTransition
from qlib.io_helpers import read_text
from qlib.transition_loader import TransitionInfo


class Transition(ShaderTransition):
    def __init__(self, transition_info: TransitionInfo, window: QuolBaseWindow):
        super().__init__(transition_info, window, read_text(transition_info.path + '\\shader.vert'), read_text(transition_info.path + '\\shader.frag'))