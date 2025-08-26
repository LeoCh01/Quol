import sys
import subprocess
import requests  # Required for API calls
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel,
    QHBoxLayout, QFrame, QMessageBox
)
from PySide6.QtGui import QMouseEvent, QPalette, QColor
from PySide6.QtCore import Qt, QPoint


# ---- Update Checker ----
def is_update_available():
    try:
        # Replace with your real API URL
        response = requests.get("https://example.com/api/check_update")
        response.raise_for_status()

        data = response.json()
        return data.get("update_available", False)
    except Exception as e:
        print(f"Update check failed: {e}")
        return False  # Fail silently and proceed as if no update


# ---- Custom Title Bar ----
class CustomTitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #222222;")

        layout = QHBoxLayout(self)

        self.title = QLabel("Launcher")
        self.title.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(self.title)

        layout.addStretch()

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(25, 25)
        layout.addWidget(self.close_btn)


# ---- Main Launcher App ----
class AppLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Launcher")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title_bar = CustomTitleBar(self)
        self.layout.addWidget(self.title_bar)
        self.title_bar.close_btn.clicked.connect(self.close)

        self.main_content = QFrame()
        self.main_content.setStyleSheet("background-color: #2b2b2b;")
        content_layout = QVBoxLayout(self.main_content)

        self.label = QLabel("Select an app or script to launch")
        self.label.setStyleSheet("color: white;")
        content_layout.addWidget(self.label)

        self.select_button = QPushButton("Browse and Select File")
        self.select_button.clicked.connect(self.select_file)
        content_layout.addWidget(self.select_button)

        self.launch_button = QPushButton("Launch")
        self.launch_button.clicked.connect(self.launch_app)
        self.launch_button.setEnabled(False)
        content_layout.addWidget(self.launch_button)

        self.layout.addWidget(self.main_content)

        self.selected_file = None
        self.drag_pos = QPoint()

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Launch")
        if file_path:
            self.selected_file = file_path
            self.label.setText(f"Selected: {file_path}")
            self.launch_button.setEnabled(True)

    def launch_app(self):
        if self.selected_file:
            try:
                subprocess.Popen([self.selected_file], shell=True)
                self.label.setText(f"Launched: {self.selected_file}")
                self.close()  # Close launcher after launching
            except Exception as e:
                self.label.setText(f"Error: {e}")

    # Drag window
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()


# ---- Apply Dark Theme ----
def apply_dark_theme(app):
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Highlight, QColor(80, 80, 255))
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setStyle("Fusion")
    app.setPalette(dark_palette)


# ---- MAIN ENTRY ----
def main():
    # Update check
    if is_update_available():
        app = QApplication(sys.argv)
        apply_dark_theme(app)

        # Ask user if they want to update
        reply = QMessageBox.question(
            None, "Update Available",
            "A new update is available. Do you want to update now?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Simulate update logic here
            QMessageBox.information(None, "Updating", "Update process would start here.")
            sys.exit(0)
        else:
            # Show launcher if user skips update
            launcher = AppLauncher()
            launcher.show()
            sys.exit(app.exec())

    else:
        # No update – directly run the app (hardcoded path or behavior)
        try:
            # Replace with path to your main executable
            subprocess.Popen(["your_app.exe"], shell=True)
        except Exception as e:
            print(f"Failed to launch app: {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()
