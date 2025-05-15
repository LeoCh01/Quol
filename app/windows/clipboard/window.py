import json
import os

from pynput import keyboard
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, QSize
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QHBoxLayout, QApplication

from windows.custom_widgets import CustomWindow

BASE_PATH = os.path.dirname(__file__)


class MainWindow(CustomWindow):
    copy_signal = Signal()

    def __init__(self, wid, geometry=(550, 10, 170, 1)):
        super().__init__('Clipboard', wid, geometry, path=BASE_PATH)
        self.copy_signal.connect(self.update_clipboard)

        self.copy_params = QHBoxLayout()
        self.clear = QPushButton('Clear')
        self.clear.clicked.connect(self.on_clear)
        self.copy_params.addWidget(self.clear)
        self.layout.addLayout(self.copy_params)

        self.clip_groupbox = QGroupBox('History')
        self.clip_layout = QVBoxLayout()
        self.clip_groupbox.setLayout(self.clip_layout)
        self.layout.addWidget(self.clip_groupbox)

        self.copy_thread = keyboard.Listener(on_release=self.on_copy)
        self.copy_thread.start()

        with open(BASE_PATH + '/res/clipboard.json', 'r') as f:
            self.clipboard = json.load(f)

            for text in self.clipboard:
                self.clip_layout.insertWidget(0, self.create_copy_btn(text))

    def on_copy(self, key):
        if str(key) == r"'\x03'":
            self.copy_signal.emit()

    @staticmethod
    def create_copy_btn(text):
        fulltext = text
        if len(text) > 16:
            text = text[:14] + '...'

        button = QPushButton(QIcon(BASE_PATH + '/res/img/copy.png'), text)
        button.setIconSize(QSize(12, 12))
        button.setFixedHeight(24)
        button.setStyleSheet('text-align: left;')
        button.clicked.connect(lambda: QApplication.clipboard().setText(fulltext))

        return button

    def update_clipboard(self):
        print('Clipboard updated')
        self.clipboard.append(QApplication.clipboard().text())
        self.setFixedHeight(self.height() + 24)

        while len(self.clipboard) > self.config['length']:
            self.clipboard.pop(0)
            self.clip_layout.itemAt(self.config['length'] - 1).widget().deleteLater()
            self.setFixedHeight(self.height() - 24)

        self.clip_layout.insertWidget(0, self.create_copy_btn(self.clipboard[-1]))

        with open(BASE_PATH + '/res/clipboard.json', 'w') as f:
            json.dump(self.clipboard, f, indent=2)

    def on_clear(self):
        self.clipboard = []
        for i in reversed(range(self.clip_layout.count())):
            self.clip_layout.itemAt(i).widget().deleteLater()
            self.setFixedHeight(self.height() - 24)

        with open(BASE_PATH + '/res/clipboard.json', 'w') as f:
            json.dump(self.clipboard, f, indent=2)
