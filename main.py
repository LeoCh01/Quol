import logging
import os
import sys

import keyboard
from pynput import mouse
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QApplication

import importlib
import json

from src.windows.custom_window import RES_PATH


class App(QObject):
    toggle = Signal(bool)
    windows = []

    def __init__(self):
        super().__init__()

        with open(RES_PATH + '/settings.json', 'r') as f:
            settings = json.load(f)

        self.toggle_key = settings.get('toggle_key', '`')
        keyboard.add_hotkey(self.toggle_key, self.toggle_windows, suppress=True)
        self.is_hidden = False
        self.is_reset = settings.get('reset', True)

        logging.error(os.getcwd())

        for i, d in enumerate(settings.get('windows', [])):
            try:
                class_obj = App.load_script(d['type']).MainWindow
            except Exception as e:
                logging.error(f"Error loading {d['type'][:-3]} :: {e}", exc_info=True)
                continue
            if d['type'] == 'info':
                if self.is_reset:
                    self.windows.append(class_obj(i, set_toggle_key=self.set_toggle_key, key=self.toggle_key))
                else:
                    self.windows.append(class_obj(i, d['geometry'], set_toggle_key=self.set_toggle_key, key=self.toggle_key))
            else:
                if self.is_reset:
                    self.windows.append(class_obj(i))
                else:
                    self.windows.append(class_obj(i, d['geometry']))

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
        with open(RES_PATH + 'settings.json', 'r') as f:
            settings = json.load(f)
        settings['toggle_key'] = key
        with open(RES_PATH + 'settings.json', 'w') as f:
            json.dump(settings, f, indent=2)

    @staticmethod
    def load_script(script_name):
        script_path = os.path.join(os.getcwd() + '\\src\\windows', script_name)
        print(script_path)

        if os.path.exists(script_path):
            spec = importlib.util.spec_from_file_location(script_name, script_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[script_name] = module
            spec.loader.exec_module(module)
            return module
        else:
            logging.error(f"Script {script_name} does not exist at {script_path}.")
            return None


if __name__ == "__main__":
    print('Starting Windows Helper')
    app = QApplication([])

    # Set working directory
    # base_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    # base_dir = os.path.abspath(os.path.join(base_dir, os.pardir))
    # os.chdir(base_dir)
    print('Current working directory:', os.getcwd())

    logging.basicConfig(
        filename=RES_PATH + "error.log",
        filemode='a',
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    try:
        with open('src/res/style.qss', 'r') as f:
            stylesheet = f.read()
        app.setStyleSheet(stylesheet)

        application = App()
        app.exec()
    except Exception as e:
        print('error :: ', e)
        logging.error(e, exc_info=True)

    # with open('res/style.qss', 'r') as f:
    #     stylesheet = f.read()
    # app.setStyleSheet(stylesheet)
