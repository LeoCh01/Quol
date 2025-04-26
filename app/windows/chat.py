import base64
import datetime
import json

import requests

from PySide6.QtCore import QTimer, Qt, QRect, QUrl, QByteArray
from PySide6.QtGui import QGuiApplication
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtWidgets import QPushButton, QComboBox, QLineEdit, QHBoxLayout, QVBoxLayout, QApplication, \
    QScrollArea, QTextEdit, QCheckBox

from res.paths import IMG_PATH, CHAT_PATH
from windows.lib.custom_widgets import CustomWindow

import ollama

HISTORY = []


class MainWindow(CustomWindow):
    def __init__(self, wid, geometry=(730, 10, 190, 1)):
        super().__init__('Chat', wid, geometry)
        self.ollama_client = None

        self.network_manager = QNetworkAccessManager(self)

        self.chat_window = ChatWindow()
        self.toggle_signal.connect(self.chat_window.toggle_windows)
        self.chat_window.toggle_windows_2 = self.toggle_windows_2

        self.ai = AI(self.network_manager, self.chat_window)

        self.prompt_layout = QVBoxLayout()
        self.config_layout = QHBoxLayout()
        self.c2_layout = QHBoxLayout()

        self.model = QLineEdit()
        self.model.setPlaceholderText("model...")
        self.model.textChanged.connect(self.on_model_change)

        self.ai_list = QComboBox()
        self.ai_list.addItems(['gemini', 'ollama', 'groq'])
        self.ai_list.currentIndexChanged.connect(self.on_ai_change)

        self.prompt = QLineEdit()
        self.prompt.setPlaceholderText("prompt...")
        self.prompt.returnPressed.connect(self.send_prompt)

        self.btn = QPushButton("Send")
        self.btn.clicked.connect(self.send_prompt)

        self.img_cb = QCheckBox("Image")
        self.hist_clear = QPushButton("Clear History")
        self.hist_clear.clicked.connect(lambda: HISTORY.clear())

        self.config_layout.addWidget(self.model)
        self.config_layout.addWidget(self.ai_list)
        self.c2_layout.addWidget(self.img_cb)
        self.c2_layout.addWidget(self.hist_clear)
        self.prompt_layout.addLayout(self.config_layout)
        self.prompt_layout.addLayout(self.c2_layout)
        self.prompt_layout.addWidget(self.prompt)
        self.layout.addLayout(self.prompt_layout)
        self.layout.addWidget(self.btn)

        self.load_config()

    def on_model_change(self):
        self.config[self.ai_list.currentText()]['model'] = self.model.text()
        self.save_config()

    def on_ai_change(self):
        if self.ai_list.currentText() == 'gemini':
            self.model.setText(self.config['gemini']['model'])
        elif self.ai_list.currentText() == 'ollama':
            self.model.setText(self.config['ollama']['model'])
        elif self.ai_list.currentText() == 'groq':
            self.model.setText(self.config['groq']['model'])

    def send_prompt(self):
        if self.img_cb.isChecked():
            screen = QGuiApplication.primaryScreen()
            self.toggle_windows_2(True)
            screenshot = screen.grabWindow(0).toImage()
            self.toggle_windows_2(False)
            screenshot.save(IMG_PATH + 'screenshot.png')

        self.ai.is_img = self.img_cb.isChecked()
        self.ai.is_hist = True
        self.set_button_loading_state(True)
        QTimer.singleShot(0, self.start_chat)

    def start_chat(self):
        print('Question:', self.prompt.text())

        if self.ai_list.currentText() == 'ollama':
            self.ai.ollama(self.config['ollama']['model'], self.prompt.text())
        elif self.ai_list.currentText() == 'groq':
            print('groq')
            self.ai.groq(self.config['groq']['model'], self.prompt.text(), self.config['groq']['apikey'])
        elif self.ai_list.currentText() == 'gemini':
            self.ai.gemini(self.config['gemini']['model'], self.prompt.text(), self.config['gemini']['apikey'])

        self.set_button_loading_state(False)
        self.prompt.setText('')

    def set_button_loading_state(self, is_loading):
        if is_loading:
            self.btn.setText("")
        else:
            self.btn.setText("Send")

    def load_config(self):
        try:
            with open(CHAT_PATH + 'chat.json', 'r') as f:
                self.config = json.load(f)
                self.model.setText(self.config['gemini']['model'])
                self.img_cb.setChecked(self.config['config']['image'])

        except Exception as e:
            print("error :: ", e)

    def save_config(self):
        with open(CHAT_PATH + 'chat.json', 'w') as f:
            json.dump(self.config, f, indent=2)


