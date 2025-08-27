import sys
import subprocess
import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel,
    QHBoxLayout, QFrame, QMessageBox
)
from PySide6.QtGui import QMouseEvent, QPalette, QColor
from PySide6.QtCore import Qt, QPoint

from lib.io_helpers import read_json


def check_for_update():
    try:
        response = requests.get('https://raw.githubusercontent.com/LeoCh01/Quol/main/app/res/settings.json')
        data = response.json()
        settings = read_json('settings.json')

        return data['version'] != settings['version']
    except Exception as e:
        print(f"Update check failed: {e}")
        return False


def run_app():
    try:
        print('test')
        subprocess.Popen(["Quol.exe"], shell=True)
    except Exception as e:
        print(f"Failed to launch app: {e}")


class CustomTitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #222222;")

        layout = QHBoxLayout(self)

        self.title = QLabel("Launcher")
        self.title.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(self.title)

        layout.addStretch()

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(25, 25)
        layout.addWidget(self.close_btn)


class AppLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Launcher")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title_bar = CustomTitleBar(self)
        self.layout.addWidget(self.title_bar)
        self.title_bar.close_btn.clicked.connect(self.close)

        self.main_content = QFrame()
        self.main_content.setStyleSheet("background-color: #2b2b2b;")
        content_layout = QVBoxLayout(self.main_content)

        self.label = QLabel(f'There is a new update Available!')
        self.label.setStyleSheet("color: white;")
        content_layout.addWidget(self.label)

        self.update_btn = QPushButton('Update Now')
        self.update_btn.clicked.connect(self.on_update_clicked)
        content_layout.addWidget(self.update_btn)

        self.cont_btn = QPushButton('Continue to App')
        self.cont_btn.clicked.connect(self.on_continue_clicked)
        content_layout.addWidget(self.cont_btn)

        self.layout.addWidget(self.main_content)

        self.drag_pos = QPoint()

    def on_update_clicked(self):
        pass

    def on_continue_clicked(self):
        # run_app()
        self.close()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()


# ---- Apply Dark Theme ----
def apply_dark_theme(app):
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Highlight, QColor(80, 80, 255))
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setStyle("Fusion")
    app.setPalette(dark_palette)


def main():
    if check_for_update():
        app = QApplication(sys.argv)
        apply_dark_theme(app)
        launcher = AppLauncher()
        launcher.show()
        sys.exit(app.exec())

    else:
        run_app()


if __name__ == "__main__":
    main()
