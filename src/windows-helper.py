import logging
import os
import sys

import keyboard
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QApplication

from windows.chance import Chance
from windows.color_picker import ColorPicker
from windows.info import Info
from windows.run_command import RunCmd
from windows.python_shell import PythonShell
import json

RESET_WINDOWS = {
    '0': {
        'type': 'info',
        'geometry': {
            'x': 10,
            'y': 10,
            'width': 180
        }
    },
    '1': {
        'type': 'cmd',
        'geometry': {
            'x': 10,
            'y': 147,
            'width': 180
        }
    },
    '2': {
        'type': 'color',
        'geometry': {
            'x': 200,
            'y': 10,
            'width': 180
        }
    },
    '3': {
        'type': 'chance',
        'geometry': {
            'x': 390,
            'y': 10,
            'width': 180
        }
    },
    '4': {
        'type': 'python',
        'geometry': {
            'x': 390,
            'y': 10,
            'width': 1000
        }
    }
}


class App(QObject):
    toggle = Signal(bool)
    all_windows = {'info': Info, 'cmd': RunCmd, 'color': ColorPicker, 'chance': Chance, 'python': PythonShell}
    windows = []

    def __init__(self):
        super().__init__()

        with open('res/settings.json', 'r') as f:
            settings = json.load(f)

        self.toggle_key = settings.get('toggle_key', '`')
        keyboard.add_hotkey(self.toggle_key, self.toggle_windows, suppress=True)
        self.is_hidden = False

        if settings.get('reset', True):
            settings['windows'] = RESET_WINDOWS
            settings['reset'] = False
            with open('res/settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            with open('res/settings.json', 'r') as f:
                settings = json.load(f)

        for i, d in settings.get('windows', {}).items():
            print(d)
            if d['type'] == 'info':
                self.windows.append(
                    Info((
                        d['geometry']['x'],
                        d['geometry']['y'],
                        d['geometry']['width'], 1),
                        i,
                        set_toggle_key=self.set_toggle_key,
                        key=self.toggle_key
                    )
                )
            elif d['type'] in self.all_windows:
                self.windows.append(
                    self.all_windows[d['type']]((
                        d['geometry']['x'],
                        d['geometry']['y'],
                        d['geometry']['width'], 1),
                        i
                    )
                )
            else:
                print(f'Invalid window name: {d["type"]}')

        for window in self.windows:
            self.toggle.connect(window.toggle_windows)
            window.show()

    def toggle_windows(self):
        self.toggle.emit(self.is_hidden)
        self.is_hidden = not self.is_hidden

    def set_toggle_key(self, key):
        print(f'Changing toggle key from {self.toggle_key} to {key}')
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


if __name__ == '__main__':
    app = QApplication([])

    # Set working directory
    # base_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    # os.chdir(base_dir)

    logging.basicConfig(
        filename='res/error.log',
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
        print('error :: ', e)
        logging.error(e, exc_info=True)
