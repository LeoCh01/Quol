import base64
import datetime

import httpx
import re
from pynput.mouse import Controller, Button

from markdown import markdown
from pygments.formatters.html import HtmlFormatter
from PySide6.QtCore import QTimer, QRect
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QPushButton, QComboBox, QLineEdit, QHBoxLayout, QVBoxLayout, QApplication, QTextBrowser
from qasync import asyncSlot
import ollama

from lib.quol_window import QuolMainWindow, QuolSubWindow
from lib.window_loader import WindowInfo, WindowContext

HISTORY = []
test_response = [""]




class MainWindow(QuolMainWindow):
    def __init__(self, window_info: WindowInfo, window_context: WindowContext):
        super().__init__('Chat', window_info, window_context, default_geometry=(730, 10, 190, 1))
        self.ollama_client = None

        with open(window_info.path + '/test_response.txt', 'r') as f:
            test_response[0] = f.read().strip()

        self.chat_window = ChatWindow(self)
        self.window_context.toggle.connect(self.chat_window.toggle_windows)
        self.window_context.toggle.connect(self.focus)

        self.ai = AI(self, self.chat_window)
        self.ai_list = QComboBox()
        self.ai_list.addItems(['gemini', 'ollama', 'groq'])

        self.hist_clear = QPushButton('Clear History')
        self.hist_clear.clicked.connect(self.clear_history)

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

    def clear_history(self):
        self.chat_window.set_text('')
        HISTORY.clear()

    def focus(self):
        if self.config['config']['auto_focus'] and not self.window_context.get_is_hidden():
            QTimer.singleShot(210, self._focus_action)

    def _focus_action(self):
        if self.window_context.get_is_hidden():
            return

        mouse = Controller()
        cur = mouse.position
        sf = QGuiApplication.primaryScreen().devicePixelRatio()

        mouse.position = ((self.x() + 20) * sf, (self.y() + 80) * sf)
        mouse.click(Button.left, 1)
        mouse.position = [cur[0], cur[1]]

    def send_prompt(self):
        self.ai.is_img = self.config['config']['image']
        self.ai.is_hist = self.config['config']['history']

        if self.config['config']['image']:
            screen = QGuiApplication.primaryScreen()
            self.window_context.toggle_windows_instant(True)
            screenshot = screen.grabWindow(0).toImage()
            self.window_context.toggle_windows_instant(False)
            screenshot.save(self.window_info.path + '/res/img/screenshot.png')

        self.set_button_loading_state(True)
        QTimer.singleShot(0, self.start_chat)

    def start_chat(self):
        s = self.prompt.text().split()
        t = self.prompt.text()

        if s and s[0] in self.config['commands']:
            t = self.config['commands'][s[0]]
            for i in range(1, len(s)):
                t = re.sub(r'\{' + str(i - 1) + r'(?::[^}]*)?}', s[i], t)
            t = re.sub(r'\{(\d+):([^}]*)}', r'\2', t)
            t = re.sub(r'\{\d+}', '', t)

        print('Question:', t)

        if self.ai_list.currentText() == 'ollama':
            self.ai.prompt('ollama', {'prompt': t, 'model': self.config['ollama']['model']})
        else:
            data = {
                'prompt': t,
                'model': self.config[self.ai_list.currentText()]['model'],
                'apikey': self.config[self.ai_list.currentText()]['apikey']
            }
            self.ai.prompt(self.ai_list.currentText(), data)

        self.prompt.setText('')

    def set_button_loading_state(self, is_loading):
        if is_loading:
            self.btn.setText('...')
            self.btn.setEnabled(False)
        else:
            self.btn.setText('Send')
            self.btn.setEnabled(True)

    def close(self):
        self.chat_window.close()
        super().close()


class ChatWindow(QuolSubWindow):
    def __init__(self, main_window: QuolMainWindow):
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        super().__init__(main_window, 'Chat')
        self.setGeometry(QRect(screen_geometry.width() - 510, screen_geometry.height() - 610, 500, 600))

        self.chat_response = QTextBrowser()
        self.chat_response.setOpenExternalLinks(True)
        self.chat_response.setReadOnly(True)
        self.layout.addWidget(self.chat_response, stretch=1)

        self.old_text = ''

    def set_text(self, text, save=True):
        if save:
            self.old_text = text

        scrollbar = self.chat_response.verticalScrollBar()
        scroll_pos = scrollbar.value()

        html = self.markdown_to_html(str(text))
        self.chat_response.setHtml(html)

        scrollbar.setValue(scroll_pos)

        self.chat_response.repaint()
        QApplication.processEvents()

    def get_text(self):
        return self.old_text

    def scroll_to_bottom(self):
        scrollbar = self.chat_response.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event):
        print('Window closed')
        super().closeEvent(event)
        self.set_text('')
        # self.setGeometry(QRect(self.g[0], self.g[1], self.g[2], self.g[3]))
        HISTORY.clear()
        self.close()

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


