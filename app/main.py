import logging
import os
import sys

from PySide6.QtWidgets import QApplication

from qlib_loader import load_all_modules
load_all_modules()

from qlib.app import App
from qlib.windows.loading_screen import LoadingScreen

from launcher import AppLauncher
from updater import check_for_update


def initialize_logging():
    logging.basicConfig(
        filename='error.log',
        filemode='a',
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logging.getLogger().addHandler(logging.StreamHandler())


def initialize_main_app():
    try:
        splash = LoadingScreen()
        splash.show()
        splash.raise_()

        app_instance = App()

        splash.close()
        return app_instance

    except Exception as e:
        logging.error(f"Failed to initialize main app :: {e}", exc_info=True)
        return None


def main():
    print('Starting Quol...')
    print('Current working directory:', os.getcwd())
    base_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(base_dir)
    print('Switched working directory:', os.getcwd())

    initialize_logging()

    app = QApplication([])

    is_new, new, old = check_for_update()

    if is_new:
        launcher = AppLauncher(new, old, initialize_main_app)
        launcher.show()
    else:
        initialize_main_app()

    app.exec()


if __name__ == '__main__':
    main()
