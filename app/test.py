import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Signal, Slot
from lib.global_input_manager import GlobalInputManager


class MainWindow(QWidget):
    key_pressed = Signal(str)
    hotkey_pressed = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signal Example")
        self.setGeometry(200, 200, 300, 100)

        self.label = QLabel("Press 'b' globally", self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.key_pressed.connect(self.say_hello)
        # Global input manager
        self.input_manager = GlobalInputManager()
        self.input_manager.start()

        self.key1 = self.input_manager.add_key_press_listener(self.on_key_press, suppressed=('a', 'h'))
        self.key2 = self.input_manager.add_hotkey('ctrl+c', self.say_bye)

    def on_key_press(self, key_str):
        if key_str.lower() in 'abc':
            self.key_pressed.emit(key_str)
        elif key_str.lower() == 'd':
            self.input_manager.remove_hotkey(self.key2)
            print('removed key listener')

    @Slot(str)
    def say_hello(self, c):
        print(f'pressed {c}')
        self.label.setText(f'pressed {c}')

    @Slot()
    def say_bye(self):
        print('bye')
        self.label.setText('bye')

    def closeEvent(self, event):
        self.input_manager.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
