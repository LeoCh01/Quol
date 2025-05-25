import base64
import datetime
import json
import os

from markdown import markdown
from pygments.formatters.html import HtmlFormatter
from PySide6.QtCore import QTimer, QRect, QUrl, QByteArray
from PySide6.QtGui import QGuiApplication
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtWidgets import QPushButton, QComboBox, QLineEdit, QHBoxLayout, QVBoxLayout, QApplication, QTextBrowser

from windows.custom_widgets import CustomWindow

import ollama

BASE_PATH = os.path.dirname(__file__)
HISTORY = []
test_response = None


class MainWindow(CustomWindow):
    def __init__(self, wid, geometry=(730, 10, 190, 1)):
        super().__init__('Chat', wid, geometry, path=BASE_PATH)
        self.ollama_client = None

        self.network_manager = QNetworkAccessManager(self)

        self.chat_window = ChatWindow()
        self.toggle_signal.connect(self.chat_window.toggle_windows)
        self.chat_window.toggle_windows_2 = self.toggle_windows_2

        self.ai = AI(self.network_manager, self.chat_window, self.config)

        self.ai_list = QComboBox()
        self.ai_list.addItems(['gemini', 'ollama', 'groq'])

        self.hist_clear = QPushButton('Clear History')
        self.hist_clear.clicked.connect(lambda: HISTORY.clear())

        self.prompt = QLineEdit()
        self.prompt.setPlaceholderText('prompt...')
        self.prompt.returnPressed.connect(self.send_prompt)

        self.btn = QPushButton('Send')
        self.btn.clicked.connect(self.send_prompt)

        self.top_layout = QHBoxLayout()
        self.prompt_layout = QVBoxLayout()

        self.top_layout.addWidget(self.ai_list)
        self.top_layout.addWidget(self.hist_clear)
        self.prompt_layout.addWidget(self.prompt)
        self.layout.addLayout(self.top_layout)
        self.layout.addLayout(self.prompt_layout)
        self.layout.addWidget(self.btn)

    def send_prompt(self):
        self.ai.is_img = self.config['config']['image']
        self.ai.is_hist = self.config['config']['history']

        if self.config['config']['image']:
            screen = QGuiApplication.primaryScreen()
            self.toggle_windows_2(True)
            screenshot = screen.grabWindow(0).toImage()
            self.toggle_windows_2(False)
            screenshot.save(BASE_PATH + '/res/img/screenshot.png')

        self.set_button_loading_state(True)
        QTimer.singleShot(0, self.start_chat)

    def start_chat(self):
        print('Question:', self.prompt.text())

        if self.ai_list.currentText() == 'ollama':
            self.ai.prompt('ollama', {'prompt': self.prompt.text(), 'model': self.config['ollama']['model']})
        else:
            data = {
                'prompt': self.prompt.text(),
                'model': self.config[self.ai_list.currentText()]['model'],
                'apikey': self.config[self.ai_list.currentText()]['apikey']
            }
            self.ai.prompt(self.ai_list.currentText(), data)

        self.set_button_loading_state(False)
        self.prompt.setText('')

    def set_button_loading_state(self, is_loading):
        if is_loading:
            self.btn.setText('')
        else:
            self.btn.setText('Send')


