from PySide6.QtWidgets import QLabel

from res.paths import RES_PATH
from windows.lib.custom_widgets import CustomWindow


class MainWindow(CustomWindow):
    """
    MainWindow class that inherits from CustomWindow.

    This class represents a window with two QLabel widgets.
    """

    def __init__(self, wid, geometry=(0, 0, 100, 1)):
        """
        Initialize a window at the top left of the screen.

        Args:
            wid (int): The window ID. (can ignore)
            geometry (tuple): A tuple containing the geometry of the window (x, y, width, height).
        """
        super().__init__('Temp', wid, geometry)

        self.layout.addWidget(QLabel('Temp'))
        self.layout.addWidget(QLabel('Hello'))
