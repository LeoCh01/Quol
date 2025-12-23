import logging
import os
import sys
import importlib

from PySide6.QtCore import Signal

from lib.global_input_manager import GlobalInputManager
from lib.io_helpers import read_json, write_json


class ToolLoader:
    def __init__(self, name, tools_dir):
        self.name = name
        self.module = None
        self.path = os.path.abspath(os.getcwd() + f'\\{tools_dir}\\{name}')
        self._added_sys_paths = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.cleanup()
        # Do not suppress exceptions
        return False

    def load(self):
        module_path = os.path.join(self.path, 'window.py')

        if os.path.exists(module_path):
            if self.path not in sys.path:
                sys.path.insert(0, self.path)
                self._added_sys_paths.append(self.path)

            # load lib
            lib_path = os.path.join(self.path, 'lib')
            if os.path.isdir(lib_path) and lib_path not in sys.path:
                sys.path.insert(0, lib_path)
                self._added_sys_paths.append(lib_path)

            spec = importlib.util.spec_from_file_location(self.name, module_path)
            self.module = importlib.util.module_from_spec(spec)
            sys.modules[self.name] = self.module
            spec.loader.exec_module(self.module)
        else:
            logging.error(f'Script {self.name} does not exist at {module_path}.')
            return False

        return True

    def create_window(self, context, app=None):
        return self.module.MainWindow(WindowInfo(self.path), context)

    def cleanup(self):
        """Unload the tool module, call optional teardown, and restore sys.path."""
        # Attempt teardown and module removal
        if self.module is not None:
            try:
                if hasattr(self.module, 'teardown'):
                    self.module.teardown()
            except Exception:
                logging.exception('Error during tool module teardown')
            finally:
                if self.name in sys.modules:
                    try:
                        del sys.modules[self.name]
                    except Exception:
                        logging.exception('Failed to remove tool module from sys.modules')
                self.module = None

        # Remove any paths we added to sys.path
        for p in list(self._added_sys_paths):
            try:
                if p in sys.path:
                    sys.path.remove(p)
            except ValueError:
                # Path may already be removed; ignore
                pass
            finally:
                try:
                    self._added_sys_paths.remove(p)
                except ValueError:
                    pass


class SystemToolLoader(ToolLoader):
    def __init__(self):
        super().__init__('quol', '')
        self.path = f'{os.getcwd()}\\quol'

    def create_window(self, context, app=None):
        return self.module.MainWindow(app, WindowInfo(self.path), context)


class WindowInfo:
    def __init__(self, path):
        self.path = path
        self.config_path = path + '\\res\\config.json'

    def save_config(self, config):
        write_json(self.config_path, config)

    def load_config(self):
        return read_json(self.config_path)


class WindowContext:
    def __init__(self, toggle: Signal(bool, bool), toggle_tools, toggle_tools_instant, settings, transition_plugin, get_is_hidden, input_manager):
        self.toggle = toggle
        self.toggle_windows = toggle_tools
        self.toggle_windows_instant = toggle_tools_instant
        self.transition_plugin = transition_plugin
        self.settings = settings
        self.get_is_hidden = get_is_hidden
        self.input_manager: GlobalInputManager = input_manager
