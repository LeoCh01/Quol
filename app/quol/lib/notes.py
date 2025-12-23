from PySide6.QtCore import QRect
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QTextBrowser,
    QTextEdit,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)

from lib.quol_window import QuolSubWindow
from worker import Worker
from api import fetch_notes, post_notes


class NotesWindow(QuolSubWindow):
    def __init__(self, main_window, admin_key=None):
        super().__init__(main_window, "Message Board")

        self.admin_key = admin_key
        self.edit_mode = False
        self.is_diff = False
        self.worker = None

        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(
            QRect(
                screen.width() // 2 - 200,
                screen.height() // 2 - 200,
                400,
                400,
            )
        )

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

        # Layouts
        button_bar = QHBoxLayout()
        button_bar.addWidget(self.refresh_btn)
        button_bar.addWidget(self.toggle_btn)

        self.container = QWidget()
        self.vlayout = QVBoxLayout(self.container)
        self.vlayout.addLayout(button_bar)
        self.vlayout.addWidget(self.view_widget)
        self.vlayout.addWidget(self.edit_widget)

        self.layout.addWidget(self.container)

    def set_text(self, text=''):
        self.view_widget.setPlainText(text)
        self.edit_widget.setPlainText(text)

    def refresh_data(self):
        self.refresh_btn.setEnabled(False)
        self.set_text("Loading notes from server...")

        self.worker = Worker(fetch_notes)
        self.worker.finished.connect(self.on_notes_loaded)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()

    def on_notes_loaded(self, text):
        self.refresh_btn.setEnabled(True)
        self.view_widget.setPlainText(text)
        self.edit_widget.setPlainText(text)

    def save_notes(self):
        if not self.admin_key or not self.is_diff:
            return

        self.toggle_btn.setEnabled(False)
        text = self.get_text()
        self.set_text("Saving notes to server...")

        self.worker = Worker(
            post_notes,
            self.admin_key,
            text,
        )

        self.worker.finished.connect(lambda result: self.on_notes_saved(result, text))
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()

    def on_notes_saved(self, success, text=''):
        self.toggle_btn.setEnabled(True)
        self.set_text(text)

        if not success:
            print("Error saving notes to server.")

    def toggle_mode(self):
        self.edit_mode = not self.edit_mode
        self.is_diff = self.view_widget.toPlainText() != self.edit_widget.toPlainText()

        if self.edit_mode:
            self.enable_edit_mode()
        else:
            self.enable_view_mode()
            self.save_notes()

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
        if self.edit_mode:
            return self.edit_widget.toPlainText()
        return self.view_widget.toPlainText()

    def on_worker_error(self, error):
        self.refresh_btn.setEnabled(True)
        self.toggle_btn.setEnabled(True)
        print("Worker error:", error)
        self.view_widget.setPlainText("Error communicating with server.")

    def showEvent(self, event):
        self.refresh_data()
        super().showEvent(event)
