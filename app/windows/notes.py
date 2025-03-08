import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QGroupBox, QVBoxLayout, QPushButton, QHBoxLayout, QCheckBox, QSlider

from res.paths import NOTES_PATH
from windows.lib.custom_widgets import CustomWindow, TestWin


class MainWindow(CustomWindow):
    def __init__(self, wid, geometry=(550, 10, 140, 1)):
        super().__init__('Notes', wid, geometry)

        self.copy_params = QHBoxLayout()
        self.copy_params.addWidget(QCheckBox("Listen"))
        self.copy_params.addWidget(QCheckBox("Hide"))
        self.layout.addLayout(self.copy_params)

        self.copy_params2 = QHBoxLayout()
        self.copy_lab = QLabel(' 1  ')
        self.copy_params2.addWidget(self.copy_lab)
        self.copy_len = QSlider()
        self.copy_len.setOrientation(Qt.Horizontal)
        self.copy_len.setRange(1, 10)
        self.copy_len.valueChanged.connect(self.on_slider_change)
        self.copy_params2.addWidget(self.copy_len)
        self.layout.addLayout(self.copy_params2)

        self.copy_groupbox = QGroupBox("Ctrl+C")
        self.copy_layout = QVBoxLayout()
        self.copy_groupbox.setLayout(self.copy_layout)
        self.layout.addWidget(self.copy_groupbox)

        self.add_btn = QPushButton("Create Note")
        self.add_btn.clicked.connect(self.create_note)
        self.layout.addWidget(self.add_btn)

        self.load_notes()

    def on_slider_change(self):
        self.copy_lab.setText(f' {self.copy_len.value():<3}')

    def create_note(self):
        n = Note()

    def load_notes(self):
        self.notes = []

        try:
            with open(NOTES_PATH, 'r') as f:
                self.notes = json.load(f)
        except Exception as e:
            print("error :: ", e)

        for name, data in self.notes:
            pass
            # self.add_note_to_layout(n_name, n, show_output)

    def save_notes(self):
        with open(NOTES_PATH, 'w') as f:
            json.dump(self.notes, f)


class Note(TestWin):
    def __init__(self, geometry=(300, 300, 200, 200)):
        super().__init__()


