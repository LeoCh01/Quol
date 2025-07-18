from quol_window import QuolBaseWindow
from shader_transition import ShaderTransition
from io_helpers import read_text
from transition_plugin import TransitionPluginInfo


class Transition(ShaderTransition):
    def __init__(self, plugin_info: TransitionPluginInfo, window: QuolBaseWindow):
        super().__init__(plugin_info, window, read_text(plugin_info.path + '\\shader.vert'), read_text(plugin_info.path + '\\shader.frag'))