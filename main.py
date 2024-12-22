import keyboard
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtWidgets import QApplication
from windows.test import Test
from windows.test2 import Test2

class App:
    def __init__(self):
        self.test = Test()
        self.test.setWindowFlags(self.test.windowFlags() | Qt.WindowStaysOnTopHint)
        self.test.show()

        self.test2 = Test2()
        self.test2.setWindowFlags(self.test2.windowFlags() | Qt.WindowStaysOnTopHint)
        self.test2.show()

        self.is_hidden = False

        keyboard.add_hotkey('`', self.toggle_windows, suppress=True)

    def toggle_windows(self):
        print("Toggling windows")
        if self.is_hidden:
            self.show_windows()
        else:
            self.hide_windows()

    def hide_windows(self):
        self.animate_window(self.test, QPoint(-self.test.width(), self.test.y()))
        self.animate_window(self.test2, QPoint(-self.test2.width(), self.test2.y()))
        self.is_hidden = True

    def show_windows(self):
        self.animate_window(self.test, QPoint(0, self.test.y()))
        self.animate_window(self.test2, QPoint(0, self.test2.y()))
        self.is_hidden = False

    def animate_window(self, window, end_pos):
        animation = QPropertyAnimation(window, b"pos")
        animation.setDuration(1000)  # Duration in milliseconds
        animation.setEndValue(end_pos)
        easing = QEasingCurve()
        animation.setEasingCurve(easing)
        animation.start()

if __name__ == "__main__":
    app = QApplication([])

    with open('style.qss', 'r') as f:
        stylesheet = f.read()
    app.setStyleSheet(stylesheet)

    application = App()

    app.exec()