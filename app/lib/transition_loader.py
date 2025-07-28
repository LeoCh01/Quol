import logging
import os
import sys
import importlib

from lib.quol_window import QuolBaseWindow


class TransitionInfo:
    def __init__(self, path):
        self.path = path


class TransitionLoader:
    def __init__(self, name):
        self.name = name
        self.module = None
        self.path = f'{os.getcwd()}\\transitions\\{self.name}'

    def load(self):
        module_path = self.path + '\\transition.py'
        if not os.path.exists(module_path):
            logging.error(f'Script {self.name} does not exist at {module_path}.')
            module_path = f'{os.getcwd()}\\transitions\\rand\\transition.py'

        spec = importlib.util.spec_from_file_location(self.name, module_path)
        self.module = importlib.util.module_from_spec(spec)
        sys.modules[self.name] = self.module
        spec.loader.exec_module(self.module)

    def create_transition(self, window: QuolBaseWindow):
        return self.module.Transition(TransitionInfo(self.path), window)
