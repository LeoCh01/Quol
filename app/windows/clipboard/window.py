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

    def __init__(self, parent, wid, geometry=(10, 120, 180, 1)):
        super().__init__('Clipboard', wid, geometry, path=BASE_PATH)
        self.parent = parent
        self.copy_signal.connect(self.on_copy)

        self.copy_params = QHBoxLayout()
        self.clear = QPushButton('Clear')
        self.clear.clicked.connect(self.on_clear)
        self.copy_params.addWidget(self.clear)

        self.note = QPushButton('Note')
        self.note.clicked.connect(lambda: self.on_note())
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

        with open(BASE_PATH + '/res/clipboard.json', 'r') as f:
            self.clipboard = json.load(f)

            if len(self.clipboard['copy']) > self.config['length']:
                self.clipboard['copy'] = self.clipboard['copy'][-self.config['length']:]

            for text in self.clipboard['copy']:
                self.clip_layout.insertWidget(0, self.create_copy_btn(text))

            for i, note in enumerate(self.clipboard['sticky'], 1):
                if note:
                    self.on_note(i, note, (i * 15, self.config['length'] * 30 + 200 + i * 45, 200, 200))

    def close(self):
        keyboard.unhook_all()
        super().close()

    def create_copy_btn(self, text):
        return CustomButton(QIcon(BASE_PATH + '/res/img/copy.png'), text, self.clipboard['copy'])

    def update_clipboard(self):
        if not QApplication.clipboard().text():
            return

        self.clipboard['copy'].append(QApplication.clipboard().text())

        while len(self.clipboard['copy']) > self.config['length']:
            self.clipboard['copy'].pop(0)
            self.clip_layout.itemAt(self.config['length'] - 1).widget().deleteLater()

        self.clip_layout.insertWidget(0, self.create_copy_btn(self.clipboard['copy'][-1]))

        with open(BASE_PATH + '/res/clipboard.json', 'w') as f:
            json.dump(self.clipboard, f, indent=2)

    def on_clear(self):
        self.clipboard['copy'] = []
        for i in reversed(range(self.clip_layout.count())):
            self.clip_layout.itemAt(i).widget().deleteLater()

        with open(BASE_PATH + '/res/clipboard.json', 'w') as f:
            json.dump(self.clipboard, f, indent=2)

    def on_note(self, id=-1, text='', geometry=(100, 100, 200, 200)):
        if id == -1:
            try:
                id = self.clipboard['sticky'].index('') + 1
            except ValueError:
                print('full')
                return

        sticky_window = StickyWindow(self, id, text, geometry)
        self.sticky_notes.append(sticky_window)

        self.parent.toggle_signal.connect(sticky_window.toggle_windows)
        sticky_window.toggle_windows_2 = self.parent.toggle_windows_2

        sticky_window.show()
        sticky_window.raise_()
        sticky_window.activateWindow()

    def on_copy(self):
        QTimer.singleShot(100, self.update_clipboard)

    def on_update_config(self):
        i = 0
        while len(self.clipboard['copy']) > self.config['length']:
            self.clipboard['copy'].pop(0)
            self.clip_layout.itemAt(self.config['length'] - i).widget().deleteLater()
            i += 1

        self.setFixedHeight(self.config['length'] * 30 + 110)


class CustomButton(QPushButton):
    def __init__(self, icon, text, clipboard):
        self.full_text = text
        if len(text) > 18:
            text = text[:16] + '...'

        super().__init__(icon, text)

        self.setIconSize(QSize(12, 12))
        self.setFixedHeight(24)
        self.setStyleSheet('text-align: left;')
        self.copy_clipboard = clipboard

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            QApplication.clipboard().setText(self.full_text)
        elif event.button() == Qt.MouseButton.RightButton:
            layout = self.parentWidget().layout()
            if layout:
                layout.removeWidget(self)
            self.deleteLater()
            self.copy_clipboard.remove(self.full_text)
        super().mousePressEvent(event)


class StickyWindow(CustomWindow):
    def __init__(self, parent, id, text, geometry):
        super().__init__(str(id), -1, geometry, add_close_btn=True)
        self.parent = parent
        self.id = id
        self.text_edit = QTextEdit(self)
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.text_edit.setPlaceholderText('...')
        self.text_edit.setText(text)
        self.layout.addWidget(self.text_edit)

        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(1000)
        self.inactivity_timer.timeout.connect(self.save_note)
        self.text_edit.textChanged.connect(self.reset_timer)

    def reset_timer(self):
        self.inactivity_timer.start()

    def save_note(self):
        self.inactivity_timer.stop()
        self.parent.clipboard['sticky'][self.id - 1] = self.text_edit.toPlainText()
        with open(BASE_PATH + '/res/clipboard.json', 'w') as f:
            json.dump(self.parent.clipboard, f, indent=2)

    def closeEvent(self, event):
        self.inactivity_timer.stop()
        self.parent.toggle_signal.disconnect(self.toggle_windows)
        self.text_edit.setText('')
        self.save_note()
        super().closeEvent(event)
