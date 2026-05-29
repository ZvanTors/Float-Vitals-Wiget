import sys
import time
from collections import deque
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QProgressBar, QFrame, QListWidget,
                             QListWidgetItem, QSizePolicy, QPushButton)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont
import psutil

# ---------- نوار وضعیت شناور ----------
class StatusBarWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusBar")
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(25)

        self.lbl_cpu = QLabel("🖥️ CPU: --%")
        self.lbl_ram = QLabel("🧠 RAM: --%")
        self.lbl_net = QLabel("⬇ 0.0  ⬆ 0.0 KB/s")

        for lbl in (self.lbl_cpu, self.lbl_ram, self.lbl_net):
            lbl.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
            layout.addWidget(lbl)

        layout.addStretch()

        self.btn_close = QPushButton("✕")
        self.btn_close.setStyleSheet("""
            QPushButton {
                color: #ff5555; font-size: 18px; font-weight: bold;
                background: transparent; border: none; padding: 0px 6px;
            }
            QPushButton:hover { color: #ff4444; }
        """)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.close_app)
        layout.addWidget(self.btn_close)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(1000)

        self.last_net = psutil.net_io_counters()
        self.last_time = time.time()

    def close_app(self):
        QApplication.instance().quit()

    def format_speed(self, kb_per_sec):
        if kb_per_sec >= 1024:
            return f"{kb_per_sec/1024:.1f} MB/s"
        return f"{kb_per_sec:.1f} KB/s"

    def refresh(self):
        cpu = psutil.cpu_percent(interval=None)
        self.lbl_cpu.setText(f"🖥️ CPU: {cpu:.0f}%")

        mem = psutil.virtual_memory()
        self.lbl_ram.setText(f"🧠 RAM: {mem.percent:.0f}%")

        now = time.time()
        new_net = psutil.net_io_counters()
        elapsed = now - self.last_time
        if elapsed > 0:
            dl_speed = (new_net.bytes_recv - self.last_net.bytes_recv) / elapsed
            ul_speed = (new_net.bytes_sent - self.last_net.bytes_sent) / elapsed
        else:
            dl_speed = ul_speed = 0.0
        self.last_net = new_net
        self.last_time = now

        dl_kb = dl_speed / 1024
        ul_kb = ul_speed / 1024

        dl_text = self.format_speed(dl_kb)
        ul_text = self.format_speed(ul_kb)
        self.lbl_net.setText(f"⬇ {dl_text}  ⬆ {ul_text}")

        if self.window() and hasattr(self.window(), 'network_widget'):
            self.window().network_widget.update_speed(dl_kb, ul_kb)

# ---------- نمودار شبکه بدون برچسب Download/Upload ----------
class NetworkGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.download_history = deque([0]*60, maxlen=60)
        self.upload_history = deque([0]*60, maxlen=60)
        self.max_speed = 1.0

    def update_speed(self, dl_kb, ul_kb):
        self.download_history.append(dl_kb)
        self.upload_history.append(ul_kb)
        all_vals = list(self.download_history) + list(self.upload_history)
        if all_vals:
            self.max_speed = max(max(all_vals), 1.0)
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        slot_width = w // 60
        bar_width = max(2, slot_width // 2 - 1)

        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        baseline = h - 10

        for i in range(60):
            dl_val = self.download_history[i]
            ul_val = self.upload_history[i]

            dl_h = int((dl_val / self.max_speed) * (h - 20))
            ul_h = int((ul_val / self.max_speed) * (h - 20))

            x_start = i * slot_width + 1
            painter.fillRect(int(x_start), baseline - dl_h, bar_width, dl_h,
                             QColor(0, 200, 100, 220))
            painter.fillRect(int(x_start + bar_width + 1), baseline - ul_h, bar_width, ul_h,
                             QColor(255, 150, 0, 220))

        # برچسب‌ها حذف شدند

# ---------- لیست درایوها (فقط نام درایو، بدون مسیر تکراری) ----------
class DriveListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 10)
        self.list = QListWidget()
        self.list.setStyleSheet("QListWidget { background: transparent; border: none; }")
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.list)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(5000)
        self.refresh()

    def refresh(self):
        self.list.clear()
        item_height = 40
        num_drives = 0

        for part in psutil.disk_partitions():
            if 'cdrom' in part.opts or part.fstype == '':
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except PermissionError:
                continue

            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(5, 2, 5, 2)

            icon_label = QLabel("💿")
            icon_label.setStyleSheet("color: white; font-size: 14px;")
            item_layout.addWidget(icon_label)

            # فقط نام درایو، بدون mountpoint
            name = QLabel(f"{part.device}")
            name.setStyleSheet("color: white; font-size: 12px;")

            free = QLabel(f"{usage.free / (1024**3):.1f} GB free / {usage.total / (1024**3):.1f} GB")
            free.setStyleSheet("color: #bbbbbb; font-size: 11px;")
            bar = QProgressBar()
            bar.setMaximum(100)
            bar.setValue(int(usage.percent))
            bar.setTextVisible(True)
            bar.setFormat(f"{usage.percent:.1f}%")
            bar.setFixedHeight(18)
            bar.setStyleSheet("""
                QProgressBar {
                    background-color: #2a2a2a;
                    border-radius: 4px;
                    text-align: center;
                    color: white;
                    font-size: 10px;
                }
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00c853, stop:1 #69f0ae);
                    border-radius: 4px;
                }
            """)

            item_layout.addWidget(name)
            item_layout.addWidget(free)
            item_layout.addWidget(bar)

            list_item = QListWidgetItem(self.list)
            list_item.setSizeHint(item_widget.sizeHint())
            self.list.addItem(list_item)
            self.list.setItemWidget(list_item, item_widget)
            num_drives += 1

        if num_drives > 0:
            total_height = num_drives * item_height + 10
            self.list.setMaximumHeight(total_height)
        else:
            self.list.setMaximumHeight(50)

# ---------- پنجره اصلی ----------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(500, 200)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.status_bar = StatusBarWidget(self)
        main_layout.addWidget(self.status_bar)

        self.network_widget = NetworkGraphWidget(self)
        main_layout.addWidget(self.network_widget)

        self.drive_widget = DriveListWidget(self)
        main_layout.addWidget(self.drive_widget)
        main_layout.addStretch()

        self.status_bar.mousePressEvent = self.start_move
        self.status_bar.mouseMoveEvent = self.do_move
        self.old_pos = None

    def start_move(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def do_move(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()

    def closeEvent(self, event):
        QApplication.instance().quit()
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        bg_color = QColor(20, 20, 20, 210)
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())