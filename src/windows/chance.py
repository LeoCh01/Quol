from PySide6 import QtCore
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QPushButton, QLabel, QGridLayout
from PySide6.QtGui import QPixmap, Qt, QMovie
import random
from src.components.custom_window import CustomWindow

COIN = 'res/img/coin-x.png'
COIN_IMAGES = ['res/img/coin-h.png', 'res/img/coin-t.png']
DICE = 'res/img/dice-x.png'
DICE_IMAGES = ['res/img/dice-1.png', 'res/img/dice-2.png', 'res/img/dice-3.png', 'res/img/dice-4.png', 'res/img/dice-5.png', 'res/img/dice-6.png']


class Chance(CustomWindow):
    def __init__(self, wid, geometry=(390, 10, 180, 1)):
        super().__init__('Chance', wid, geometry)
        self.is_coin_flip = True

        self.grid_layout = QGridLayout()
        self.result_label = QLabel()
        self.result_label.setPixmap(QPixmap(COIN))
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
        self.is_running = False

    def set_coin_flip(self):
        if self.is_running:
            return
        self.is_coin_flip = True
        self.update_buttons()

    def set_dice_roll(self):
        if self.is_running:
            return
        self.is_coin_flip = False
        self.update_buttons()

    def update_buttons(self):
        if self.is_coin_flip:
            self.coin_button.setStyleSheet('background-color: #696')
            self.dice_button.setStyleSheet('')
            self.result_label.setPixmap(QPixmap(COIN))
        else:
            self.coin_button.setStyleSheet('')
            self.dice_button.setStyleSheet('background-color: #696')
            self.result_label.setPixmap(QPixmap(DICE))

    def perform_action(self, event):
        if self.is_running:
            return
        self.is_running = True

        if self.is_coin_flip:
            self.flip_animation(random.sample(COIN_IMAGES, 2), random.randint(14, 15))
        else:
            self.flip_animation(random.sample(DICE_IMAGES, 6), random.randint(12, 16))

    def flip_animation(self, frames, total_flips, initial_interval=10):
        def update_flip():
            if self.flip_counter < total_flips:
                current_frame = frames[self.flip_counter % len(frames)]
                self.result_label.setPixmap(QPixmap(current_frame))
                self.flip_counter += 1

                new_interval = initial_interval + (self.flip_counter * 20)
                self.flip_timer.setInterval(new_interval)
            else:
                self.flip_timer.stop()
                self.confetti()

        self.flip_counter = 0
        self.flip_timer = QTimer(self)
        self.flip_timer.timeout.connect(update_flip)
        self.flip_timer.start(initial_interval)

    def confetti(self):
        self.confetti_label = QLabel(self)
        self.confetti_label.setAlignment(Qt.AlignCenter)
        self.grid_layout.addWidget(self.confetti_label, 0, 0, 1, 2)

        confetti_movie = QMovie("res/img/confetti2.gif")
        confetti_movie.setSpeed(150)
        confetti_movie.setScaledSize(QtCore.QSize(160, 80))

        self.confetti_label.setMovie(confetti_movie)
        confetti_movie.start()

        QTimer.singleShot(1700, self.hide_confetti)

    def hide_confetti(self):
        self.is_running = False
        self.grid_layout.removeWidget(self.confetti_label)
        self.confetti_label.deleteLater()

