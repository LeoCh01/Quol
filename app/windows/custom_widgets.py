import json
import os
import random

from PySide6.QtCore import QPropertyAnimation, QPoint, QEasingCurve, Qt, QRect, QByteArray, Signal
from PySide6.QtGui import QPainterPath, QRegion, QColor, QPainter, QBrush, QIcon, QPen
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QLineEdit, QGroupBox, \
    QSizePolicy

from res.paths import POS_PATH, IMG_PATH


class CustomWindow(QWidget):
    config_signal = Signal()
    toggle_direction = 'random'

    def __init__(self, title='Custom Window', wid=-1, geometry=(0, 0, 0, 0), add_close_btn=False, path=None):
        """
        Initialize a custom window.

        Args:
            title (str): The title of the window.
            wid (int): The window ID.
            geometry (tuple): The default geometry of the window (x, y, width, height).
            add_close_btn (bool): Whether to add a close button to the title bar.
            path (str): The window path (required for loading config).
        """
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setGeometry(*geometry)
        self.geo_old = self.geometry()
        self.wid = wid

        self.config_path = None
        if path and os.path.exists(path + '/config.json'):
            self.config_path = path + '/config.json'
        self.config = None
        self.update_config()
        self.config_signal.connect(self.on_update_config)

        self.l1 = QVBoxLayout(self)
        self.l1.setContentsMargins(0, 0, 0, 0)
        self.l1.setSpacing(0)

        self.title_bar = CustomTitleBar(title, self, add_close_btn)
        self.l1.addWidget(self.title_bar)

        self.w1 = QWidget()
        self.w1.setObjectName('content')
        self.w1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.l1.addWidget(self.w1)

        self.layout = QVBoxLayout(self.w1)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def update_config(self):
        if self.config_path:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
                self.config_signal.emit()

    def on_update_config(self):
        """
        This method is called when the config.json file is updated (requires path to be set).
        """
        pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setMask(self.generateRoundedMask())

    def generateRoundedMask(self):
        rect = self.rect()
        path = QPainterPath()
        radius = 6
        path.addRoundedRect(rect, radius, radius)
        return QRegion(path.toFillPolygon().toPolygon())

    def generatePosition(self):
        screen_geometry = self.screen().geometry()

        if CustomWindow.toggle_direction == 'up':
            x = (screen_geometry.width() - self.geo_old.width()) // 2
            y = -self.geometry().height()
        elif CustomWindow.toggle_direction == 'down':
            x = (screen_geometry.width() - self.geo_old.width()) // 2
            y = screen_geometry.height()
        elif CustomWindow.toggle_direction == 'left':
            x = -self.geo_old.width()
            y = (screen_geometry.height() - self.geometry().height()) // 2
        elif CustomWindow.toggle_direction == 'right':
            x = screen_geometry.width()
            y = (screen_geometry.height() - self.geometry().height()) // 2
        else:
            side = random.randint(0, 1)
            if side:
                x = random.randint(0, screen_geometry.width() - self.geo_old.width())
                y = random.choice([-self.geometry().height(), screen_geometry.height()])
            else:
                x = random.choice([-self.geo_old.width(), screen_geometry.width()])
                y = random.randint(0, screen_geometry.height() - self.geometry().height())

        return QPoint(x, y)

    def toggle_windows(self, is_hidden, is_instant=False):
        if is_instant:
            if is_hidden:
                self.hide()
            elif self.wid != -1:
                self.show()
            return

        self.animation = QPropertyAnimation(self, QByteArray(b'pos'))
        start_pos = self.pos()

        end_pos = QPoint(self.geo_old.x(), self.geo_old.y()) if is_hidden else self.generatePosition()

        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush('#444'))
        painter.drawRect(self.rect())


class CustomTitleBar(QWidget):
    def __init__(self, title='Custom Title Bar', parent: CustomWindow = None, add_close_btn=False):
        super().__init__()
        self.parent = parent

        self.setObjectName('title-bar')
        self.bar_color_default = QColor('#222')
        self.bar_color = self.bar_color_default

        self.l1 = QHBoxLayout(self)

        self.title_label = QLabel(title)
        self.l1.addWidget(self.title_label, stretch=10)

        if parent.config_path:
            self.config_window = ConfigWindow(parent, title + ' Config')
            self.config_btn = QPushButton(self)
            self.config_btn.setIcon(QIcon(IMG_PATH + 'config.png'))
            self.config_btn.clicked.connect(self.config_window.show)
            self.l1.addWidget(self.config_btn, stretch=1)
        if add_close_btn:
            self.close_btn = QPushButton('✕')
            self.close_btn.clicked.connect(parent.close)
            self.l1.addWidget(self.close_btn, stretch=1)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(self.bar_color))
        painter.drawRect(self.rect())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.globalPosition().toPoint() - self.window().pos()
            self.bar_color = self.bar_color.darker(150)
            self.parent.setWindowOpacity(0.5)
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        self.bar_color = self.bar_color_default
        self.parent.setWindowOpacity(1)
        self.parent.geo_old = QRect(
            round(self.parent.geometry().x() / 10) * 10,
            round(self.parent.geometry().y() / 10) * 10,
            self.parent.geometry().width(),
            self.parent.geometry().height()
        )

        self.parent.setGeometry(self.parent.geo_old)
        self.update()

        if self.parent.wid != -1:
            with open(POS_PATH, 'r') as f:
                settings = json.load(f)
                w = settings.get('windows')[self.parent.wid]
                settings['pos'][w] = [self.parent.geo_old.x(), self.parent.geo_old.y(), self.parent.geo_old.width(),
                                      self.parent.geometry().height()]

            with open(POS_PATH, 'w') as f:
                json.dump(settings, f, indent=2)


class ConfigWindow(CustomWindow):
    def __init__(self, parent, title='Settings'):
        super().__init__(title, add_close_btn=True)
        self.setGeometry(300, 300, 400, 1)
        self.parent = parent
        self.config_path = parent.config_path

        self.config_layout = QVBoxLayout()
        self.layout.addLayout(self.config_layout)
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

        with open(self.config_path, 'r') as f:
            settings = json.load(f)

        for k, v in settings.items():
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
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
            self.hide()

        self.parent.update_config()
