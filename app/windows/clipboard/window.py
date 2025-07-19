import os

import keyboard
from PySide6.QtGui import QIcon, Qt
from PySide6.QtCore import Signal, QSize, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QHBoxLayout, QApplication, QSizePolicy, QTextEdit, \
    QWidget, QLabel

from lib.io_helpers import read_json, write_json
from lib.quol_window import QuolMainWindow, QuolSubWindow
from lib.window_loader import WindowInfo, WindowContext


class MainWindow(QuolMainWindow):
    copy_signal = Signal()

    def __init__(self, window_info: WindowInfo, window_context: WindowContext):
        super().__init__('Clipboard', window_info, window_context, default_geometry=(10, 130, 180, 1))

        self.copy_signal.connect(self.on_copy)

        # self.copy_popup = CopiedPopup('copied!')

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
        
        self.clipboard_path = self.window_info.path + '/res/clipboard.json'
        self.clipboard = None
        self.load_clipboard()
        
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
        return CustomButton(QIcon(self.window_info.path + '/res/img/copy.png'), text, self.clipboard['copy'])

    def save_clipboard(self):
        write_json(self.clipboard_path, self.clipboard)

    def load_clipboard(self):
        self.clipboard = read_json(self.clipboard_path)

    def update_clipboard(self):
        if not QApplication.clipboard().text():
            return

        # self.copy_popup.play()

        self.clipboard['copy'].append(QApplication.clipboard().text())

        while len(self.clipboard['copy']) > self.config['length']:
            self.clipboard['copy'].pop(0)
            self.clip_layout.itemAt(self.config['length'] - 1).widget().deleteLater()

        self.clip_layout.insertWidget(0, self.create_copy_btn(self.clipboard['copy'][-1]))

    def on_clear(self):
        self.clipboard['copy'] = []
        for i in reversed(range(self.clip_layout.count())):
            self.clip_layout.itemAt(i).widget().deleteLater()

        self.save_clipboard()

    def on_note(self, id=-1, text=''):
        if id == -1:
            try:
                id = self.clipboard['sticky'].index('') + 1
            except ValueError:
                print('full')
                return

        sticky_window = StickyWindow(self, text, id)
        self.sticky_notes.append(sticky_window)

        self.window_context.toggle.connect(sticky_window.toggle_windows)

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
        super().mousePressEvent(event)


class StickyWindow(QuolSubWindow):
    def __init__(self, main_window: MainWindow, text: str, id: int):
        super().__init__(main_window, str(id))

        self.id = id
        self.text_edit = QTextEdit(self)
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.text_edit.setPlaceholderText('...')
        self.text_edit.setText(text)
        self.layout.addWidget(self.text_edit)

        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(500)
        self.inactivity_timer.timeout.connect(self.save_note)
        self.text_edit.textChanged.connect(self.reset_timer)

    def reset_timer(self):
        self.inactivity_timer.start()

    def save_note(self):
        self.inactivity_timer.stop()
        self.main_window.clipboard['sticky'][self.id - 1] = self.text_edit.toPlainText()
        self.main_window.save_clipboard()

    def closeEvent(self, event):
        self.inactivity_timer.stop()
        self.main_window.window_context.toggle.disconnect(self.toggle_windows)
        self.text_edit.setText('')
        self.save_note()
        super().closeEvent(event)


class CopiedPopup:
    def __init__(self, text):
        screen_w = QApplication.primaryScreen().size().width()
        screen_h = QApplication.primaryScreen().size().height()

        self.top = CopiedPopupSub('', QRect(0, -30, screen_w, 50), 30, [0, -1])
        self.bottom = CopiedPopupSub(text, QRect(0, screen_h - 20, screen_w, 50), 30, [0, 1])
        self.left = CopiedPopupSub('', QRect(-30, 0, 50, screen_h), 30, [-1, 0])
        self.right = CopiedPopupSub('', QRect(screen_w - 20, 0, 50, screen_h), 30, [1, 0])

    def play(self):
        self.top.play()
        self.bottom.play()
        self.left.play()
        self.right.play()


class CopiedPopupSub(QWidget):
    def __init__(self, text, geometry, h, d):
        super().__init__(geometry=geometry)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(
            f'background: qlineargradient(x1:{int(d[0] == -1)}, y1:{int(d[1] == -1)}, x2:{int(d[0] == 1)}, y2:{int(d[1] == 1)}, stop:0 #00000000, stop:1 #000000);'
        )

        layout = QVBoxLayout(self)
        self.text = QLabel(text, self)
        self.text.setStyleSheet('color: #fff;')
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.move_in_animation = QPropertyAnimation(self, b"pos")
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.move_out_animation = QPropertyAnimation(self, b"pos")

        self.t1 = 300
        self.t2 = 500
        self.h = h
        self.d = d

    def play(self):
        self.show()
        self.raise_()

        self.start_fade()

    def start_fade(self):
        self.fade_in_animation.setDuration(self.t1)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)

        self.move_in_animation.setEasingCurve(QEasingCurve.Type.OutExpo)
        self.move_in_animation.setDuration(self.t2)
        self.move_in_animation.setStartValue(QRect(self.x(), self.y(), self.width(), self.height()).topLeft())
        self.move_in_animation.setEndValue(QRect(self.x() - self.h * self.d[0], self.y() - self.h * self.d[1], self.width(), self.height()).topLeft())

        self.fade_in_animation.start()
        self.move_in_animation.start()

        QTimer.singleShot(self.t1 + 200, self.start_fade_out)

    def start_fade_out(self):
        self.fade_out_animation.setDuration(self.t1)
        self.fade_out_animation.setStartValue(1)
        self.fade_out_animation.setEndValue(0)

        self.move_out_animation.setDuration(self.t2)
        self.move_out_animation.setStartValue(QRect(self.x(), self.y(), self.width(), self.height()).topLeft())
        self.move_out_animation.setEndValue(QRect(self.x() + self.h * self.d[0], self.y() + self.h * self.d[1], self.width(), self.height()).topLeft())

        self.fade_out_animation.start()
        self.move_out_animation.start()

        QTimer.singleShot(self.t2, self.hide)
