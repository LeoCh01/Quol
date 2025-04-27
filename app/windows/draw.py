from PySide6.QtWidgets import  QPushButton, QColorDialog, QHBoxLayout

from windows.lib.custom_widgets import CustomWindow


class MainWindow(CustomWindow):
    def __init__(self, wid, geometry=(730, 10, 150, 1)):
        super().__init__('Draw', wid, geometry)

        self.color_button = QPushButton("Color")
        self.color_button.clicked.connect(self.open_color_picker)
        self.layout.addWidget(self.color_button)
        self.color_picker = QColorDialog()

        self.button_layout = QHBoxLayout()

        self.clear_button = QPushButton("Clear")
        # self.clear_button.clicked.connect(self.clear_canvas)
        self.button_layout.addWidget(self.clear_button)

        self.start_button = QPushButton("Start")
        # self.start_button.clicked.connect(self.start_drawing)
        self.button_layout.addWidget(self.start_button)

        self.layout.addLayout(self.button_layout)

    def open_color_picker(self):
        self.color_picker.getColor()
