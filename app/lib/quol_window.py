from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainterPath, QRegion
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QHBoxLayout, QPushButton, QGroupBox, QCheckBox, QLabel, QLineEdit

from lib.io_helpers import read_json
from lib.quol_titlebar import QuolSubTitleBar, QuolMainTitleBar
from lib.window_loader import WindowInfo, WindowContext


class QuolBaseWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

        self.l1 = QVBoxLayout(self)
        self.l1.setContentsMargins(0, 0, 0, 0)
        self.l1.setSpacing(0)

        self.body = QWidget()
        self.body.setObjectName('content')
        self.body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.l1.addWidget(self.body)

        self.layout = QVBoxLayout(self.body)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.transition = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setMask(self.generate_rounded_mask())

    def generate_rounded_mask(self):
        rect = self.rect()
        path = QPainterPath()
        radius = 6
        path.addRoundedRect(rect, radius, radius)
        return QRegion(path.toFillPolygon().toPolygon())

    def toggle_windows(self, is_hidden, is_instant=False):
        if is_instant:
            if is_hidden:
                self.hide()
            else:
                self.show()
            return

        if is_hidden:
            self.transition.enter()
        else:
            self.transition.exit()


class QuolMainWindow(QuolBaseWindow):
    config_signal = Signal()

    def __init__(self, title, window_info: WindowInfo, window_context: WindowContext, default_geometry: tuple[int, int, int, int]):
        super().__init__()

        self.window_info = window_info
        self.config = self.window_info.load_config()
        self.window_context = window_context

        default_pos = self.window_context.settings.get('is_default_pos')
        self.config.setdefault('_', {})
        self.setGeometry(QRect(*default_geometry))
        if default_pos or not self.config['_'].get('geometry'):
            self.config['_']['geometry'] = [*default_geometry]
            self.window_info.save_config(self.config)
        else:
            self.setGeometry(QRect(*self.config['_']['geometry']))

        self.update()
        self.config_signal.connect(self.on_update_config)
        self.config_window = QuolConfigWindow(self, title + ' Config')

        self.title_bar = QuolMainTitleBar(self, title, self.config_window)
        self.l1.insertWidget(0, self.title_bar)

        self.transition = self.window_context.transition_plugin.create_transition(self)

    def on_update_config(self):
        """
        This method is called when the config.json file is updated.
        """
        pass


class QuolSubWindow(QuolBaseWindow):
    def __init__(self, main_window: QuolMainWindow, title):
        super().__init__(main_window)

        self.main_window = main_window
        self.title_bar = QuolSubTitleBar(self, title)
        self.l1.insertWidget(0, self.title_bar)

        self.transition = self.main_window.window_context.transition_plugin.create_transition(self)


class QuolConfigWindow(QuolSubWindow):
    def __init__(self, main_window: QuolMainWindow, title):
        super().__init__(main_window, title)

        self.setGeometry(300, 300, 400, 1)

        self.config_layout = QVBoxLayout()
        self.layout.addLayout(self.config_layout)

        self.settings = read_json(self.main_window.window_info.config_path)
        self.generate_settings()

        self.button_layout = QHBoxLayout()
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.hide)
        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save)
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.save_button)
        self.layout.addLayout(self.button_layout)

    def generate_settings(self):
        def add_to_layout(layout, item):
            if isinstance(item, QGroupBox):
                layout.addWidget(item)
            else:
                layout.addLayout(item)

        def create_item(key, value):
            if isinstance(value, bool):
                checkbox = QCheckBox(self)
                checkbox.setChecked(value)
                layout = QHBoxLayout()
                layout.addWidget(QLabel(key))
                layout.addWidget(checkbox)
                return layout
            elif isinstance(value, dict):
                group_box = QGroupBox(key, self)
                group_layout = QVBoxLayout(group_box)
                for k, v in value.items():
                    add_to_layout(group_layout, create_item(k, v))
                return group_box
            else:
                input_field = QLineEdit(self)
                input_field.setText(str(value))
                layout = QHBoxLayout()
                layout.addWidget(QLabel(key))
                layout.addWidget(input_field)
                return layout

        for k, v in self.settings.items():
            add_to_layout(self.config_layout, create_item(k, v))

    def save(self):
        def extract_from_layout(layout):
            result = {}
            for i in range(layout.count()):
                item = layout.itemAt(i)
                widget = item.widget()
                sub_layout = item.layout()

                if isinstance(widget, QGroupBox):
                    group_layout = widget.layout()
                    result[widget.title()] = extract_from_layout(group_layout)
                elif isinstance(sub_layout, QHBoxLayout):
                    label = sub_layout.itemAt(0).widget()
                    value = sub_layout.itemAt(1).widget()
                    k = label.text()

                    if isinstance(value, QCheckBox):
                        result[k] = value.isChecked()
                    elif isinstance(value, QLineEdit):
                        text = value.text()
                        if text.isdigit():
                            result[k] = int(text)
                        elif text.replace('.', '', 1).isdigit():
                            result[k] = float(text)
                        else:
                            result[k] = text

            return result

        config = extract_from_layout(self.config_layout)
        self.main_window.config = config
        self.main_window.window_info.save_config(config)
        self.main_window.config_signal.emit()
        self.hide()
