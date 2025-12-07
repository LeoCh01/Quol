from PySide6.QtCore import QRect
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QTextBrowser, QTextEdit,
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout
)

from lib.quol_window import QuolSubWindow


class NotesWindow(QuolSubWindow):
    def __init__(self, main_window, admin_key=None):
        super().__init__(main_window, 'Admin Notes')

        self.admin_key = admin_key
        self.edit_mode = False

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
    def fetch_notes_from_api():
        return (
            "### Admin Notes\n"
            "- Hard-coded API response.\n"
            "- Replace fetch_notes_from_api() with server request.\n"
        )

    def refresh_data(self):
        new_text = self.fetch_notes_from_api()
        self.view_widget.setPlainText(new_text)
        self.edit_widget.setPlainText(new_text)

    def toggle_mode(self):
        if not self.admin_key:
            return

        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.enable_edit_mode()
        else:
            self.enable_view_mode()

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

    def set_text(self, text):
        if self.edit_mode:
            self.edit_widget.setPlainText(text)
        else:
            self.view_widget.setPlainText(text)

    def get_text(self):
        return self.edit_widget.toPlainText() if self.edit_mode else self.view_widget.toPlainText()

    def showEvent(self, event):
        self.refresh_data()
        super().showEvent(event)
