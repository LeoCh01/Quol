import logging
import os
import sys
import importlib

from quol_window import QuolBaseWindow


class TransitionPluginInfo:
    def __init__(self, path):
        self.path = path


class TransitionPlugin:
    def __init__(self, name):
        self.name = name
        self.module = None
        self.path = f'{os.getcwd()}\\transitions\\{self.name}'

    def load(self):
        module_path = self.path + '\\transition.py'

        if os.path.exists(module_path):
            spec = importlib.util.spec_from_file_location(self.name, module_path)
            self.module = importlib.util.module_from_spec(spec)
            sys.modules[self.name] = self.module
            spec.loader.exec_module(self.module)
        else:
            logging.error(f'Script {self.name} does not exist at {module_path}.')
            return None

    def create_transition(self, window: QuolBaseWindow):
        return self.module.Transition(TransitionPluginInfo(self.path), window)