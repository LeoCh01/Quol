import logging
import os
import sys

from PySide6.QtWidgets import QApplication

from qlogging import initialize_logging
from globals import set_dir

BASE_DIR: str = None


def bootstrap_dependencies():
    from qlib_loader import load_all_modules
    load_all_modules()

    from qlib.app import App
    from qlib.launcher import AppLauncher
    from qlib.windows.loading_screen import LoadingScreen
    from qlib.updater import check_for_update

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
    logging.info('Starting Quol...')
    logging.info('Current working directory: %s', os.getcwd())

    global BASE_DIR
    if getattr(sys, "frozen", False):
        BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    set_dir(BASE_DIR)
    logging.info('Switched working directory: %s', BASE_DIR)


def main():
    setup_runtime_environment()

    App, AppLauncher, LoadingScreen, check_for_update = bootstrap_dependencies()

    quol_app = QApplication([])

    is_new, new, old = check_for_update()

    if is_new:
        launcher = AppLauncher(new, old, lambda: initialize_main_app(App, LoadingScreen))
        launcher.show()
    else:
        initialize_main_app(App, LoadingScreen)

    quol_app.exec()


if __name__ == '__main__':
    initialize_logging()
    main()
