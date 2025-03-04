import json

from PySide6.QtWidgets import QLabel, QGroupBox, QVBoxLayout, QPushButton, QHBoxLayout, QCheckBox, QDialog, \
    QPlainTextEdit, QLineEdit

from res.paths import NOTES_PATH
from windows.lib.custom_window import CustomWindow


class MainWindow(CustomWindow):
    def __init__(self, wid, geometry=(550, 10, 140, 1)):
        super().__init__('Notes', wid, geometry)

        self.copy_params = QHBoxLayout()
        self.copy_params.addWidget(QCheckBox("Listen"))
        self.copy_params.addWidget(QCheckBox("Hide"))
        self.layout.addLayout(self.copy_params)

        self.copy_params2 = QHBoxLayout()
        self.copy_params2.addWidget(QLabel("Length: "))
        self.copy_length = QLineEdit()
        self.copy_params2.addWidget(self.copy_length)
        self.layout.addLayout(self.copy_params2)

        self.copy_groupbox = QGroupBox("Ctrl+C")
        self.copy_layout = QVBoxLayout()
        self.copy_groupbox.setLayout(self.copy_layout)
        self.layout.addWidget(self.copy_groupbox)

        self.add_btn = QPushButton("Create Note")
        # self.add_btn.clicked.connect(self.open_add_note_dialog)
        self.layout.addWidget(self.add_btn)

        self.notes = []
        self.load_notes()

    def load_notes(self):
        try:
            with open(NOTES_PATH, 'r') as f:
                self.notes = json.load(f)
        except Exception as e:
            print("error :: ", e)
            self.notes = []

        for name, data in self.notes:
            pass
            # self.add_note_to_layout(n_name, n, show_output)

    def save_notes(self):
        with open(NOTES_PATH, 'w') as f:
            json.dump(self.notes, f)
