import json

from pynput import keyboard
from PySide6.QtCore import Qt, QTimer, QMetaObject, Signal
from PySide6.QtWidgets import QLabel, QGroupBox, QVBoxLayout, QPushButton, QHBoxLayout, QCheckBox, QSlider, \
    QApplication, QWidget

from res.paths import NOTES_PATH
from windows.lib.custom_widgets import CustomWindow, TestWin


class MainWindow(CustomWindow):
    copy_signal = Signal()

    def __init__(self, wid, geometry=(550, 10, 140, 1)):
        super().__init__('Notes', wid, geometry)
        self.copy_signal.connect(self.update_clipboard)

        self.copy_params = QHBoxLayout()
        self.disable = QCheckBox("Disable")
        self.disable.stateChanged.connect(self.on_disable_change)
        self.copy_params.addWidget(self.disable)
        self.hide = QCheckBox("Hide")
        self.hide.stateChanged.connect(self.on_hide_change)
        self.copy_params.addWidget(self.hide)
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

        self.clip_groupbox = QGroupBox("Ctrl+C")
        self.clip_layout = QVBoxLayout()
        self.clip_groupbox.setLayout(self.clip_layout)
        self.layout.addWidget(self.clip_groupbox)

        self.add_btn = QPushButton("Create Note")
        self.add_btn.clicked.connect(self.create_note)
        self.layout.addWidget(self.add_btn)

        self.copy_thread = None
        self.load_notes()
        self.on_disable_change()

    def on_disable_change(self):
        self.set_config('disable', self.disable.isChecked())

        if self.disable.isChecked() and self.copy_thread:
            self.copy_thread.stop()
            self.copy_thread = None
        else:
            self.copy_thread = keyboard.Listener(on_release=self.on_copy)
            self.copy_thread.start()

    def on_copy(self, key):
        if str(key) == r"'\x03'":
            self.copy_signal.emit()

    def create_copy_btn(self, text):
        if len(text) > 15:
            text = text[:12] + '...'

        layout = QHBoxLayout()
        label = QLabel(text)
        button = QPushButton("+")
        button.clicked.connect(lambda: self.on_clipboard_button_click(text))

        layout.addWidget(label)
        layout.addWidget(button)

        return layout

    def update_clipboard(self):
        self.clipboard.append(QApplication.clipboard().text())

        while len(self.clipboard) > self.copy_len.value():
            self.clipboard.pop(0)

            sec = self.clip_layout.itemAt(self.copy_len.value() - 1).layout()
            for i in reversed(range(sec.count())):
                sec.itemAt(i).widget().deleteLater()
            sec.deleteLater()

        self.clip_layout.insertLayout(0, self.create_copy_btn(self.clipboard[-1]))
        self.save_notes()

    def on_clipboard_button_click(self, text):
        pass

    def on_hide_change(self):
        self.set_config('hide', self.hide.isChecked())

    def on_slider_change(self):
        self.copy_lab.setText(f' {self.copy_len.value():<3}')
        self.set_config('length', self.copy_len.value())

        while len(self.clipboard) > self.copy_len.value():
            self.clipboard.pop(0)
            self.clip_layout.itemAt(self.copy_len.value() - 1).layout().deleteLater()

    def create_note(self):
        pass

    def set_config(self, k, v):
        self.config[k] = v
        self.save_notes()

    def load_notes(self):
        self.notes = []
        self.clipboard = []

        try:
            with open(NOTES_PATH, 'r') as f:
                self.config = json.load(f)

                self.notes = self.config['notes']
                self.clipboard = self.config['clipboard']
                self.disable.setChecked(self.config['disable'])
                self.hide.setChecked(self.config['hide'])
                self.copy_len.setValue(self.config['length'])

                for note in self.notes:
                    pass

                for clip in self.clipboard:
                    self.clip_layout.insertLayout(0, self.create_copy_btn(clip))
        except Exception as e:
            print("error :: ", e)

    def save_notes(self):
        with open(NOTES_PATH, 'w') as f:
            json.dump(self.config, f)


class Note(TestWin):
    def __init__(self, geometry=(300, 300, 200, 200)):
        super().__init__()