class AI:
    def __init__(self, network_manager, chat_window, config):
        self.network_manager = network_manager
        self.config = config
        self.chat_window = chat_window
        self.ollama_client = None
        self.network_manager.finished.connect(self.handle_response)
        self.current_type = None

        self.is_img = True
        self.is_hist = True
        self.text_content = ''

        self.max_hist = self.config['config']['max_history']

    def prompt(self, model, d):
        url = headers = data = None
        self.chat_window.set_text('Loading...')
        self.chat_window.show()

        if test_response:
            self.chat_window.set_text(test_response)
            return

        if model == 'ollama':
            self.ollama(d['model'], d['prompt'])
            return
        elif model == 'gemini':
            url, headers, data = self.gemini(d['model'], d['prompt'], d['apikey'])
        elif model == 'groq':
            url, headers, data = self.groq(d['model'], d['prompt'], d['apikey'])

        request = QNetworkRequest(QUrl(str(url)))
        for header, value in headers.items():
            request.setRawHeader(header.encode(), value.encode())

        json_data = json.dumps(data).encode('utf-8')
        self.current_type = model
        self.network_manager.post(request, QByteArray(json_data))

    def add_history(self, model, text, img_data, is_user):
        if self.is_hist:
            if is_user:
                HISTORY.append({'role': 'user', 'text': text})
                if self.is_img:
                    HISTORY[-1]['image'] = img_data
            else:
                HISTORY.append({'role': 'model', 'text': text})

        with open(BASE_PATH + f'/res/{model}.log', 'a', encoding='utf-8') as f:
            if is_user:
                f.write(f'{datetime.datetime.now()}\nQ: {text}\n')
            else:
                f.write(f'A: {text.replace('\n\n', '\n')}\n\n')

        if len(HISTORY) > (self.max_hist - 1) * 2:
            HISTORY.pop(0)

    def ollama(self, model, prompt):
        if not self.ollama_client:
            self.ollama_client = ollama.Client(host='http://localhost:11434')

        try:
            response = self.ollama_client.chat(
                model=model,
                stream=True,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [BASE_PATH + '/res/img/screenshot.png']
                }]
            )

            text = ''
            for chunk in response:
                text += chunk['message']['content']
                self.chat_window.set_text(text)
        except Exception as e:
            self.chat_window.set_text(f'Error: {e}')

    def gemini(self, model, prompt, key):
        key = key or 'APIKEY'
        url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}'
        headers = {'Content-Type': 'application/json'}
        data = {'contents': []}
        img_data = None

        if self.is_hist:
            for h in HISTORY:
                data['contents'].append({'role': h['role'], 'parts': [{'text': h['text']}]})

                if 'image' in h:
                    data['contents'][-1]['parts'].append(
                        {'inline_data': {'mime_type': 'image/jpeg', 'data': h['image']}}
                    )

        cur = {'role': 'user', 'parts': [{'text': prompt}]}

        if self.is_img:
            with open(BASE_PATH + '/res/img/screenshot.png', 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                cur['parts'].append({'inline_data': {'mime_type': 'image/jpeg', 'data': img_data}})

        data['contents'].append(cur)
        self.add_history('gemini', prompt, img_data, True)
        return url, headers, data

    def groq(self, model, prompt, key):
        key = key or 'APIKEY'
        url = 'https://api.groq.com/openai/v1/chat/completions'
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {key}'}
        data = {'messages': [], 'model': model, 'stream': False}
        img_data = None

        if self.is_hist:
            for h in HISTORY:
                if h['role'] == 'user':
                    data['messages'].append({'role': 'user', 'content': [{'type': 'text', 'text': h['text']}]})

                    if 'image' in h:
                        data['messages'][-1]['content'].append(
                            {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{h['image']}'}}
                        )
                else:
                    data['messages'].append({'role': 'assistant', 'content': h['text']})

        cur = {'role': 'user', 'content': [{'type': 'text', 'text': prompt}]}

        if self.is_img:
            with open(BASE_PATH + '/res/img/screenshot.png', 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                cur['content'].append({'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{img_data}'}})

        data['messages'].append(cur)
        self.add_history('groq', prompt, img_data, True)
        return url, headers, data

    def handle_response(self, reply: QNetworkReply):
        res = reply.readAll()
        res = res.data().decode()
        self.text_content = ''
        try:
            res = json.loads(res)
            if 'error' in res:
                raise Exception(f'Error: {res['error']['message']}')

            if self.current_type == 'gemini':
                self.text_content = res['candidates'][0]['content']['parts'][0]['text']
            elif self.current_type == 'groq':
                self.text_content = res['choices'][0]['message']['content']

            self.chat_window.set_text(self.text_content)
            self.add_history(self.current_type, self.text_content, None, False)

        except Exception as e:
            self.text_content = str(e)
            self.chat_window.set_text(self.text_content)
            HISTORY.clear()

        reply.deleteLater()


class ChatWindow(CustomWindow):
    def __init__(self):
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        self.g = (screen_geometry.width() - 510, screen_geometry.height() - 610, 500, 600)
        super().__init__('Chat', -1, geometry=self.g, add_close_btn=True)

        self.chat_response = QTextBrowser()
        self.chat_response.setOpenExternalLinks(True)
        self.chat_response.setReadOnly(True)
        self.layout.addWidget(self.chat_response, stretch=1)

    def set_text(self, text):
        html = self.markdown_to_html(str(text))
        self.chat_response.setHtml(html)
        self.chat_response.repaint()
        QApplication.processEvents()

    def closeEvent(self, event):
        print('Window closed')
        super().closeEvent(event)
        self.set_text('')
        self.setGeometry(QRect(self.g[0], self.g[1], self.g[2], self.g[3]))
        HISTORY.clear()

    @staticmethod
    def markdown_to_html(md_text):
        html_body = markdown(md_text, extensions=["fenced_code", "codehilite"])
        css = HtmlFormatter(style="monokai").get_style_defs('.codehilite')

        styling = f"""
            <style type="text/css">
            {css}
            .content-wrapper {{
                padding: 10px;
            }}
            body {{
                background-color: #333;
                color: white;
                font-size: 13px;
                letter-spacing: 0.2px;
                line-height: 1.2;
            }}
            .codehilite pre {{
                margin: 0;
                padding: 10px;
                background: #262626;
                line-height: 1;
            }}
            code {{
                background-color: #262626;
                padding:10px;
                border-radius: 4px;
            }}
            </style>
        """

        html_text = f"""
            <html>
            <head>{styling}</head>
            <body>
                {html_body}
            </body>
            </html>
        """

        return html_text
