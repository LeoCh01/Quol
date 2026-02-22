from PySide6.QtWidgets import QLabel

from qlib.windows.quol_window import QuolMainWindow
from qlib.windows.tool_loader import ToolSpec
from lib.adder import op_to_str


class MainWindow(QuolMainWindow):
    """
    MainWindow class that inherits from QuolMainWindow.

    This class represents a window displaying basic arithmetic and last key pressed.
    """

    def __init__(self, tool_spec: ToolSpec):
        super().__init__('Temp', tool_spec, default_geometry=(500, 500, 100, 1))

        # self.layout is the main layout of the window
        self.layout.addWidget(QLabel('Hello'))

        # self.config is a dictionary containing data in config.json
        self.number = QLabel(op_to_str(self.config['a'], self.config['b'], self.config['op'][0][self.config['op'][1]]))
        self.layout.addWidget(self.number)

        # input_manager allows listening to keyboard and mouse events
        self.key_label = QLabel("Last Key: None")
        self.layout.addWidget(self.key_label)
        self.tool_spec.input_manager.add_key_press_listener(self.on_key_press)

    def on_update_config(self):
        # This method is called when the config is updated.
        self.number.setText(op_to_str(self.config['a'], self.config['b'], self.config['op'][0][self.config['op'][1]]))

    def on_key_press(self, key):
        try:
            self.key_label.setText(f"Last Key: {key.char}")
        except AttributeError:
            self.key_label.setText(f"Last Key: {key}")