from PySide6.QtWidgets import QLabel

from quol_window import QuolMainWindow
from window_plugin import WindowPluginInfo, WindowPluginContext

class MainWindow(QuolMainWindow):
    """
    MainWindow class that inherits from CustomWindow.

    This class represents a window with two QLabel widgets.
    """

    def __init__(self, plugin_info: WindowPluginInfo, plugin_context: WindowPluginContext):
        super().__init__('Temp', plugin_info, plugin_context, default_geometry=(300, 300, 100, 1))

        # self.layout is the main layout of the window
        self.layout.addWidget(QLabel('Hello'))

        # self.config is a dictionary containing data in config.json
        self.number = QLabel(str(self.config['test']))
        self.layout.addWidget(self.number)

    def on_update_config(self):
        # This method is called when the config is updated.
        self.number.setText(str(self.config['test']))
