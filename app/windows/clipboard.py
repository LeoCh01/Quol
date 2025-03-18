import json

from PySide6 import QtGui, QtCore
from pynput import keyboard
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QGroupBox, QVBoxLayout, QPushButton, QHBoxLayout, QCheckBox, QSlider, QApplication

from res.paths import CLIPBOARD_PATH, IMG_PATH
from windows.lib.custom_widgets import CustomWindow


class MainWindow(CustomWindow):
    copy_signal = Signal()

    def __init__(self, wid, geometry=(550, 10, 170, 1)):
        super().__init__('Clipboard', wid, geometry)
        self.copy_signal.connect(self.update_clipboard)

        self.copy_params = QHBoxLayout()
        self.disable = QCheckBox("Disable")
        self.disable.stateChanged.connect(self.on_disable_change)
        self.copy_params.addWidget(self.disable)
        self.clear = QPushButton("Clear")
        self.clear.clicked.connect(self.on_clear)
        self.copy_params.addWidget(self.clear)
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

        self.clip_groupbox = QGroupBox("History")
        self.clip_layout = QVBoxLayout()
        self.clip_groupbox.setLayout(self.clip_layout)
        self.layout.addWidget(self.clip_groupbox)

        self.copy_thread = None
        self.load_config()
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

    @staticmethod
    def create_copy_btn(text):
        fulltext = text
        if len(text) > 16:
            text = text[:14] + '...'

        button = QPushButton(QtGui.QIcon(IMG_PATH + 'copy.png'), text)
        button.setIconSize(QtCore.QSize(12, 12))
        button.setFixedHeight(24)
        button.setStyleSheet("text-align: left;")
        button.clicked.connect(lambda: QApplication.clipboard().setText(fulltext))

        return button

    def update_clipboard(self):
        self.clipboard.append(QApplication.clipboard().text())
        self.setFixedHeight(self.height() + 24)

        while len(self.clipboard) > self.copy_len.value():
            self.clipboard.pop(0)
            self.clip_layout.itemAt(self.copy_len.value() - 1).widget().deleteLater()
            self.setFixedHeight(self.height() - 24)

        self.clip_layout.insertWidget(0, self.create_copy_btn(self.clipboard[-1]))
        self.save_config()

    def on_clear(self):
        self.clipboard = []
        for i in reversed(range(self.clip_layout.count())):
            self.clip_layout.itemAt(i).widget().deleteLater()
            self.setFixedHeight(self.height() - 24)

        self.set_config('clipboard', self.clipboard)
        self.save_config()

    def on_slider_change(self):
        self.copy_lab.setText(f' {self.copy_len.value():<3}')
        self.set_config('length', self.copy_len.value())

        while len(self.clipboard) > self.copy_len.value():
            self.clipboard.pop(0)
            self.clip_layout.itemAt(self.copy_len.value() - 1).widget().deleteLater()
            self.setFixedHeight(self.height() - 24)

    def set_config(self, k, v):
        self.config[k] = v
        self.save_config()

    def load_config(self):
        self.clipboard = []

        try:
            with open(CLIPBOARD_PATH, 'r') as f:
                self.config = json.load(f)
                self.clipboard = self.config['clipboard']
                self.disable.setChecked(self.config['disable'])
                self.copy_len.setValue(max(self.config['length'], len(self.clipboard)))

                for clip in self.clipboard:
                    self.clip_layout.insertWidget(0, self.create_copy_btn(clip))

        except Exception as e:
            print("error :: ", e)

    def save_config(self):
        with open(CLIPBOARD_PATH, 'w') as f:
            json.dump(self.config, f)
