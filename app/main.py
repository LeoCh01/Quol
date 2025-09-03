import json
import os
import asyncio
import logging
import requests
import sys

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PySide6.QtGui import QMouseEvent, QDesktopServices
from PySide6.QtCore import Qt, QPoint, QTimer, QUrl
from qasync import QEventLoop

from lib.app import App
from lib.loading_screen import LoadingScreen

CURRENT_DIR = os.getcwd()
BRANCH = 'main'


def initialize_logging():
    # logging.basicConfig(
    #     filename='info.log',
    #     filemode='a',
    #     level=logging.INFO,
    #     format='%(message)s',
    # )
    logging.basicConfig(
        filename='error.log',
        filemode='a',
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logging.getLogger().addHandler(logging.StreamHandler())


def initialize_main_app():
    try:
        splash = LoadingScreen()
        splash.show()
        splash.raise_()

        app_instance = App()

        splash.close()

        return app_instance

    except Exception as e:
        logging.error(f"Failed to initialize main app :: {e}", exc_info=True)
        return None


def check_for_update():
    try:
        response = requests.get(f'https://raw.githubusercontent.com/LeoCh01/Quol/{BRANCH}/app/settings.json')
        response.raise_for_status()
        data = response.json()

        with open('settings.json', 'r') as f:
            settings = json.load(f)

        return data['version'] if data['version'] != settings['version'] else ''
    except Exception as e:
        logging.error(f'Update check failed: {e}')
        return ''


class CustomTitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet('background-color: #222;')

        layout = QHBoxLayout(self)

        self.title = QLabel('Launcher')
        self.title.setStyleSheet('color: white; font-weight: bold;')
        layout.addWidget(self.title)

        layout.addStretch()

        self.close_btn = QPushButton('✕')
        self.close_btn.setFixedSize(25, 25)
        layout.addWidget(self.close_btn)


class AppLauncher(QWidget):
    def __init__(self, version, on_continue_callback):
        super().__init__()
        self.setWindowTitle('Updater')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(300, 150)

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

        self.main_content = QFrame()
        content_layout = QVBoxLayout(self.main_content)

        self.label = QLabel(f'New update available! (v{version})')
        content_layout.addWidget(self.label)

        self.update_btn = QPushButton('Go to Releases')
        self.update_btn.clicked.connect(self.on_update_clicked)
        content_layout.addWidget(self.update_btn)

        self.cont_btn = QPushButton('Continue without Updating')
        self.cont_btn.clicked.connect(self.on_continue_clicked)
        content_layout.addWidget(self.cont_btn)

        self.layout.addWidget(self.main_content)

        self.drag_pos = QPoint()
        self.version = version
        self.on_continue = on_continue_callback

    def on_update_clicked(self):
        QDesktopServices.openUrl(QUrl("https://github.com/LeoCh01/Quol/releases/latest"))
        self.close()

    def on_continue_clicked(self):
        self.on_continue()
        self.hide()
        QTimer.singleShot(100, self.close)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()


def main():
    print('Starting Quol...')
    print('Current working directory:', os.getcwd())
    base_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(base_dir)
    print('Switched working directory:', os.getcwd())

    initialize_logging()

    app = QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    new_version = check_for_update()

    if new_version:
        launcher = AppLauncher(new_version, initialize_main_app)
        launcher.show()
    else:
        initialize_main_app()

    with loop:
        loop.run_forever()


if __name__ == '__main__':
    main()
