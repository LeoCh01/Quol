import time

from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QPushButton, QComboBox, QLineEdit, QHBoxLayout, QVBoxLayout

from res.paths import IMG_PATH
from windows.lib.custom_widgets import CustomWindow

import asyncio
import ollama


class MainWindow(CustomWindow):

    def __init__(self, wid, geometry=(730, 10, 170, 1)):
        super().__init__('Chat', wid, geometry)
        self.ollama_client = None

        self.prompt_layout = QVBoxLayout()
        self.config_layout = QHBoxLayout()

        self.ollama_btn = QPushButton("Activate")
        self.ai_list = QComboBox()
        self.ai_list.addItems(['GPT', 'Gemini', 'ollama'])
        self.prompt = QLineEdit()
        self.prompt.setPlaceholderText("prompt...")

        self.config_layout.addWidget(self.ollama_btn)
        self.config_layout.addWidget(self.ai_list)
        self.prompt_layout.addLayout(self.config_layout)
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
        QTimer.singleShot(0, self.ollama_chat)

    def activate_ollama(self):
        self.ollama_client = ollama.Client(host='http://localhost:11434')
        print('connected')

    def ollama_chat(self):
        if not self.ollama_client:
            self.activate_ollama()

        print('Question:', self.prompt.text())
        response = self.ollama_client.chat(
            model='gemma3',
            stream=True,
            messages=[{
                'role': 'user',
                'content': self.prompt.text(),
                'images': [IMG_PATH + 'screenshot.png']
            }]
        )

        for chunk in response:
            print(chunk['message']['content'], end='', flush=True)
