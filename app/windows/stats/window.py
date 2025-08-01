import psutil
from GPUtil import GPUtil
import pyqtgraph as pg
from PySide6.QtCore import QTimer, QThread, Signal, QObject, Qt
from PySide6.QtWidgets import QLabel, QTableWidget, QHeaderView, QTableWidgetItem

from lib.quol_window import QuolMainWindow
from lib.window_loader import WindowInfo, WindowContext


class MainWindow(QuolMainWindow):
    def __init__(self, window_info: WindowInfo, window_context: WindowContext):
        super().__init__('Stats', window_info, window_context, default_geometry=(300, 300, 200, 1))

        self.max_points = 60
        self.cpu_data = [0] * self.max_points
        self.ram_data = [0] * self.max_points
        self.gpu_data = [0] * self.max_points
        self.gpu_percent = 0
        self.top_procs = []

        # Graphs
        self.cpu_plot, self.cpu_curve = self.create_plot("CPU (%)", 'cyan')
        self.ram_plot, self.ram_curve = self.create_plot("RAM (%)", 'orange')
        self.gpu_plot, self.gpu_curve = self.create_plot("GPU (%)", 'green')
        self.plots = [self.cpu_plot, self.ram_plot, self.gpu_plot]
        self.current_plot_index = 0

        self.layout.addWidget(self.plots[self.current_plot_index])
        self.plots[self.current_plot_index].setFixedSize(180, 150)
        self.plots[self.current_plot_index].scene().sigMouseClicked.connect(self.cycle_plot)

        # Network label
        self.net_label = QLabel("↑ 0.0 KB/s ↓ 0.0 KB/s")
        self.layout.addWidget(self.net_label)
        self.last_net_io = psutil.net_io_counters()

        # Process table (2 columns only)
        self.process_table = QTableWidget(3, 2)
        self.process_table.setHorizontalHeaderLabels(["Process", "CPU %"])
        header = self.process_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.process_table.verticalHeader().setVisible(False)
        self.process_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.process_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.process_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.process_table.setFocusPolicy(Qt.NoFocus)
        self.process_table.setSelectionMode(QTableWidget.NoSelection)
        self.layout.addWidget(self.process_table)

        # Timers
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_main_stats)
        self.timer.start(1000)

        # Background thread
        self.worker = BackgroundWorker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker.updated.connect(self.update_background_stats)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    def create_plot(self, title, color):
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('#1e1e1e')
        plot_widget.showGrid(x=True, y=True)
        plot_widget.setYRange(0, 100)
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
        next_plot.setFixedSize(180, 150)
        next_plot.show()
        next_plot.scene().sigMouseClicked.connect(self.cycle_plot)

        # Update process column header
        metric = ["CPU %", "RAM %", "GPU %"][self.current_plot_index]
        self.process_table.setHorizontalHeaderLabels(["Process", metric])
        self.refresh_process_table()

    def update_main_stats(self):
        cpu_percent = psutil.cpu_percent()
        self.cpu_data.append(cpu_percent)
        self.cpu_data = self.cpu_data[-self.max_points:]
        self.cpu_curve.setData(self.cpu_data)
        self.cpu_plot.setTitle(f"CPU ({cpu_percent:.1f}%)")

        ram = psutil.virtual_memory()
        self.ram_data.append(ram.percent)
        self.ram_data = self.ram_data[-self.max_points:]
        self.ram_curve.setData(self.ram_data)
        self.ram_plot.setTitle(f"RAM ({ram.percent:.1f}%)")

        self.gpu_data.append(self.gpu_percent)
        self.gpu_data = self.gpu_data[-self.max_points:]
        self.gpu_curve.setData(self.gpu_data)
        self.gpu_plot.setTitle(f"GPU ({self.gpu_percent:.1f}%)")

        net_io = psutil.net_io_counters()
        sent_speed = (net_io.bytes_sent - self.last_net_io.bytes_sent) / 1024
        recv_speed = (net_io.bytes_recv - self.last_net_io.bytes_recv) / 1024
        self.net_label.setText(f"↑ {sent_speed:.1f} KB/s   ↓ {recv_speed:.1f} KB/s")
        self.last_net_io = net_io

        self.refresh_process_table()

    def refresh_process_table(self):
        self.process_table.setRowCount(len(self.top_procs))
        metric_index = self.current_plot_index  # 0 = CPU, 1 = RAM, 2 = GPU
        metric_keys = ['cpu_percent', 'memory_percent', 'gpu_percent']
        for row, proc in enumerate(self.top_procs):
            name_item = QTableWidgetItem(proc['name'][:20])
            value = proc.get(metric_keys[metric_index], 0.0)
            value_item = QTableWidgetItem(f"{value:.1f}")
            for col, item in enumerate([name_item, value_item]):
                item.setTextAlignment(Qt.AlignCenter)
                self.process_table.setItem(row, col, item)

    def update_background_stats(self, top_procs, gpu_percent):
        self.gpu_percent = gpu_percent
        # Add gpu_percent to each process dict for flexibility
        for p in top_procs:
            p['gpu_percent'] = gpu_percent
        self.top_procs = top_procs

    def closeEvent(self, event):
        self.worker.running = False
        self.worker_thread.quit()
        self.worker_thread.wait()
        super().closeEvent(event)


class BackgroundWorker(QObject):
    updated = Signal(list, float)  # processes, gpu_percent

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        while self.running:
            try:
                procs = [
                    p.info for p in psutil.process_iter(['name', 'cpu_percent', 'memory_percent'])
                    if p.info['cpu_percent'] is not None
                ]
                top_procs = sorted(procs, key=lambda p: (p['cpu_percent'], p['memory_percent']), reverse=True)[:3]
            except Exception:
                top_procs = []

            try:
                gpus = GPUtil.getGPUs()
                gpu_percent = gpus[0].load * 100 if gpus else 0
            except Exception:
                gpu_percent = 0

            self.updated.emit(top_procs, gpu_percent)

            for _ in range(30):  # sleep for 3 seconds total
                if not self.running:
                    return
                QThread.msleep(100)
