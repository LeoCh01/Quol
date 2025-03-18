from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QPushButton, QComboBox, QLineEdit, QHBoxLayout, QVBoxLayout, QLabel, QApplication, QScrollArea

from res.paths import IMG_PATH
from windows.lib.custom_widgets import CustomWindow

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
        self.btn.clicked.connect(self.prompt_screen)
        self.layout.addWidget(self.btn)

        screen_geometry = QGuiApplication.primaryScreen().geometry()
        self.chat_window = ChatWindow(geometry=(screen_geometry.width() - 510, screen_geometry.height() - 610, 500, 600))
        self.toggle_signal.connect(self.chat_window.toggle_windows)

    def prompt_screen(self):
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
        self.chat_window.show()
        self.chat_window.clear_text()

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
            self.chat_window.add_text(chunk['message']['content'])


class ChatWindow(CustomWindow):
    def __init__(self, geometry=(0, 0, 0, 0)):
        super().__init__("Chat", add_close_btn=True)
        self.setObjectName("content")
        self.setGeometry(*geometry)

        self.chat_response = QLabel()
        self.chat_response.setWordWrap(True)
        self.chat_response.setAlignment(Qt.AlignTop)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.chat_response)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

    def add_text(self, text):
        self.chat_response.setText(self.chat_response.text() + text)
        self.chat_response.repaint()
        QApplication.processEvents()

    def clear_text(self):
        self.chat_response.setText('')
        self.chat_response.repaint()
        QApplication.processEvents()
