import os
import asyncio
import logging
import sys

from PySide6.QtWidgets import QApplication
from qasync import QEventLoop
from lib.app import App


def initialize_app():
    print('Starting Quol...')
    app = QApplication([])

    # set working directory
    print('Current working directory:', os.getcwd())
    base_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(base_dir)
    print('Switched working directory:', os.getcwd())

    logging.basicConfig(
        filename='res/error.log',
        filemode='a',
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    # try:
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    application = App()

    with loop:
        loop.run_forever()
    #
    # except Exception as e:
    #     print('error :: ', e)
    #     logging.error(e, exc_info=True)


if __name__ == '__main__':
    initialize_app()
