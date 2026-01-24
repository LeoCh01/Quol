import asyncio
import os

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QCheckBox
from PySide6.QtGui import QMouseEvent, QDesktopServices
from PySide6.QtCore import Qt, QPoint, QTimer, QUrl

from qlib.io_helpers import read_json, write_json
from updater import update_minor


class CustomTitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet('background-color: #222;')

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)

        self.title = QLabel('Launcher')
        self.title.setStyleSheet('color: white; font-weight: bold;')
        layout.addWidget(self.title)

        layout.addStretch()

        self.close_btn = QPushButton('✕')
        self.close_btn.setFixedSize(25, 25)
        layout.addWidget(self.close_btn)


class AppLauncher(QWidget):
    def __init__(self, new, old, on_continue_callback):
        super().__init__()
        self.new_version = new
        self.old_version = old
        major = new.split('.')[0:2] != old.split('.')[0:2]
        self.on_continue = on_continue_callback
        self.drag_pos = QPoint()

        self.setWindowTitle('Updater')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(300, 175)

        self.setStyleSheet('''
            QWidget {
                background-color: #333;
                color: white;
            }

            QPushButton {
                background-color: #444;
                color: white;
                border: none;
                padding: 6px;
            }

            QPushButton:hover {
                background-color: #555;
            }
        ''')

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title_bar = CustomTitleBar(self)
        self.layout.addWidget(self.title_bar)
        self.title_bar.close_btn.clicked.connect(self.close)

        if major:
            self.init_major_update_ui()
        else:
            self.init_patch_update_ui()

    def init_major_update_ui(self):
        self.main_content = QFrame()
        content_layout = QVBoxLayout(self.main_content)

        self.label = QLabel(f'New update available! (v{self.new_version})')
        content_layout.addWidget(self.label)

        self.update_btn = QPushButton('Go to Releases')
        self.update_btn.clicked.connect(self.on_update_clicked)
        content_layout.addWidget(self.update_btn)

        self.cont_btn = QPushButton('Continue without Updating')
        self.cont_btn.clicked.connect(self.on_continue_clicked)
        content_layout.addWidget(self.cont_btn)

        self.dont_show = QCheckBox("Don't show this again")
        self.dont_show.stateChanged.connect(lambda state: self.on_dont_show_changed(state))
        self.dont_show.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        content_layout.addWidget(self.dont_show)

        self.layout.addWidget(self.main_content)

    def init_patch_update_ui(self):
        self.main_content = QFrame()
        content_layout = QVBoxLayout(self.main_content)

        self.label = QLabel(f'Patch update available! (v{self.new_version})')
        content_layout.addWidget(self.label)

        self.update_btn = QPushButton('Update')
        self.update_btn.clicked.connect(lambda: QTimer.singleShot(0, lambda: asyncio.run(self.on_patch_update())))
        content_layout.addWidget(self.update_btn)

        self.cont_btn = QPushButton('Continue without Updating')
        self.cont_btn.clicked.connect(self.on_continue_clicked)
        content_layout.addWidget(self.cont_btn)

        self.dont_show = QCheckBox("Don't show this again")
        self.dont_show.stateChanged.connect(lambda state: self.on_dont_show_changed(state))
        self.dont_show.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        content_layout.addWidget(self.dont_show)

        self.layout.addWidget(self.main_content)

    def on_update_clicked(self):
        QDesktopServices.openUrl(QUrl("https://github.com/LeoCh01/Quol/releases/latest"))
        self.close()

    async def on_patch_update(self):
        self.label.setText("Updating...")
        self.update_btn.setEnabled(False)
        self.cont_btn.setEnabled(False)
        self.dont_show.setEnabled(False)
        QApplication.processEvents()

        success = await update_minor()

        self.update_btn.hide()
        self.cont_btn.hide()
        self.dont_show.hide()

        self.countdown_label = QLabel("")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.countdown_label.setContentsMargins(0, 0, 10, 10)
        self.layout.addWidget(self.countdown_label)

        if success:
            self.label.setText("Update complete. Please reopen the app.")
        else:
            self.label.setText("Update failed. Please try again later.")

        QApplication.processEvents()

        self.seconds_left = 10
        self.countdown_label.setText(f"This window will close in {self.seconds_left}s")

        def update_countdown():
            self.seconds_left -= 1
            if self.seconds_left > 0:
                self.countdown_label.setText(f"This window will close in {self.seconds_left}s")
            else:
                self.close_timer.stop()
                self.close()

        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(update_countdown)
        self.close_timer.start(1000)

    def on_dont_show_changed(self, state):
        settings = read_json(os.getcwd() + '/settings.json')
        settings['show_updates'] = (state != 2)
        write_json(os.getcwd() + '/settings.json', settings)

    def on_continue_clicked(self):
        self.hide()
        self.on_continue()
        QTimer.singleShot(100, self.close)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()