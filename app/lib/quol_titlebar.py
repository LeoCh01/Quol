from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QFrame


class QuolBaseTitleBar(QFrame):
    def __init__(self, quol_window: "QuolBaseWindow", title='Custom Title Bar'):
        super().__init__(quol_window)

        self.quol_window = quol_window
        self.setObjectName('title-bar')
        self.l1 = QHBoxLayout(self)
        self.l1.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel(title)
        self.l1.addWidget(self.title_label, stretch=10)

        self.offset = QPoint(self.quol_window.pos().x(), self.quol_window.pos().y())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.globalPosition().toPoint() - self.quol_window.pos()
            self.quol_window.setWindowOpacity(0.5)
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.quol_window.move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        self.quol_window.setWindowOpacity(1)
        self.quol_window.transition.old_pos = self.quol_window.pos()


class QuolMainTitleBar(QuolBaseTitleBar):
    def __init__(self, quol_window: "QuolMainWindow", title, config_window: "QuolConfigWindow"):
        super().__init__(quol_window, title)

        self.quol_window = quol_window

        if config_window:
            self.config_btn = QPushButton(self)
            self.config_btn.setIcon(QIcon('res/icons/config.png'))
            self.config_btn.clicked.connect(config_window.show)
            self.l1.addWidget(self.config_btn, stretch=1)

    def mouseReleaseEvent(self, event):
        QuolBaseTitleBar.mouseReleaseEvent(self, event)
        geometry = QRect(
            round(self.quol_window.geometry().x() / 10) * 10,
            round(self.quol_window.geometry().y() / 10) * 10,
            self.quol_window.geometry().width(),
            self.quol_window.geometry().height()
        )

        self.quol_window.setGeometry(geometry)
        self.quol_window.config['_']['geometry'] = [geometry.x(), geometry.y(), geometry.width(), geometry.height()]
        self.quol_window.window_info.save_config(self.quol_window.config)


class QuolSubTitleBar(QuolBaseTitleBar):
    def __init__(self, quol_window: "QuolSubWindow", title):
        super().__init__(quol_window, title)

        self.close_btn = QPushButton('✕')
        self.close_btn.clicked.connect(quol_window.close)
        self.l1.addWidget(self.close_btn, stretch=1)