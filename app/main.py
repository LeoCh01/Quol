import io
import os
import logging
import shutil
import zipfile

import httpx
import requests
import sys

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QCheckBox
from PySide6.QtGui import QMouseEvent, QDesktopServices
from PySide6.QtCore import Qt, QPoint, QTimer, QUrl

from lib.app import App
from lib.io_helpers import read_json, write_json
from lib.loading_screen import LoadingScreen

BRANCH = '3.3-lib-updater'


def initialize_logging():
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


def check_for_update() -> tuple:  # version, is_new_patch_version
    try:
        settings = read_json(os.getcwd() + '/settings.json')
        if not settings.get('show_updates', True):
            return '', ''

        response = requests.get(f'https://raw.githubusercontent.com/LeoCh01/Quol/{BRANCH}/app/settings.json')
        response.raise_for_status()
        data = response.json()

        v1 = settings['version'].split('.')
        v2 = data['version'].split('.')

        return data['version'] if v2[:2] != v1[:2] else '', data['version'] if v2[-1] != v1[-1] else ''

    except Exception as e:
        logging.error(f'Update check failed: {e}')
        return '', ''


def on_dont_show_changed(state):
    settings = read_json(os.getcwd() + '/settings.json')
    settings['show_updates'] = (state != 2)
    write_json(os.getcwd() + '/settings.json', settings)


async def download_item(item: str) -> bool:
    raw_url = f"https://raw.githubusercontent.com/LeoCh01/Quol/main/{item}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(raw_url)
            response.raise_for_status()
            zip_file = io.BytesIO(response.content)

        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(os.getcwd())

        print(f"Successfully extracted {item}")
        return True

    except httpx.RequestError as e:
        print(f"Error downloading the file: {e}")
        return False
    except zipfile.BadZipFile as e:
        print(f"Error: Invalid zip file: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


async def update_patch() -> bool:

    for d in ['res', 'lib', 'quol', 'transitions']:
        item_path = os.path.join(os.getcwd(), d)

        try:
            is_downloaded = await download_item(d)

            if os.path.exists(item_path + '/res/config.json'):
                print(f"Item {item_path} requires app version {v} or higher.")
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                return False

            if os.path.exists(item_path):
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)

            return is_downloaded

        except Exception as e:
            print(f"Error updating {item_path}: {e}")
            return False


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
    def __init__(self, major, patch, on_continue_callback):
        super().__init__()
        self.version = major or patch
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

        self.label = QLabel(f'New update available! (v{self.version})')
        content_layout.addWidget(self.label)

        self.update_btn = QPushButton('Go to Releases')
        self.update_btn.clicked.connect(self.on_update_clicked)
        content_layout.addWidget(self.update_btn)

        self.cont_btn = QPushButton('Continue without Updating')
        self.cont_btn.clicked.connect(self.on_continue_clicked)
        content_layout.addWidget(self.cont_btn)

        self.dont_show = QCheckBox("Don't show this again")
        self.dont_show.stateChanged.connect(lambda state: on_dont_show_changed(state))
        self.dont_show.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        content_layout.addWidget(self.dont_show)

        self.layout.addWidget(self.main_content)

    def init_patch_update_ui(self):
        self.main_content = QFrame()
        content_layout = QVBoxLayout(self.main_content)

        self.label = QLabel(f'Patch update available! (v{self.version})')
        content_layout.addWidget(self.label)

        self.update_btn = QPushButton('Update')
        self.update_btn.clicked.connect(self.on_patch_update)
        content_layout.addWidget(self.update_btn)

        self.cont_btn = QPushButton('Continue without Updating')
        self.cont_btn.clicked.connect(self.on_continue_clicked)
        content_layout.addWidget(self.cont_btn)

        self.dont_show = QCheckBox("Don't show this again")
        self.dont_show.stateChanged.connect(lambda state: on_dont_show_changed(state))
        self.dont_show.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        content_layout.addWidget(self.dont_show)

        self.layout.addWidget(self.main_content)

    def on_update_clicked(self):
        QDesktopServices.openUrl(QUrl("https://github.com/LeoCh01/Quol/releases/latest"))
        self.close()

    def on_patch_update(self):  # TODO
        self.close()

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


def main():
    print('Starting Quol...')
    print('Current working directory:', os.getcwd())
    base_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(base_dir)
    print('Switched working directory:', os.getcwd())

    initialize_logging()

    app = QApplication([])

    major, patch = check_for_update()

    if major or patch:
        launcher = AppLauncher(major, patch, initialize_main_app)
        launcher.show()
    else:
        initialize_main_app()

    app.exec()


if __name__ == '__main__':
    main()
