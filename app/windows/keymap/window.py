import os
import keyboard

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QWidget, QGroupBox

from lib.io_helpers import read_json, write_json
from lib.quol_window import QuolMainWindow
from lib.window_loader import WindowInfo, WindowContext


class MainWindow(QuolMainWindow):
    def __init__(self, window_info: WindowInfo, window_context: WindowContext):
        super().__init__('Keymap', window_info, window_context, default_geometry=(200, 180, 180, 1), show_config=False)

        self.keymap_groupbox = QGroupBox('Key Mappings')
        self.keymap_layout = QVBoxLayout()
        self.keymap_groupbox.setLayout(self.keymap_layout)
        self.keymap_layout.setContentsMargins(0, 5, 0, 5)
        self.layout.addWidget(self.keymap_groupbox)

        self.add_button = QPushButton('+ Add Mapping')
        self.add_button.clicked.connect(lambda: self.add_mapping_row())
        self.layout.addWidget(self.add_button)

        self.key_mappings: dict[str, dict] = {}

        self.mappings_path = self.window_info.path + '/res/keymaps.json'
        self.load_mappings()

    def add_mapping_row(self, src='', dst=''):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)

        src_input = QLineEdit(src)
        dst_input = QLineEdit(dst)
        src_input.setFixedWidth(50)
        dst_input.setFixedWidth(50)
        src_input.setPlaceholderText("Old")
        dst_input.setPlaceholderText("New")

        save_btn = QPushButton("✔")
        delete_btn = QPushButton("✖")
        save_btn.setFixedWidth(20)
        delete_btn.setFixedWidth(20)

        row_layout.addWidget(src_input)
        row_layout.addWidget(dst_input)
        row_layout.addWidget(save_btn)
        row_layout.addWidget(delete_btn)

        self.setFixedHeight(self.height() + 25)
        self.keymap_layout.addWidget(row_widget)

        def save_mapping():
            source = src_input.text().strip().lower()
            target = dst_input.text().strip().lower()

            if not source or not target:
                return

            if source in self.key_mappings:
                keyboard.remove_hotkey(self.key_mappings[source]['handle'])

            handle = keyboard.add_hotkey(source, lambda: keyboard.send(target), suppress=True)
            self.key_mappings[source] = {'target': target, 'handle': handle}
            print(f"Mapped '{source}' -> '{target}'")

            self.save_mappings()

        def delete_mapping():
            source = src_input.text().strip().lower()
            if source in self.key_mappings:
                keyboard.remove_hotkey(self.key_mappings[source]['handle'])
                del self.key_mappings[source]

            row_widget.setParent(None)
            row_widget.deleteLater()
            self.setFixedHeight(self.height() - 25)

            self.save_mappings()

        save_btn.clicked.connect(save_mapping)
        delete_btn.clicked.connect(delete_mapping)

        return src_input, dst_input, save_btn

    def save_mappings(self):
        data = {src: self.key_mappings[src]['target'] for src in self.key_mappings}
        write_json(self.mappings_path, data)

    def load_mappings(self):
        data = read_json(self.mappings_path)

        for src, dst in data.items():
            src_input, dst_input, save_btn = self.add_mapping_row(src, dst)
            save_btn.clicked.connect(lambda: save_btn.parent().save_mappings())
            self.key_mappings[src] = {'target': dst, 'handle': None}
            self.key_mappings[src]['handle'] = keyboard.add_hotkey(src, lambda: keyboard.send(dst), suppress=True)

