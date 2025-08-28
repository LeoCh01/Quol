import json
import os
import sys
import subprocess
import zipfile

import requests

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt, QPoint

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


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


def clear_old_files():
    for root, dirs, files in os.walk(CURRENT_DIR):
        for file in files:
            if not file.startswith('windows/'):
                file_path = os.path.join(root, file)
                os.remove(file_path)


def extract():
    with zipfile.ZipFile('quol.zip', 'r') as zip_ref:
        for file in zip_ref.namelist():
            if not file.startswith('windows/'):
                zip_ref.extract(file, CURRENT_DIR)


def run_app():
    try:
        subprocess.Popen(['QuolMain.exe'], shell=True)
    except Exception as e:
        print(f'Failed to launch app: {e}')


class CustomTitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet('background-color: #222222;')

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
        clear_old_files()
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
