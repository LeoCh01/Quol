from PySide6.QtCore import QThread, Signal
import asyncio


class Worker(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, task, *args):
        super().__init__()
        self.task = task  # The function to run
        self.args = args  # Arguments for the task

    def run(self):
        # Running async code inside the QThread worker
        try:
            result = asyncio.run(self.task(*self.args))
            self.finished.emit(result)  # Emit results to UI thread
        except Exception as e:
            self.error.emit(str(e))  # Emit any error to UI thread
