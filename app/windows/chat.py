import base64
import json
import re

import requests

from PySide6.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QPushButton, QComboBox, QLineEdit, QHBoxLayout, QVBoxLayout, QApplication, \
    QScrollArea, QMessageBox, QTextEdit

from res.paths import IMG_PATH, CHAT_PATH
from windows.lib.custom_widgets import CustomWindow

import ollama


class MainWindow(CustomWindow):

    def __init__(self, wid, geometry=(730, 10, 170, 1)):
        super().__init__('Chat', wid, geometry)
        self.ollama_client = None

        self.prompt_layout = QVBoxLayout()
        self.config_layout = QHBoxLayout()

        self.model = QLineEdit()
        self.model.setPlaceholderText("model...")
        self.model.textChanged.connect(self.on_model_change)

        self.ai_list = QComboBox()
        self.ai_list.addItems(['Gemini', 'ollama', 'GPT'])
        self.ai_list.currentIndexChanged.connect(self.on_ai_change)

        item = self.ai_list.model().item(2)
        font = item.font()
        item.setEnabled(False)
        font.setStrikeOut(True)
        item.setFont(font)

        self.prompt = QLineEdit()
        self.prompt.setPlaceholderText("prompt...")
        self.prompt.returnPressed.connect(self.send_prompt)

        self.config_layout.addWidget(self.model)
        self.config_layout.addWidget(self.ai_list)
        self.prompt_layout.addLayout(self.config_layout)
        self.prompt_layout.addWidget(self.prompt)
        self.layout.addLayout(self.prompt_layout)

        self.btn = QPushButton("Send")
        self.btn.clicked.connect(self.send_prompt)
        self.layout.addWidget(self.btn)

        self.ai = AI()
        self.chat_window = ChatWindow(wid)
        self.load_config()

    def on_model_change(self):
        self.config[self.ai_list.currentText()]['model'] = self.model.text()
        self.save_config()

    def on_ai_change(self, index):
        if self.ai_list.currentText() == 'Gemini':
            self.model.setText(self.config['Gemini']['model'])
        elif self.ai_list.currentText() == 'ollama':
            self.model.setText(self.config['ollama']['model'])
        elif self.ai_list.currentText() == 'GPT':
            pass

    def send_prompt(self):
        screen = QGuiApplication.primaryScreen()
        self.toggle_windows_2(True)
        screenshot = screen.grabWindow(0).toImage()
        self.toggle_windows_2(False)
        screenshot.save(IMG_PATH + 'screenshot.png')

        self.set_button_loading_state(True)
        QTimer.singleShot(0, self.start_chat)

    def start_chat(self):
        print('Question:', self.prompt.text())
        self.set_button_loading_state(False)

        if self.ai_list.currentText() == 'ollama':
            self.ai.ollama(self.config['ollama']['model'], self.prompt.text(), self.chat_window)
        elif self.ai_list.currentText() == 'GPT':
            pass
        elif self.ai_list.currentText() == 'Gemini':
            self.ai.gemini(self.config['Gemini']['model'], self.prompt.text(), self.config['Gemini']['apikey'], self.chat_window)

        self.prompt.setText('')

    def set_button_loading_state(self, is_loading):
        if is_loading:
            self.btn.setText("loading...")
        else:
            self.btn.setText("Send")

    def load_config(self):
        try:
            with open(CHAT_PATH, 'r') as f:
                self.config = json.load(f)
                self.model.setText(self.config['Gemini']['model'])

        except Exception as e:
            print("error :: ", e)

    def save_config(self):
        with open(CHAT_PATH, 'w') as f:
            json.dump(self.config, f, indent=2)


class AI:
    def __init__(self):
        self.ollama_client = None

    def ollama(self, model, prompt, window):
        if not self.ollama_client:
            self.ollama_client = ollama.Client(host='http://localhost:11434')

        try:
            response = self.ollama_client.chat(
                model=model,
                stream=True,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [IMG_PATH + 'screenshot.png']
                }]
            )
        except Exception as e:
            window.set_text(f"Error: {e}")
            window.show()
            return

        window.show()

        text = ''
        for chunk in response:
            text += chunk['message']['content']
            window.set_text(text)

    def gemini(self, model, prompt, key, window):
        with open(IMG_PATH + 'screenshot.png', 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')

        key = key or 'APIKEY'
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": img_data
                        }
                    }
                ]
            }]
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code != 200:
                raise Exception(f"{response.status_code}\n\n{response.text}")
            response = response.json()
            window.set_text('')
            window.set_text(response['candidates'][0]['content']['parts'][0]['text'])
        except Exception as e:
            window.set_text(f"Error: {e}")

        window.show()


class ChatWindow(CustomWindow):
    def __init__(self, wid):
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        self.g = (screen_geometry.width() - 510, screen_geometry.height() - 610, 500, 600)
        super().__init__("Chat", -1, geometry=self.g, add_close_btn=True)

        # self.chat_response = QTextBrowser()
        self.chat_response = QTextEdit(readOnly=True)
        self.chat_response.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.chat_response)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

    def set_text(self, text):
        self.chat_response.setMarkdown(text)
        self.chat_response.repaint()
        QApplication.processEvents()

    def animate_up(self):
        self.animation = QPropertyAnimation(self, b'geometry')
        self.animation.setDuration(1000)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().translated(0, -610))
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def closeEvent(self, event):
        print("Window closed")
        super().closeEvent(event)
        self.set_text('')
        self.setGeometry(QRect(self.g[0], self.g[1], self.g[2], self.g[3]))

    @staticmethod
    def get_styled_html(html):
        return f"""
        <html>
        <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
            }}
            .code-container {{
                max-width: 100%;
                overflow-x: auto;  /* Scrollbar only inside the code block */
                padding: 10px;
                border-radius: 5px;
            }}
            pre {{
                white-space: pre;  /* Keeps newlines */
                margin: 0;  /* Prevents extra spacing */
                font-family: monospace;
            }}
            code {{
                font-family: monospace;
            }}
        </style>
        </head>
        <body>
        {html}
        </body>
        </html>
        """
