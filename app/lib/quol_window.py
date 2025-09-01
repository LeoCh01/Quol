from PySide6.QtCore import Qt, Signal, QRect, QPoint
from PySide6.QtGui import QPainterPath, QRegion
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QHBoxLayout, QPushButton, QGroupBox, QCheckBox, QLabel, QLineEdit

from lib.io_helpers import read_json
from lib.quol_titlebar import QuolSubTitleBar, QuolMainTitleBar
from lib.window_loader import WindowInfo, WindowContext


class QuolBaseWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

        self._l1 = QVBoxLayout(self)
        self._l1.setContentsMargins(0, 0, 0, 0)
        self._l1.setSpacing(0)

        self._body = QWidget()
        self._body.setObjectName('content')
        self._body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._l1.addWidget(self._body)

        self._lower = QWidget()
        self._lower.setObjectName('content')
        self._l1.addWidget(self._lower)

        self.layout = QVBoxLayout(self._body)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.transition = None

        self.is_hidden = True

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
        if self.is_hidden:
            return

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

    def setGeometry(self, *args):
        if len(args) == 1 and isinstance(args[0], QRect):
            super().setGeometry(args[0])
            if self.transition:
                self.transition.old_pos = self.pos()
        elif len(args) == 4:
            super().setGeometry(QRect(*args))
            if self.transition:
                self.transition.old_pos = self.pos()
        else:
            raise TypeError("setGeometry() accepts either a QRect or (x, y, width, height)")
        self.update()

    def show(self):
        super().show()
        self.is_hidden = False

    def close(self):
        super().close()
        self.is_hidden = True


class QuolMainWindow(QuolBaseWindow):
    config_signal = Signal()

    def __init__(self, title, window_info: WindowInfo, window_context: WindowContext, default_geometry: tuple[int, int, int, int], show_config=True):
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

        if show_config:
            self.config_signal.connect(self.on_update_config)
            self.config_window = QuolConfigWindow(self, title + ' Config')
        else:
            self.config_window = None

        self._title_bar = QuolMainTitleBar(self, title, self.config_window)
        self._l1.insertWidget(0, self._title_bar)

        self.transition = self.window_context.transition_plugin.create_transition(self)
        self.update()

    def on_update_config(self):
        """
        This method is called when the config.json file is updated.
        """
        pass

    def close(self):
        super().close()
        if self.config_window:
            self.config_window.close()


class QuolSubWindow(QuolBaseWindow):
    def __init__(self, main_window: QuolMainWindow, title):
        super().__init__(main_window)

        self.main_window = main_window
        self._title_bar = QuolSubTitleBar(self, title)
        self._l1.insertWidget(0, self._title_bar)

        self.transition = self.main_window.window_context.transition_plugin.create_transition(self)


