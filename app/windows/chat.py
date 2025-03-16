from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QLabel, QPushButton, QComboBox, QLineEdit, QHBoxLayout, QVBoxLayout

from res.paths import IMG_PATH
from windows.lib.custom_widgets import CustomWindow

import requests


class MainWindow(CustomWindow):

    def __init__(self, wid, geometry=(730, 10, 170, 1)):
        super().__init__('Chat', wid, geometry)

        # self.api_key_label = QLabel("API Key:")
        # self.api_key = QLineEdit()
        # self.api_key.setEchoMode(QLineEdit.Password)
        # self.api_key_label2 = QLabel("API key 2")
        # self.api_key2 = QLineEdit()
        # self.api_key.setEchoMode(QLineEdit.Password)
        #
        # self.apis_layout = QVBoxLayout()
        # self.api_name_layout = QHBoxLayout()
        # self.api_name_layout.addWidget(self.api_key_label)
        # self.api_name_layout.addWidget(self.api_key_label2)
        # self.api_input_layout = QHBoxLayout()
        # self.api_input_layout.addWidget(self.api_key)
        # self.api_input_layout.addWidget(self.api_key2)
        # self.apis_layout.addLayout(self.api_name_layout)
        # self.apis_layout.addLayout(self.api_input_layout)
        # self.layout.addLayout(self.apis_layout)

        self.prompt_layout = QVBoxLayout()
        self.row_layout = QHBoxLayout()

        self.prompt_label = QLabel("Prompt:")
        self.ai_list = QComboBox()
        self.ai_list.addItems(['GPT', 'Gemini', 'aaa'])
        self.prompt = QLineEdit()
        self.prompt.setPlaceholderText("prompt...")

        self.row_layout.addWidget(self.prompt_label)
        self.row_layout.addWidget(self.ai_list)
        self.prompt_layout.addLayout(self.row_layout)
        self.prompt_layout.addWidget(self.prompt)
        self.layout.addLayout(self.prompt_layout)

        self.btn = QPushButton("Send")
        self.btn.clicked.connect(self.get_screen_text)
        self.layout.addWidget(self.btn)

    def get_screen_text(self):
        screen = QGuiApplication.primaryScreen()
        self.toggle_windows_2(True)
        screenshot = screen.grabWindow(0).toImage()
        self.toggle_windows_2(False)
        screenshot.save(IMG_PATH + 'screenshot.png')

        files = {'file': open(IMG_PATH + 'screenshot.png', 'rb')}
        payload = {
            'apikey': 'K81022411788957',
            'language': 'eng',
        }

        # res = requests.post('https://api.ocr.space/parse/image', data=payload, files=files)
        # text = res.json()
        # return text
