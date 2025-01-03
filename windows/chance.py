from PySide6.QtWidgets import QPushButton, QLabel, QGridLayout
import random

from components.custom_window import CustomWindow


class Chance(CustomWindow):
    def __init__(self, geometry):
        super().__init__('Chance', geometry)
        self.is_coin_flip = True

        self.grid_layout = QGridLayout()
        self.result_label = QLabel('Result will be shown here')
        self.coin_button = QPushButton('Coin Flip')
        self.dice_button = QPushButton('Dice Roll')
        self.action_button = QPushButton('Flip Coin')

        self.grid_layout.addWidget(self.result_label, 0, 0, 1, 2)
        self.grid_layout.addWidget(self.coin_button, 1, 0)
        self.grid_layout.addWidget(self.dice_button, 1, 1)
        self.grid_layout.addWidget(self.action_button, 2, 0, 1, 2)
        self.layout.addLayout(self.grid_layout)

        self.coin_button.clicked.connect(self.set_coin_flip)
        self.dice_button.clicked.connect(self.set_dice_roll)
        self.action_button.clicked.connect(self.perform_action)

        self.update_buttons()

    def set_coin_flip(self):
        self.is_coin_flip = True
        self.update_buttons()

    def set_dice_roll(self):
        self.is_coin_flip = False
        self.update_buttons()

    def update_buttons(self):
        if self.is_coin_flip:
            self.coin_button.setStyleSheet('background-color: #676')
            self.dice_button.setStyleSheet('')
            self.action_button.setText('Flip Coin')
        else:
            self.coin_button.setStyleSheet('')
            self.dice_button.setStyleSheet('background-color: #676')
            self.action_button.setText('Roll Dice')

    def perform_action(self):
        if self.is_coin_flip:
            result = 'Heads' if random.choice([True, False]) else 'Tails'
        else:
            result = f'Dice rolled: {random.randint(1, 6)}'
        self.result_label.setText(result)
