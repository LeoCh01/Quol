import json
import logging
import os
import shutil
import sys
import subprocess
import zipfile

import requests

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt, QPoint

CURRENT_DIR = os.getcwd()


def check_for_update():
    try:
        response = requests.get('https://raw.githubusercontent.com/LeoCh01/Quol/main/app/res/settings.json')
        data = response.json()

        with open('settings.json', 'r') as f:
            settings = json.load(f)

        return data['version'] if data['version'] != settings['version'] else ''
    except Exception as e:
        print(f'Update check failed: {e}')
        return ''


def download_latest(version):
    url = f'https://github.com/LeoCh01/Quol/releases/latest/download/Quol-v{version}.zip'
    response = requests.get(url)
    with open(f'quol.zip', 'wb') as f:
        f.write(response.content)


def extract():
    #  TODO move this somewhere else
    folders_to_remove = ['lib', 'res', 'transitions', '_internal']

    for folder in folders_to_remove:
        folder_path = os.path.join(CURRENT_DIR, folder)
        logging.info(folder_path)
        if os.path.exists(folder_path):
            logging.info(f"Removing folder: {folder_path}")
            try:
                shutil.rmtree(folder_path)
            except Exception as e:
                logging.info(f"Failed to remove {folder}: {e}")

    logging.info('\n\ndone\n\n')

    with zipfile.ZipFile('quol.zip', 'r') as zip_ref:
        for file in zip_ref.namelist():
            if not file.startswith('windows/') and not file.startswith('Quol.exe'):
                target_path = os.path.join(CURRENT_DIR, file)

                if file.endswith('/'):
                    os.makedirs(target_path, exist_ok=True)
                    logging.info('folder :: ' + target_path)
                else:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    logging.info('file? :: ' + target_path)
                    with zip_ref.open(file) as source, open(target_path, 'wb') as target:
                        target.write(source.read())


def run_app():
    try:
        subprocess.Popen(['QuolMain.exe'], shell=True)
    except Exception as e:
        print(f'Failed to launch app: {e}')


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
    def __init__(self, version):
        super().__init__()
        self.setWindowTitle('Custom Launcher')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

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
                background-color: #f00;
            }
        ''')

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title_bar = CustomTitleBar(self)
        self.layout.addWidget(self.title_bar)
        self.title_bar.close_btn.clicked.connect(self.close)

        self.main_content = QFrame()
        content_layout = QVBoxLayout(self.main_content)

        self.label = QLabel(f'There is a new update Available! ({version})')
        content_layout.addWidget(self.label)

        self.update_btn = QPushButton('Update Now')
        self.update_btn.clicked.connect(self.on_update_clicked)
        content_layout.addWidget(self.update_btn)

        self.cont_btn = QPushButton('Continue to App')
        self.cont_btn.clicked.connect(self.on_continue_clicked)
        content_layout.addWidget(self.cont_btn)

        self.layout.addWidget(self.main_content)

        self.drag_pos = QPoint()
        self.ver = version

    def on_update_clicked(self):
        download_latest(self.ver)
        # clear_old_files()
        extract()
        self.close()

    def on_continue_clicked(self):
        run_app()
        self.close()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()


def main():
    logging.basicConfig(
        filename='info.log',
        filemode='a',
        level=logging.INFO,
        format='%(message)s',
    )
    logging.getLogger().addHandler(logging.StreamHandler())

    new_version = check_for_update()
    if new_version:
        app = QApplication(sys.argv)
        launcher = AppLauncher(new_version)
        launcher.show()
        sys.exit(app.exec())

    else:
        run_app()


if __name__ == '__main__':
    main()
