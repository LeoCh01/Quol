from quol_window import QuolBaseWindow
from transition_plugin import TransitionPluginInfo


class Transition:
    def __init__(self, plugin_info: TransitionPluginInfo, window: QuolBaseWindow):
        self.plugin_info = plugin_info
        self.window = window

    def begin(self):
        pass

    def end(self):
        pass