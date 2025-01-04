from PySide6.QtCore import QThread
from PySide6.QtWidgets import QPushButton, QLabel, QGridLayout, QApplication
from PySide6.QtGui import QPixmap, Qt
import random

from components.custom_window import CustomWindow
HEADS_IMAGE = 'res/img/coin-h.png'
TAILS_IMAGE = 'res/img/coin-t.png'

class Chance(CustomWindow):
    def __init__(self, geometry):
        super().__init__('Chance', geometry)
        self.is_coin_flip = True

        self.grid_layout = QGridLayout()
        self.result_label = QLabel()
        self.result_label.setPixmap(QPixmap(HEADS_IMAGE))
        self.result_label.setAlignment(Qt.AlignCenter)
        self.coin_button = QPushButton('Coin')
        self.dice_button = QPushButton('Dice')

        self.grid_layout.addWidget(self.result_label, 0, 0, 1, 2)
        self.grid_layout.addWidget(self.coin_button, 1, 0)
        self.grid_layout.addWidget(self.dice_button, 1, 1)
        self.layout.addLayout(self.grid_layout)

        self.coin_button.clicked.connect(self.set_coin_flip)
        self.dice_button.clicked.connect(self.set_dice_roll)
        self.result_label.mousePressEvent = self.perform_action

        self.update_buttons()

    def set_coin_flip(self):
        self.is_coin_flip = True
        self.update_buttons()

    def set_dice_roll(self):
        self.is_coin_flip = False
        self.update_buttons()

    def update_buttons(self):
        if self.is_coin_flip:
            self.coin_button.setStyleSheet('background-color: #696')
            self.dice_button.setStyleSheet('')
            self.result_label.setPixmap(QPixmap(HEADS_IMAGE))
        else:
            self.coin_button.setStyleSheet('')
            self.dice_button.setStyleSheet('background-color: #696')
            self.result_label.setPixmap(QPixmap('path/to/dice/image.png'))

    def perform_action(self, event):
        if self.is_coin_flip:
            for i in range(1, 10):
                self.result_label.setPixmap(QPixmap(HEADS_IMAGE))
                QApplication.processEvents()
                QThread.msleep(50 + i * 20)
                self.result_label.setPixmap(QPixmap(TAILS_IMAGE))
                QApplication.processEvents()
                QThread.msleep(50 + i * 20)

            if random.choice([True, False]):
                self.result_label.setPixmap(QPixmap(HEADS_IMAGE))
        else:
            dice_value = random.randint(1, 6)