class QuolResizableSubWindow(QuolSubWindow):
    MARGIN = 8

    def __init__(self, main_window: QuolMainWindow, title):
        super().__init__(main_window, title)
        self.setMinimumSize(150, 150)

        self._mouse_pos = None
        self._resizing = False
        self._resize_dir = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._mouse_pos = event.globalPosition().toPoint()
            self._resize_dir = self._detect_resize_direction(event.pos())
            if self._resize_dir:
                self._resizing = True
            else:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event):
        if self._resizing and self._resize_dir:
            self._resize_window(event.globalPosition().toPoint())

            direction = self._detect_resize_direction(event.pos())
            if direction:
                self._set_cursor(direction)
            else:
                self.unsetCursor()

        if hasattr(self, '_drag_pos'):
            self.move(event.globalPosition().toPoint() - self._drag_pos)

        event.accept()

    def mouseReleaseEvent(self, event):
        self._resizing = False
        self._resize_dir = None
        if hasattr(self, '_drag_pos'):
            del self._drag_pos
        self.unsetCursor()
        event.accept()

    def _detect_resize_direction(self, pos: QPoint):
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        margin = self.MARGIN

        directions = {
            'left': x < margin,
            'right': x > w - margin,
            'top': y < margin,
            'bottom': y > h - margin,
        }

        result = ''
        if directions['top']:
            result += 'top'
        elif directions['bottom']:
            result += 'bottom'
        if directions['left']:
            result += 'left'
        elif directions['right']:
            result += 'right'
        return result if result else None

    def _set_cursor(self, direction):
        cursors = {
            'left': Qt.CursorShape.SizeHorCursor,
            'right': Qt.CursorShape.SizeHorCursor,
            'top': Qt.CursorShape.SizeVerCursor,
            'bottom': Qt.CursorShape.SizeVerCursor,
            'topleft': Qt.CursorShape.SizeFDiagCursor,
            'topright': Qt.CursorShape.SizeBDiagCursor,
            'bottomleft': Qt.CursorShape.SizeBDiagCursor,
            'bottomright': Qt.CursorShape.SizeFDiagCursor,
        }
        self.setCursor(cursors.get(direction, Qt.CursorShape.ArrowCursor))

    def _resize_window(self, global_pos: QPoint):
        delta = global_pos - self._mouse_pos
        geom = self.geometry()

        x, y, w, h = geom.x(), geom.y(), geom.width(), geom.height()

        if 'left' in self._resize_dir:
            new_x = x + delta.x()
            new_w = w - delta.x()
            if new_w >= self.minimumWidth():
                geom.setX(new_x)
                geom.setWidth(new_w)
        elif 'right' in self._resize_dir:
            new_w = w + delta.x()
            if new_w >= self.minimumWidth():
                geom.setWidth(new_w)

        if 'top' in self._resize_dir:
            new_y = y + delta.y()
            new_h = h - delta.y()
            if new_h >= self.minimumHeight():
                geom.setY(new_y)
                geom.setHeight(new_h)
        elif 'bottom' in self._resize_dir:
            new_h = h + delta.y()
            if new_h >= self.minimumHeight():
                geom.setHeight(new_h)

        self.setGeometry(geom)
        self._mouse_pos = global_pos


class QuolDialogWindow(QuolSubWindow):
    def __init__(self, main_window: QuolMainWindow, title: str):
        super().__init__(main_window, title)

        self.setGeometry(300, 300, 400, 200)

        self.button_layout = QHBoxLayout(self._lower)
        self.accept_button = QPushButton("Accept")
        self.accept_button.setShortcut(Qt.Key.Key_Return)
        self.cancel_button = QPushButton("Cancel")
        self.accept_button.clicked.connect(self.close)
        self.cancel_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.accept_button)

    def on_accept(self, fn):
        """
        Override this method to define what happens when the accept button is clicked.
        :param fn: Function to call when the accept button is clicked.
        """
        self.accept_button.clicked.connect(fn)

    def on_reject(self, fn):
        """
        Override this method to define what happens when the cancel button is clicked.
        :param fn: Function to call when the cancel button is clicked.
        """
        self.cancel_button.clicked.connect(fn)


class QuolConfigWindow(QuolSubWindow):
    def __init__(self, main_window: QuolMainWindow, title: str):
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
                checkbox = QCheckBox()
                checkbox.setChecked(value)
                layout = QHBoxLayout()
                layout.addWidget(QLabel(key))
                layout.addWidget(checkbox)
                return layout
            elif isinstance(value, dict):
                group_box = QGroupBox(key)
                group_layout = QVBoxLayout(group_box)
                for k, v in value.items():
                    add_to_layout(group_layout, create_item(k, v))
                return group_box
            else:
                input_field = QLineEdit()
                input_field.setText(str(value))
                layout = QHBoxLayout()
                layout.addWidget(QLabel(key))
                layout.addWidget(input_field)
                return layout

        for k, v in self.settings.items():
            if k == '_':
                continue
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
        config['_'] = self.main_window.config.get('_', {})
        self.main_window.config = config
        self.main_window.window_info.save_config(config)
        self.main_window.config_signal.emit()
        self.hide()