class AI:
    def __init__(self, network_manager, chat_window):
        self.ollama_client = None
        self.network_manager = network_manager
        self.network_manager.finished.connect(self.handle_response)
        self.chat_window = chat_window
        self.current_type = None

        self.is_img = True
        self.is_hist = True
        self.text_content = ''
        self.buffer = b""
        self.reply = None

        with open(CHAT_PATH + 'chat.json', 'r') as f:
            self.config = json.load(f)
            self.max_hist = self.config['config']['max_history']

    def ollama(self, model, prompt):
        self.chat_window.set_text('Loading...')
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

            text = ''
            for chunk in response:
                text += chunk['message']['content']
                self.chat_window.set_text(text)
        except Exception as e:
            self.chat_window.set_text(f"Error: {e}")
        finally:
            self.chat_window.show()

    def gemini(self, model, prompt, key):
        self.chat_window.set_text('Loading...')

        if len(HISTORY) > self.max_hist * 2:
            HISTORY.pop(0)
            HISTORY.pop(0)

        key = key or 'APIKEY'
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        headers = {'Content-Type': 'application/json'}
        data = {'contents': []}

        if self.is_hist:
            for h in HISTORY:
                data['contents'].append({'role': h['role'], 'parts': [{'text': h['text']}]})

                if 'image' in h:
                    data['contents'][-1]['parts'].append(
                        {'inline_data': {'mime_type': 'image/jpeg', 'data': h['image']}}
                    )

        cur = {'role': 'user', 'parts': [{'text': prompt}]}

        if self.is_img:
            with open(IMG_PATH + 'screenshot.png', 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                cur['parts'].append({'inline_data': {'mime_type': 'image/jpeg', 'data': img_data}})

        data['contents'].append(cur)

        if self.is_hist:
            HISTORY.append({'role': 'user', 'text': prompt, 'image': img_data})
        with open(CHAT_PATH + 'gemini.log', 'a') as f:
            f.write(f"{datetime.datetime.now()}\nQ: {prompt}\n")

        request = QNetworkRequest(QUrl(url))
        for header, value in headers.items():
            request.setRawHeader(header.encode(), value.encode())

        json_data = json.dumps(data).encode('utf-8')
        self.current_type = "gemini"
        self.network_manager.post(request, QByteArray(json_data))

    def groq(self, model, prompt, key):
        self.chat_window.set_text('Loading...')

        if len(HISTORY) > self.max_hist * 2:
            HISTORY.pop(0)
            HISTORY.pop(0)

        key = key or 'APIKEY'
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {key}'}
        data = {"messages": [], "model": model, "stream": False}

        if self.is_hist:
            for h in HISTORY:
                data['messages'].append({'role': h['role'], 'content': [{'type': 'text', 'text': h['text']}]})

                if 'image' in h:
                    data['messages'][-1]['content'].append(
                        {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{h["image"]}'}}
                    )

        cur = {"role": "user", "content": [{"type": "text", "text": prompt}]}

        if self.is_img:
            with open(IMG_PATH + 'screenshot.png', 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                cur['content'].append({"type": "image_url", "image_url": {"url": f'data:image/jpeg;base64,{img_data}'}})

        data['messages'].append(cur)

        if self.is_hist:
            HISTORY.append({'role': 'user', 'text': prompt, 'image': img_data})
        with open(CHAT_PATH + 'groq.log', 'a') as f:
            f.write(f"{datetime.datetime.now()}\nQ: {prompt}\n")

        print('sending groq')
        request = QNetworkRequest(QUrl(url))
        for header, value in headers.items():
            request.setRawHeader(header.encode(), value.encode())

        json_data = json.dumps(data).encode('utf-8')
        self.current_type = "groq"
        self.reply = self.network_manager.post(request, QByteArray(json_data))

    def handle_response(self, reply: QNetworkReply):
        res = reply.readAll()
        res = res.data().decode()

        if self.current_type == "gemini":
            self.handle_gemini_response(res)
        elif self.current_type == "groq":
            self.handle_groq_response(res)

        reply.deleteLater()

    def handle_gemini_response(self, res):
        self.text_content = ''
        try:
            res = json.loads(res)
            if 'error' in res:
                raise Exception(f"Error: {res['error']['message']}")
            self.text_content = res['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            self.text_content = e
        finally:
            self.chat_window.set_text(self.text_content)
            if self.is_hist:
                HISTORY.append({'role': 'model', 'text': self.text_content})
            with open(CHAT_PATH + 'gemini.log', 'a') as f:
                f.write(f"A: {self.text_content.replace('\n\n', '\n')}\n\n")

    def handle_groq_response(self, res):
        self.text_content = ''
        try:
            for chunk in res:
                self.text_content += chunk.choices[0]['delta']['content']
                self.chat_window.set_text(self.text_content)
        except Exception as e:
            self.chat_window.set_text(f"Error: {e}")
        finally:
            if self.is_hist:
                HISTORY.append({'role': 'model', 'text': self.text_content})
            with open(CHAT_PATH + 'groq.log', 'a') as f:
                f.write(f"A: {self.text_content.replace('\n\n', '\n')}\n\n")


class ChatWindow(CustomWindow):
    def __init__(self):
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
        self.chat_response.setMarkdown(str(text))
        self.chat_response.repaint()
        QApplication.processEvents()

    def closeEvent(self, event):
        print("Window closed")
        super().closeEvent(event)
        self.set_text('')
        self.setGeometry(QRect(self.g[0], self.g[1], self.g[2], self.g[3]))
        HISTORY.clear()

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
