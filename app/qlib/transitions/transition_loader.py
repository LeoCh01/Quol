import logging
import os
import sys
import importlib

from globals import BASE_DIR
from qlib.windows.quol_window import QuolBaseWindow

logger = logging.getLogger(__name__)


class TransitionInfo:
    def __init__(self, path):
        self.path = path


class TransitionLoader:
    def __init__(self, name):
        self.name = name
        self.module = None
        self.path = f'{BASE_DIR}\\transitions\\{self.name}'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.cleanup()
        # Do not suppress exceptions
        return False

    def load(self):
        module_path = self.path + '\\transition.py'
        if not os.path.exists(module_path):
            logger.error(f'Script {self.name} does not exist at {module_path}.')
            module_path = f'{BASE_DIR}\\transitions\\rand\\transition.py'

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
                logger.exception('Error during transition module teardown')
            finally:
                # Remove the dynamically loaded module from sys.modules
                if self.name in sys.modules:
                    try:
                        del sys.modules[self.name]
                    except Exception:
                        logger.exception('Failed to remove transition module from sys.modules')
                self.module = None
