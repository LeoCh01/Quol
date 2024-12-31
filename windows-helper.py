import logging
import os
import sys

import keyboard
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QApplication
from windows.color_picker import ColorPicker
from windows.run_command import RunCmd
from windows.info import Info
import json


class App(QObject):
    toggle = Signal(bool)

    def __init__(self):
        super().__init__()

        with open('res/settings.json', 'r') as f:
            settings = json.load(f)

        self.toggle_key = settings.get('toggle_key', '`')
        keyboard.add_hotkey(self.toggle_key, self.toggle_windows, suppress=True)

        self.windows = [
            Info((10, 10, 200, 1), set_toggle_key=self.set_toggle_key, key=self.toggle_key),
            ColorPicker((10, 150, 200, 1)),
            RunCmd((220, 10, 200, 1))
        ]
        self.is_hidden = False

        for window in self.windows:
            self.toggle.connect(window.toggle_windows)
            window.show()

    def toggle_windows(self):
        self.toggle.emit(self.is_hidden)
        self.is_hidden = not self.is_hidden

    def set_toggle_key(self, key):
        print(f"Changing toggle key from {self.toggle_key} to {key}")
        if self.toggle_key == key:
            return

        keyboard.remove_hotkey(self.toggle_key)
        self.toggle_key = key

        keyboard.add_hotkey(self.toggle_key, self.toggle_windows, suppress=True)
        with open('res/settings.json', 'r') as f:
            settings = json.load(f)
        settings['toggle_key'] = key
        with open('res/settings.json', 'w') as f:
            json.dump(settings, f, indent=2)


if __name__ == "__main__":
    app = QApplication([])

    # Set working directory
    base_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(base_dir)

    logging.basicConfig(
        filename="res/error.log",
        filemode='a',
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    try:
        with open('res/style.qss', 'r') as f:
            stylesheet = f.read()
        app.setStyleSheet(stylesheet)

        application = App()
        app.exec()
    except Exception as e:
        logging.error(e, exc_info=True)
