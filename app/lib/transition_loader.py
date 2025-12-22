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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.cleanup()
        # Do not suppress exceptions
        return False

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

    def cleanup(self):
        """Unload the transition module and perform optional teardown."""
        if self.module is not None:
            try:
                if hasattr(self.module, 'teardown'):
                    # Allow transition module to release resources if it defines a teardown hook
                    self.module.teardown()
            except Exception:
                logging.exception('Error during transition module teardown')
            finally:
                # Remove the dynamically loaded module from sys.modules
                if self.name in sys.modules:
                    try:
                        del sys.modules[self.name]
                    except Exception:
                        logging.exception('Failed to remove transition module from sys.modules')
                self.module = None
