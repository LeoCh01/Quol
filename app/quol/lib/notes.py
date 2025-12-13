import requests
from PySide6.QtCore import QRect
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QTextBrowser, QTextEdit,
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout
)

from lib.quol_window import QuolSubWindow

BASE_URL = 'https://leo-s-website-backend-695678049922.northamerica-northeast2.run.app/quol'


class NotesWindow(QuolSubWindow):
    def __init__(self, main_window, admin_key=None):
        super().__init__(main_window, 'Admin Notes')

        self.admin_key = admin_key
        self.edit_mode = False
        self.is_diff = False

        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(QRect(screen.width() // 2 - 200, screen.height() // 2 - 200, 400, 400))

        self.view_widget = QTextBrowser()
        self.view_widget.setOpenExternalLinks(False)
        self.view_widget.setReadOnly(True)

        self.edit_widget = QTextEdit()
        self.edit_widget.hide()

        self.toggle_btn = QPushButton("Edit")
        self.toggle_btn.clicked.connect(self.toggle_mode)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_data)

        if not self.admin_key:
            self.toggle_btn.hide()

        button_bar = QHBoxLayout()
        button_bar.addWidget(self.refresh_btn)
        button_bar.addWidget(self.toggle_btn)

        self.container = QWidget()
        self.vlayout = QVBoxLayout(self.container)
        self.vlayout.addLayout(button_bar)
        self.vlayout.addWidget(self.view_widget)
        self.vlayout.addWidget(self.edit_widget)

        self.layout.addWidget(self.container)

    @staticmethod
    def get_notes():
        try:
            response = requests.get(f'{BASE_URL}/notes')
            response.raise_for_status()
            text = response.text
            return text
        except requests.RequestException:
            return "Error fetching notes from server."

    def save_notes(self):
        if not self.admin_key or not self.is_diff:
            return False

        try:
            response = requests.post(f'{BASE_URL}/notes/{self.admin_key}', json={"notes": self.get_text()})
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    def refresh_data(self):
        new_text = self.get_notes()
        self.view_widget.setPlainText(new_text)
        self.edit_widget.setPlainText(new_text)

    def toggle_mode(self):
        self.edit_mode = not self.edit_mode
        self.is_diff = self.view_widget.toPlainText() != self.edit_widget.toPlainText()

        if self.edit_mode:
            self.enable_edit_mode()
        else:
            self.enable_view_mode()

            if not self.save_notes():
                print("Error saving notes to server.")

    def enable_edit_mode(self):
        pos = self.view_widget.verticalScrollBar().value()
        self.edit_widget.setPlainText(self.view_widget.toPlainText())
        self.view_widget.hide()
        self.edit_widget.show()
        QApplication.processEvents()
        self.edit_widget.verticalScrollBar().setValue(pos)
        self.toggle_btn.setText("View")

    def enable_view_mode(self):
        pos = self.edit_widget.verticalScrollBar().value()
        text = self.edit_widget.toPlainText()
        self.view_widget.setPlainText(text)
        self.edit_widget.hide()
        self.view_widget.show()
        QApplication.processEvents()
        self.view_widget.verticalScrollBar().setValue(pos)
        self.toggle_btn.setText("Edit")

    def get_text(self):
        return self.edit_widget.toPlainText() if self.edit_mode else self.view_widget.toPlainText()

    def showEvent(self, event):
        self.refresh_data()
        super().showEvent(event)
