import json
import os

import keyboard
from PySide6.QtGui import QIcon, Qt
from PySide6.QtCore import Signal, QSize, QTimer
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QHBoxLayout, QApplication, QSizePolicy, QTextEdit

from windows.custom_widgets import CustomWindow

BASE_PATH = os.path.dirname(__file__)


class MainWindow(CustomWindow):
    copy_signal = Signal()

    def __init__(self, wid, geometry=(10, 120, 180, 1)):
        super().__init__('Clipboard', wid, geometry, path=BASE_PATH)
        self.copy_signal.connect(self.on_copy)

        self.copy_params = QHBoxLayout()
        self.clear = QPushButton('Clear')
        self.clear.clicked.connect(self.on_clear)
        self.copy_params.addWidget(self.clear)

        self.note = QPushButton('Note')
        self.note.clicked.connect(self.on_note)
        self.copy_params.addWidget(self.note)

        self.layout.addLayout(self.copy_params)

        self.clip_layout = QVBoxLayout()
        self.clip_groupbox = QGroupBox('History')
        self.clip_groupbox.setLayout(self.clip_layout)
        self.clip_groupbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.clip_groupbox)

        self.copy_hotkey = keyboard.add_hotkey('ctrl+c', lambda: self.copy_signal.emit())

        self.setFixedHeight(self.config['length'] * 30 + 110)
        self.clip_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.sticky_notes = []
        self.sticky_count = 1

        with open(BASE_PATH + '/res/clipboard.json', 'r') as f:
            self.clipboard = json.load(f)

            if len(self.clipboard) > self.config['length']:
                self.clipboard = self.clipboard[-self.config['length']:]

            for text in self.clipboard:
                self.clip_layout.insertWidget(0, self.create_copy_btn(text))

    def close(self):
        keyboard.unhook_all()
        super().close()

    def create_copy_btn(self, text):
        return CustomButton(QIcon(BASE_PATH + '/res/img/copy.png'), text, self.clipboard)

    def update_clipboard(self):
        if not QApplication.clipboard().text():
            return
        print('Clipboard updated')
        self.clipboard.append(QApplication.clipboard().text())

        while len(self.clipboard) > self.config['length']:
            self.clipboard.pop(0)
            self.clip_layout.itemAt(self.config['length'] - 1).widget().deleteLater()

        self.clip_layout.insertWidget(0, self.create_copy_btn(self.clipboard[-1]))

        with open(BASE_PATH + '/res/clipboard.json', 'w') as f:
            json.dump(self.clipboard, f, indent=2)

    def on_clear(self):
        self.clipboard = []
        for i in reversed(range(self.clip_layout.count())):
            self.clip_layout.itemAt(i).widget().deleteLater()

        with open(BASE_PATH + '/res/clipboard.json', 'w') as f:
            json.dump(self.clipboard, f, indent=2)

    def on_note(self):
        sticky_window = StickyWindow(self.sticky_count, self)
        self.sticky_count += 1
        self.sticky_notes.append(sticky_window)

        self.toggle_signal.connect(sticky_window.toggle_windows)
        sticky_window.toggle_windows_2 = self.toggle_windows_2

        sticky_window.show()
        sticky_window.raise_()
        sticky_window.activateWindow()

    def on_copy(self):
        QTimer.singleShot(100, self.update_clipboard)

    def on_update_config(self):
        i = 0
        while len(self.clipboard) > self.config['length']:
            self.clipboard.pop(0)
            self.clip_layout.itemAt(self.config['length'] - i).widget().deleteLater()
            i += 1

        self.setFixedHeight(self.config['length'] * 30 + 110)


class StickyWindow(CustomWindow):
    def __init__(self, count, parent):
        super().__init__(str(count), -1, (100, 100, 200, 200), add_close_btn=True)
        self.parent = parent
        self.text_edit = QTextEdit(self)
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.text_edit.setPlaceholderText('Write your note here...')
        self.layout.addWidget(self.text_edit)

    def closeEvent(self, event):
        self.parent.toggle_signal.disconnect(self.toggle_windows)
        self.parent.sticky_notes.remove(self)
        super().closeEvent(event)


class CustomButton(QPushButton):
    def __init__(self, icon, text, clipboard):
        self.full_text = text
        if len(text) > 18:
            text = text[:16] + '...'

        super().__init__(icon, text)

        self.setIconSize(QSize(12, 12))
        self.setFixedHeight(24)
        self.setStyleSheet('text-align: left;')
        self.clipboard = clipboard

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            QApplication.clipboard().setText(self.full_text)
        elif event.button() == Qt.MouseButton.RightButton:
            layout = self.parentWidget().layout()
            if layout:
                layout.removeWidget(self)
            self.deleteLater()
            self.clipboard.remove(self.full_text)
        super().mousePressEvent(event)
