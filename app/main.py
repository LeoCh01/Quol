import logging
import os
import sys

from PySide6.QtWidgets import QApplication

from qlogging import initialize_logging
from globals import set_dir
from qlib.worker import Worker

BASE_DIR: str = None


def bootstrap_dependencies():
    from qlib_loader import load_all_modules
    load_all_modules()

    from qlib.app import App
    from qlib.windows.loading_screen import LoadingScreen
    from launcher import AppLauncher
    from updater import check_for_update

    return App, AppLauncher, LoadingScreen, check_for_update


def initialize_main_app(App, LoadingScreen):
    try:
        splash = LoadingScreen()
        splash.show()
        splash.raise_()

        app_instance = App()

        splash.close()
        return app_instance

    except Exception as e:
        logging.error(f'Failed to initialize main app :: {e}', exc_info=True)
        return None


def setup_runtime_environment():
    print('Starting Quol...')

    global BASE_DIR
    if getattr(sys, "frozen", False):
        BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    set_dir(BASE_DIR)


if __name__ == '__main__':
    setup_runtime_environment()
    initialize_logging(BASE_DIR)

    App, AppLauncher, LoadingScreen, check_for_update = bootstrap_dependencies()

    quol_app = QApplication([])

    # Run check_for_update asynchronously to avoid blocking UI
    def on_update_check_complete(result):
        is_new, new, old = result
        if is_new:
            launcher = AppLauncher(new, old, lambda: initialize_main_app(App, LoadingScreen))
            launcher.show()
        else:
            initialize_main_app(App, LoadingScreen)

    def on_update_check_error(error):
        logging.error(f'Update check error: {error}')
        initialize_main_app(App, LoadingScreen)

    worker = Worker(check_for_update)
    worker.finished.connect(on_update_check_complete)
    worker.error.connect(on_update_check_error)
    worker.start()

    quol_app.exec()
