import queue
import time
import threading

import imageio.v2 as imageio
import numpy as np
from mss import mss

from PySide6.QtWidgets import (
    QLabel, QPushButton, QComboBox, QLineEdit, QWidget, QApplication
)
from PySide6.QtCore import Signal, Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QPixmap, QColor, QPen, QKeySequence, QMouseEvent, QCursor

from lib.quol_window import QuolMainWindow
from lib.window_loader import WindowInfo, WindowContext


class MainWindow(QuolMainWindow):
    status_updated = Signal(str)

    def __init__(self, window_info: WindowInfo, window_context: WindowContext):
        super().__init__('Screen Recorder', window_info, window_context, default_geometry=(1340, 10, 200, 1))

        self.recording = False
        self.fps = 60  # target capture fps
        self.output_path = self.window_info.path + "/res/recording.mp4"
        self.crop_selector = CropSelectorWidget(self.window_context)
        self.crop_selector.crop_selected.connect(self.set_crop_rect)

        # UI elements
        self.mode_select = QComboBox()
        self.mode_select.addItems(["Full Screen", "Crop Region"])

        self.crop_input = QLineEdit("100,100,800,600")
        self.crop_input.setReadOnly(True)

        self.crop_button = QPushButton("Select Crop Region")
        self.crop_button.clicked.connect(lambda: self.crop_selector.start())

        self.start_btn = QPushButton("Start Recording")
        self.start_btn.clicked.connect(self.toggle_recording)

        self.status = QLabel("Status: Idle")

        self.layout.addWidget(QLabel("Recording Mode:"))
        self.layout.addWidget(self.mode_select)
        self.layout.addWidget(self.crop_button)
        self.layout.addWidget(self.crop_input)
        self.layout.addWidget(self.start_btn)
        self.layout.addWidget(self.status)

        self.status_updated.connect(self.status.setText)

        # Internal state
        self.frame_queue = None
        self.stop_signal = None
        self.writer_thread = None

    def set_crop_rect(self, x, y, w, h):
        self.crop_input.setText(f"{x},{y},{w},{h}")

    def toggle_recording(self):
        if self.recording:
            # Stop
            self.recording = False
            self.start_btn.setText("Start Recording")
            self.status_updated.emit("Status: Stopped")
            self.mode_select.setEnabled(True)
        else:
            # Start
            self.recording = True
            self.start_btn.setText("Stop Recording")
            self.status_updated.emit("Status: Recording...")
            self.mode_select.setEnabled(False)
            self.crop_input.setEnabled(False)
            self.crop_button.setEnabled(False)

            self.writer_thread = None  # clear old writer thread
            threading.Thread(target=self.record_screen, daemon=True).start()

    def writer_thread_func(self, frame_queue, stop_signal, fps):
        writer = imageio.get_writer(self.output_path, fps=fps)
        while True:
            frame = frame_queue.get()
            if frame is stop_signal:
                break
            writer.append_data(frame)
        writer.close()

    def record_screen(self):
        mode = self.mode_select.currentText()
        sct = mss()

        # Get capture area
        if mode == "Crop Region":
            try:
                x, y, w, h = map(int, self.crop_input.text().split(','))
            except ValueError:
                self.status_updated.emit("Status: Invalid crop format")
                self._reset_ui_on_error()
                return
        else:
            mon = sct.monitors[1]
            x, y, w, h = mon["left"], mon["top"], mon["width"], mon["height"]

        self.frame_queue = queue.Queue(maxsize=1)  # avoid backlog
        self.stop_signal = object()

        # FPS measurement setup
        target_interval = 1.0 / self.fps
        frame_count = 0
        start_time = time.perf_counter()
        measured_fps = None

        while self.recording:
            loop_start = time.perf_counter()

            # continue if we're not ready to capture the next frame
            if measured_fps is not None:
                elapsed = loop_start - start_time
                if elapsed < target_interval:
                    time.sleep(target_interval - elapsed)

            # Grab and convert frame
            img = np.array(sct.grab({"top": y, "left": x, "width": w, "height": h}))
            frame = img[:, :, :3][:, :, ::-1]  # BGRA → RGB

            # Enqueue frame
            try:
                self.frame_queue.put_nowait(frame)
            except queue.Full:
                print("⚠️ Frame queue full — dropping frame")

            # FPS measurement
            frame_count += 1
            elapsed = loop_start - start_time
            if elapsed >= 1.0:
                measured_fps = frame_count / elapsed
                print(f"📸 Capture FPS: {measured_fps:.2f}")

                # Start writer thread once FPS known
                if self.writer_thread is None:
                    self.writer_thread = threading.Thread(
                        target=self.writer_thread_func,
                        args=(self.frame_queue, self.stop_signal, measured_fps),
                        daemon=True,
                    )
                    self.writer_thread.start()

                frame_count = 0
                start_time = time.perf_counter()

        # Clean up
        self.frame_queue.put(self.stop_signal)
        if self.writer_thread:
            self.writer_thread.join()

    def _reset_ui_on_error(self):
        self.recording = False
        self.start_btn.setText("Start Recording")
        self.mode_select.setEnabled(True)
        self.update_crop_enabled()

    def close(self):
        if self.recording:
            self.recording = False
            self.frame_queue.put(self.stop_signal)
            if self.writer_thread:
                self.writer_thread.join()
        self.crop_selector.close()
        super().close()


class CropSelectorWidget(QWidget):
    crop_selected = Signal(int, int, int, int)  # x, y, w, h

    def __init__(self, context):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        screen_geometry = QApplication.primaryScreen().geometry()
        self.setFixedSize(screen_geometry.width(), screen_geometry.height() - 20)

        self.context = context
        self.start_point = None
        self.end_point = None
        self.screenshot = QPixmap()
        self.selecting = False

    def start(self):
        self.context.toggle_windows_instant(True)
        screen = QApplication.primaryScreen()
        self.screenshot = screen.grabWindow(0)
        self.start_point = None
        self.end_point = None
        self.selecting = False
        self.show()
        self.context.toggle_windows_instant(False)
        self.context.toggle_windows()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.start_point = event.position().toPoint()
            self.end_point = self.start_point
            self.selecting = True
            self.update()
            print(f"Crop started at: {self.start_point}")

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.selecting:
            self.end_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.selecting:
            self.end_point = event.position().toPoint()
            self.selecting = False
            self.emit_crop()
            self.context.toggle_windows()
            print(f"Crop selected: {self.start_point} to {self.end_point}")

    def emit_crop(self):
        if self.start_point and self.end_point:
            rect = QRect(self.start_point, self.end_point).normalized()
            self.crop_selected.emit(rect.x(), rect.y(), rect.width(), rect.height())
        self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.screenshot)

        overlay_color = QColor(0, 0, 0, 100)
        painter.fillRect(self.rect(), overlay_color)

        if self.start_point and self.end_point:
            rect = QRect(self.start_point, self.end_point).normalized()

            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(rect, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

            pen = QPen(QColor(255, 255, 255), 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(rect)

