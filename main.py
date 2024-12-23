import keyboard
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import QApplication
from windows.test import Test
from windows.test2 import Test2
from windows.info import Info


class App(QObject):
    toggle = Signal(bool)

    def __init__(self):
        super().__init__()
        self.windows = [
            Info("Info", (10, 10, 200, 1)),
            Test("Test Window", (10, 90, 200, 1)),
            Test2("Test Window 2", (220, 10, 200, 1))
        ]
        self.is_hidden = False

        for window in self.windows:
            self.toggle.connect(window.toggle_windows)

            window.show()

        keyboard.add_hotkey('`', self.toggle_windows, suppress=True)

    def toggle_windows(self):
        self.toggle.emit(self.is_hidden)
        self.is_hidden = not self.is_hidden


if __name__ == "__main__":
    app = QApplication([])

    with open('style.qss', 'r') as f:
        stylesheet = f.read()
    app.setStyleSheet(stylesheet)

    application = App()
    app.exec()
