from lib.quol_window import QuolBaseWindow
from shader_transition import ShaderTransition
from lib.io_helpers import read_text
from transition_plugin import TransitionPluginInfo


class Transition(ShaderTransition):
    def __init__(self, window_info: TransitionPluginInfo, window: QuolBaseWindow):
        super().__init__(window_info, window, read_text(window_info.path + '\\shader.vert'), read_text(window_info.path + '\\shader.frag'))