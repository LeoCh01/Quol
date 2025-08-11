import os
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QWidget, QGroupBox
)
import keyboard

from lib.io_helpers import read_json, write_json
from lib.quol_window import QuolMainWindow, QuolDialogWindow
from lib.window_loader import WindowInfo, WindowContext


class MainWindow(QuolMainWindow):
    def __init__(self, window_info: WindowInfo, window_context: WindowContext):
        super().__init__('Keymap', window_info, window_context, default_geometry=(200, 180, 180, 1), show_config=False)

        self.keymap_groupbox = QGroupBox('Key Mappings')
        self.keymap_layout = QVBoxLayout()
        self.keymap_groupbox.setLayout(self.keymap_layout)
        self.keymap_layout.setContentsMargins(0, 5, 0, 5)
        self.layout.addWidget(self.keymap_groupbox)

        self.add_button = QPushButton('+ Add Mapping Group')
        self.add_button.clicked.connect(self.add_group_row)
        self.layout.addWidget(self.add_button)

        self.mapping_groups: dict[str, dict] = {}
        self.group_counter = 0  # For unnamed groups

        self.mappings_path = os.path.join(self.window_info.path, 'res', 'keymaps.json')

        # Load existing mappings on start
        self.load_mappings()

    @staticmethod
    def make_send_callback(dst):
        return lambda: keyboard.send(dst)

    def add_group_row(self):
        group_id = f"__group_{self.group_counter}"
        self.group_counter += 1

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)

        group_button = QPushButton("Unnamed")
        group_button.setFixedWidth(100)

        enable_btn = QPushButton("✔")
        enable_btn.setFixedWidth(20)

        delete_btn = QPushButton("✖")
        delete_btn.setFixedWidth(20)

        row_layout.addWidget(group_button)
        row_layout.addWidget(enable_btn)
        row_layout.addWidget(delete_btn)

        self.keymap_layout.addWidget(row_widget)

        self.mapping_groups[group_id] = {
            'widget': row_widget,
            'button': group_button,
            'mappings': [],
            'enabled': False,
            'handles': {},
            'name': "Unnamed"
        }

        def toggle_enable():
            group = self.mapping_groups[group_id]
            if not group['enabled']:
                for src, dst in group['mappings']:
                    try:
                        handle = keyboard.add_hotkey(src, self.make_send_callback(dst), suppress=True)
                        group['handles'][src] = handle
                    except Exception as e:
                        print(f"Failed to bind {src} -> {dst}: {e}")
                group['enabled'] = True
                enable_btn.setStyleSheet("background-color: #4CAF50;")
            else:
                for handle in group['handles'].values():
                    keyboard.remove_hotkey(handle)
                group['handles'].clear()
                group['enabled'] = False
                enable_btn.setStyleSheet("")

        def delete_group():
            self.remove_group(group_id)
            self.save_mappings()

        def open_dialog():
            group = self.mapping_groups[group_id]
            dialog = KeymapGroupDialog(self, group['name'], group['mappings'])

            def on_accept():
                name, mappings = dialog.get_group_data()
                if not name or not mappings:
                    return

                # Update group data
                group['mappings'] = mappings
                group['name'] = name
                group_button.setText(name)

                # Refresh hotkeys if enabled
                if group['enabled']:
                    for handle in group['handles'].values():
                        keyboard.remove_hotkey(handle)
                    group['handles'].clear()
                    for src, dst in mappings:
                        try:
                            handle = keyboard.add_hotkey(src, self.make_send_callback(dst), suppress=True)
                            group['handles'][src] = handle
                        except Exception as e:
                            print(f"Failed to bind {src} -> {dst}: {e}")

                self.save_mappings()
                dialog.close()

            dialog.on_accept(on_accept)
            dialog.show()

        enable_btn.clicked.connect(toggle_enable)
        delete_btn.clicked.connect(delete_group)
        group_button.clicked.connect(open_dialog)

    def remove_group(self, group_id):
        if group_id not in self.mapping_groups:
            return

        group = self.mapping_groups[group_id]
        if group['enabled']:
            for handle in group['handles'].values():
                keyboard.remove_hotkey(handle)

        group['widget'].setParent(None)
        group['widget'].deleteLater()
        del self.mapping_groups[group_id]

    def save_mappings(self):
        data = {}
        for group in self.mapping_groups.values():
            name = group['name'] or "Unnamed"
            mappings_dict = {src: dst for src, dst in group['mappings']}
            data[name] = mappings_dict
        write_json(self.mappings_path, data)

    def load_mappings(self):
        if not os.path.exists(self.mappings_path):
            return

        data = read_json(self.mappings_path)
        for name, mappings_dict in data.items():
            self.add_group_row()
            group_id = f"__group_{self.group_counter - 1}"
            group = self.mapping_groups[group_id]
            group['name'] = name
            group['button'].setText(name)
            group['mappings'] = list(mappings_dict.items())

    def closeEvent(self, event):
        for group in self.mapping_groups.values():
            for handle in group['handles'].values():
                keyboard.remove_hotkey(handle)
        super().closeEvent(event)


class KeymapGroupDialog(QuolDialogWindow):
    def __init__(self, main_window: QuolMainWindow, group_name='', mappings=None):
        super().__init__(main_window, "Edit Keymap Group")
        self.setGeometry(300, 300, 200, 300)

        self.group_name_input = QLineEdit(group_name)
        self.group_name_input.setPlaceholderText("Group name")
        self.layout.addWidget(self.group_name_input)

        self.groupbox = QGroupBox("Key Mappings")
        self.groupbox_layout = QVBoxLayout()
        self.groupbox.setLayout(self.groupbox_layout)
        self.layout.addWidget(self.groupbox)

        self.add_mapping_btn = QPushButton("+ Add Mapping")
        self.add_mapping_btn.clicked.connect(self.add_mapping_row)
        self.layout.addWidget(self.add_mapping_btn)

        self.mapping_rows = []

        if mappings:
            for src, dst in mappings:
                self.add_mapping_row(src, dst)

    def add_mapping_row(self, src: str = '', dst: str = '', *_):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)

        src_input = QLineEdit()
        dst_input = QLineEdit()
        src_input.setText(src)
        dst_input.setText(dst)
        src_input.setPlaceholderText("Old")
        dst_input.setPlaceholderText("New")
        src_input.setFixedWidth(60)
        dst_input.setFixedWidth(60)

        delete_btn = QPushButton("✖")
        delete_btn.setFixedWidth(20)
        delete_btn.clicked.connect(lambda: self.remove_mapping_row(row_widget))

        row_layout.addWidget(src_input)
        row_layout.addWidget(dst_input)
        row_layout.addWidget(delete_btn)

        self.groupbox_layout.addWidget(row_widget)
        self.mapping_rows.append((src_input, dst_input, row_widget))

    def remove_mapping_row(self, row_widget):
        for i, (_, _, widget) in enumerate(self.mapping_rows):
            if widget == row_widget:
                self.mapping_rows.pop(i)
                break
        row_widget.setParent(None)
        row_widget.deleteLater()

    def get_group_data(self):
        group_name = self.group_name_input.text().strip()
        mappings = [
            (src.text().strip().lower(), dst.text().strip().lower())
            for src, dst, _ in self.mapping_rows
            if src.text().strip() and dst.text().strip()
        ]
        return group_name, mappings
