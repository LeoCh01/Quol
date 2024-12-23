from PySide6.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QLineEdit, QPushButton

from components.custom_window import CustomWindow


class Test(CustomWindow):
    def __init__(self, title, geometry):
        super().__init__(title, geometry)

        self.box = QGroupBox("Test")
        self.layout.addWidget(self.box)

        self.box_layout = QVBoxLayout(self.box)

        self.label = QLabel("Test label")
        self.box_layout.addWidget(self.label)

        self.text_input = QLineEdit()
        self.box_layout.addWidget(self.text_input)

        self.button = QPushButton("Submit")
        self.box_layout.addWidget(self.button)



