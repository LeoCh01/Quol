from PySide6.QtWidgets import QApplication
from windows.test import Test
from windows.test2 import Test2

if __name__ == "__main__":
    app = QApplication([])

    test = Test()
    test.show()

    # test2 = Test2()
    # test2.show()

    app.exec()