class AI:
    def __init__(self, window: MainWindow, chat_window: ChatWindow):
        self.window = window
        self.chat_window = chat_window
        self.ollama_client = None
        self.current_type = None

        self.is_img = True
        self.is_hist = True
        self.text_content = ''
        self.loading_counter = 0

        self.max_hist = self.window.config['config']['max_history']

    def prompt(self, model, d):
        self.current_type = model
        self.chat_window.show()
        self.chat_window.set_text(f'{self.chat_window.get_text()}\\> {d['prompt']}\n\n')
        self.chat_window.set_text(f'{self.chat_window.get_text()}' + '<div style="height: 50px;"></div>', False)
        self.chat_window.scroll_to_bottom()

        if test_response[0]:
            self.chat_window.set_text(test_response[0])
            return

        if model == 'ollama':
            self.ollama(d['model'], d['prompt'])
            return
        elif model == 'gemini':
            self.handle_response(*self.gemini(d['model'], d['prompt'], d['apikey']))
        elif model == 'groq':
            self.handle_response(*self.groq(d['model'], d['prompt'], d['apikey']))

    @asyncSlot()
    async def handle_response(self, url, headers, data):
        self.text_content = ''
        self.loading_counter = 0

        def update_loading_text():
            self.loading_counter += 0.1
            self.chat_window.set_text(f'{self.chat_window.get_text()}Loading... ({self.loading_counter:.1f}s)', False)

        try:
            timer = QTimer()
            timer.timeout.connect(update_loading_text)
            timer.start(100)

            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=30.0)) as client:
                response = await client.post(url, headers=headers, json=data)

            timer.stop()
            res = response.json()

            if 'error' in res:
                raise Exception(f'Error: {res["error"]["message"]}')

            if self.current_type == 'gemini':
                self.text_content = res['candidates'][0]['content']['parts'][0]['text']
            elif self.current_type == 'groq':
                self.text_content = res['choices'][0]['message']['content']

            self.chat_window.set_text(f'{self.chat_window.get_text()}{self.text_content}\n\n')
            self.add_history(self.current_type, self.text_content, None, False)
        except Exception as e:
            print(e)
            self.text_content = str(e)
            self.chat_window.set_text(f'{self.chat_window.get_text()}{self.text_content}\n\n')
            HISTORY.clear()
        finally:
            self.window.set_button_loading_state(False)

    def add_history(self, model, text, img_data, is_user):
        if self.is_hist:
            if is_user:
                HISTORY.append({'role': 'user', 'text': text})
                if self.is_img:
                    HISTORY[-1]['image'] = img_data
            else:
                HISTORY.append({'role': 'model', 'text': text})

        with open(self.window.window_info.path + f'/res/{model}.log', 'a', encoding='utf-8') as f:
            if is_user:
                f.write(f'{datetime.datetime.now()}\nQ: {text}\n')
            else:
                f.write(f'A: {text.replace("\n\n", "\n")}\n\n')

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
                    'images': [self.window.window_info.path + '/res/img/screenshot.png']
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
                        {'inline_data': {'mime_type': 'image/png', 'data': h['image']}}
                    )

        cur = {'role': 'user', 'parts': [{'text': prompt}]}

        if self.is_img:
            with open(self.window.window_info.path + '/res/img/screenshot.png', 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                cur['parts'].append({'inline_data': {'mime_type': 'image/png', 'data': img_data}})

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
                            {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{h['image']}'}}
                        )
                else:
                    data['messages'].append({'role': 'assistant', 'content': h['text']})

        cur = {'role': 'user', 'content': [{'type': 'text', 'text': prompt}]}

        if self.is_img:
            with open(self.window.window_info.path + '/res/img/screenshot.png', 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                cur['content'].append({'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{img_data}'}})

        data['messages'].append(cur)
        self.add_history('groq', prompt, img_data, True)
        return url, headers, data
