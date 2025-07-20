import logging
import os
import sys
import importlib

from PySide6.QtCore import Signal

from lib.io_helpers import read_json, write_json


class WindowLoader:
    def __init__(self, name):
        self.name = name
        self.module = None
        self.path = f'{os.getcwd()}\\windows\\{self.name}'

    def load(self):
        module_path = self.path + '\\window.py'

        if os.path.exists(module_path):
            spec = importlib.util.spec_from_file_location(self.name, module_path)
            self.module = importlib.util.module_from_spec(spec)
            sys.modules[self.name] = self.module
            spec.loader.exec_module(self.module)
        else:
            logging.error(f'Script {self.name} does not exist at {module_path}.')

    def create_window(self, context, app=None):
        return self.module.MainWindow(WindowInfo(self.path), context)


class SystemWindowLoader(WindowLoader):
    def __init__(self, name):
        super().__init__(name)

    def create_window(self, context, app=None):
        return self.module.MainWindow(app, WindowInfo(self.path), context)


class WindowInfo:
    def __init__(self, path):
        self.path = path
        self.config_path = path + '\\config.json'

    def save_config(self, config):
        write_json(self.config_path, config)

    def load_config(self):
        return read_json(self.config_path)


class WindowContext:
    def __init__(self, toggle: Signal(bool, bool), toggle_windows, toggle_windows_instant, settings, transition_plugin, get_is_hidden):
        self.toggle = toggle
        self.toggle_windows = toggle_windows
        self.toggle_windows_instant = toggle_windows_instant
        self.transition_plugin = transition_plugin
        self.settings = settings
        self.get_is_hidden = get_is_hidden
