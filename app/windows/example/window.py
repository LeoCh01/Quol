import os

from PySide6.QtWidgets import QLabel

from windows.custom_widgets import CustomWindow

BASE_PATH = os.path.dirname(__file__)


class MainWindow(CustomWindow):
    """
    MainWindow class that inherits from CustomWindow.

    This class represents a window with two QLabel widgets.
    """

    def __init__(self, parent, wid, geometry=(300, 300, 100, 1)):
        super().__init__('Temp', wid, geometry, path=BASE_PATH)

        # self.layout is the main layout of the window
        self.layout.addWidget(QLabel('Hello'))

        # self.config is a dictionary containing data in config.json
        self.number = QLabel(str(self.config['test']))
        self.layout.addWidget(self.number)

    def on_update_config(self):
        # This method is called when the config is updated.
        self.number.setText(str(self.config['test']))
