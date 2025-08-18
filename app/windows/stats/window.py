import heapq
from collections import deque

import psutil
from GPUtil import GPUtil
import pyqtgraph as pg
from PySide6.QtCore import QTimer, QThread, Signal, QObject, Qt
from PySide6.QtWidgets import QLabel, QTableWidget, QHeaderView, QTableWidgetItem

from lib.quol_window import QuolMainWindow
from lib.window_loader import WindowInfo, WindowContext


class MainWindow(QuolMainWindow):
    def __init__(self, window_info: WindowInfo, window_context: WindowContext):
        super().__init__('Stats', window_info, window_context, default_geometry=(10, 130, 180, 1), show_config=False)

        self.max_points = 60
        self.cpu_data = deque([0.0] * self.max_points, maxlen=self.max_points)
        self.ram_data = deque([0.0] * self.max_points, maxlen=self.max_points)
        self.gpu_data = deque([0.0] * self.max_points, maxlen=self.max_points)
        self.gpu_percent = 0
        self.top_procs = []

        self.cpu_plot, self.cpu_curve = self.create_plot("CPU (%)", 'cyan')
        self.ram_plot, self.ram_curve = self.create_plot("RAM (%)", 'orange')
        self.gpu_plot, self.gpu_curve = self.create_plot("GPU (%)", 'green')
        self.plots = [self.cpu_plot, self.ram_plot, self.gpu_plot]
        self.metrics = ["CPU", "RAM", "GPU"]
        self.current_plot_index = 0

        self.layout.addWidget(self.plots[self.current_plot_index])
        self.plots[self.current_plot_index].scene().sigMouseClicked.connect(self.cycle_plot)

        self.process_table = QTableWidget(3, 2)
        header = self.process_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setVisible(False)
        self.process_table.verticalHeader().setVisible(False)
        self.process_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.process_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.process_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.process_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.process_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.layout.addWidget(self.process_table)

        self.net_label = QLabel("↑ 0.0 KB/s ↓ 0.0 KB/s")
        self.layout.addWidget(self.net_label)
        self.last_net_io = psutil.net_io_counters()

        # Timers
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_main_stats)
        self.timer.start(1000)

        # Background thread
        self.worker = BackgroundWorker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker.updated.connect(self.update_background_stats)
        self.worker_thread.started.connect(self.worker.start)
        self.worker_thread.start()

    def create_plot(self, title, color):
        plot_widget = pg.PlotWidget()
        plot_widget.setMinimumHeight(90)

        plot_widget.setBackground('#1e1e1e')
        plot_widget.showGrid(x=True, y=True)
        plot_widget.getAxis('bottom').setTicks([])
        plot_widget.plotItem.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)

        curve = plot_widget.plot(pen=pg.mkPen(color=color, width=2))
        plot_widget.setTitle(f"{title} (0%)")
        return plot_widget, curve

    def cycle_plot(self, event):
        current_plot = self.plots[self.current_plot_index]
        self.layout.removeWidget(current_plot)
        current_plot.scene().sigMouseClicked.disconnect(self.cycle_plot)
        current_plot.hide()

        self.current_plot_index = (self.current_plot_index + 1) % len(self.plots)
        next_plot = self.plots[self.current_plot_index]

        self.layout.insertWidget(0, next_plot)
        next_plot.show()
        next_plot.scene().sigMouseClicked.connect(self.cycle_plot)

        metric = self.metrics[self.current_plot_index]
        self.process_table.setHorizontalHeaderLabels(["Process", metric])
        self.update_process_table()

    def update_main_stats(self):
        cpu_percent = psutil.cpu_percent()
        self.cpu_data.append(cpu_percent)
        self.cpu_curve.setData(list(self.cpu_data))
        self.cpu_plot.setTitle(f"CPU ({cpu_percent:.1f}%)")

        ram = psutil.virtual_memory()
        self.ram_data.append(ram.percent)
        self.ram_curve.setData(list(self.ram_data))
        self.ram_plot.setTitle(f"RAM ({ram.percent:.1f}%)")

        self.gpu_data.append(self.gpu_percent)
        self.gpu_curve.setData(list(self.gpu_data))
        self.gpu_plot.setTitle(f"GPU ({self.gpu_percent:.1f}%)")

        net_io = psutil.net_io_counters()
        sent_speed = (net_io.bytes_sent - self.last_net_io.bytes_sent) / 1024
        recv_speed = (net_io.bytes_recv - self.last_net_io.bytes_recv) / 1024
        self.net_label.setText(f"↑ {sent_speed:.1f} KB/s   ↓ {recv_speed:.1f} KB/s")
        self.last_net_io = net_io

        self.update_process_table()

    def update_process_table(self):
        metric_index = self.current_plot_index
        metric_keys = ['cpu_percent', 'memory_percent', 'gpu_percent']
        metric_key = metric_keys[metric_index]

        top3 = heapq.nlargest(3, self.top_procs, key=lambda p: p.get(metric_key, 0.0))

        self.process_table.setRowCount(len(top3))

        for row, proc in enumerate(top3):
            name_item = QTableWidgetItem(proc['name'][:20])
            value = proc.get(metric_key, 0.0)
            value_item = QTableWidgetItem(f"{value:.1f}%")
            for col, item in enumerate([name_item, value_item]):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.process_table.setItem(row, col, item)

        self.process_table.setFixedHeight(75)
        self.process_table.setRowHeight(0, 5)
        self.process_table.setRowHeight(1, 5)

    def update_background_stats(self, top_procs, gpu_percent):
        self.gpu_percent = gpu_percent
        self.top_procs = top_procs

    def closeEvent(self, event):
        self.worker.stop()
        self.worker_thread.quit()
        self.worker_thread.wait()
        super().closeEvent(event)


class BackgroundWorker(QObject):
    updated = Signal(list, float)

    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.fetch_stats)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def fetch_stats(self):
        try:
            procs = []
            for p in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
                info = p.info
                if info['cpu_percent'] is None or (info['cpu_percent'] / psutil.cpu_count() < 0.1 and info['memory_percent'] < 1.0):
                    continue
                elif info['name'] in {'System Idle Process', 'MemCompression'}:
                    continue
                procs.append({
                    'name': info.get('name', 'Unknown'),
                    'cpu_percent': info.get('cpu_percent', 0.0) / psutil.cpu_count(),
                    'memory_percent': info.get('memory_percent', 0.0)
                })
        except Exception:
            procs = []

        try:
            gpus = GPUtil.getGPUs()
            gpu_percent = gpus[0].load * 100 if gpus else 0.0
        except Exception:
            gpu_percent = 0.0

        for proc in procs:
            proc['gpu_percent'] = gpu_percent

        self.updated.emit(procs, gpu_percent)
