import sqlite3
from datetime import datetime, timedelta
import psutil
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtCharts import *
import time

class DB:
    def __init__(self, p="sys.db"):
        self.p = p
        self.init()

    def init(self):
        c = sqlite3.connect(self.p)
        cr = c.cursor()
        cr.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu REAL,
                mem_tot INTEGER,
                mem_av INTEGER,
                mem_used INTEGER,
                mem_pct REAL,
                dsk_pct REAL,
                bsent INTEGER,
                brecv INTEGER
            )
        ''')
        cr.execute('''
            CREATE TABLE IF NOT EXISTS proc_hist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts DATETIME DEFAULT CURRENT_TIMESTAMP,
                pid INTEGER,
                name TEXT,
                cpu REAL,
                mem_pct REAL,
                mem_rss INTEGER,
                stat TEXT
            )
        ''')
        cr.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts DATETIME DEFAULT CURRENT_TIMESTAMP,
                typ TEXT,
                msg TEXT,
                proc TEXT,
                val REAL,
                res INTEGER DEFAULT 0
            )
        ''')
        cr.execute('''
            CREATE TABLE IF NOT EXISTS proc_ev (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts DATETIME DEFAULT CURRENT_TIMESTAMP,
                ev_typ TEXT,
                pid INTEGER,
                name TEXT
            )
        ''')
        c.commit()
        c.close()

class MetricCol(QThread):
    sig = pyqtSignal(dict)

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.runn = True
        self.prev_net = psutil.net_io_counters()

    def run(self):
        while self.runn:
            try:
                m = self.coll()
                self.sig.emit(m)
                self.save(m)
                self.msleep(5000)
            except:
                pass

    def coll(self):
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        dsk = psutil.disk_usage('/')
        dsk_pct = (dsk.used / dsk.total) * 100
        net = psutil.net_io_counters()
        bsent = net.bytes_sent - self.prev_net.bytes_sent
        brecv = net.bytes_recv - self.prev_net.bytes_recv
        self.prev_net = net
        return {
            'ts': datetime.now(),
            'cpu': cpu,
            'mem_tot': mem.total,
            'mem_av': mem.available,
            'mem_used': mem.used,
            'mem_pct': mem.percent,
            'dsk_pct': dsk_pct,
            'bsent': bsent,
            'brecv': brecv
        }

    def save(self, m):
        c = sqlite3.connect(self.db.p)
        cr = c.cursor()
        cr.execute('''
            INSERT INTO metrics (cpu, mem_tot, mem_av, mem_used, mem_pct, dsk_pct, bsent, brecv)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (m['cpu'], m['mem_tot'], m['mem_av'], m['mem_used'], m['mem_pct'], m['dsk_pct'], m['bsent'], m['brecv']))
        c.commit()
        c.close()

class AlertM:
    def __init__(self, db):
        self.db = db
        self.th = {
            'cpu': 90,
            'mem': 85,
            'dsk': 90,
            'proc_cpu': 50
        }

    def chk(self, m):
        al = []
        if m['cpu'] > self.th['cpu']:
            al.append({
                'type': 'high_cpu',
                'msg': f'High CPU: {m["cpu"]:.1f}%',
                'val': m['cpu']
            })
        if m['mem_pct'] > self.th['mem']:
            al.append({
                'type': 'high_mem',
                'msg': f'High Memory: {m["mem_pct"]:.1f}%',
                'val': m['mem_pct']
            })
        if m['dsk_pct'] > self.th['dsk']:
            al.append({
                'type': 'high_dsk',
                'msg': f'High Disk: {m["dsk_pct"]:.1f}%',
                'val': m['dsk_pct']
            })
        self.save_al(al)

    def save_al(self, al):
        c = sqlite3.connect(self.db.p)
        cr = c.cursor()
        for a in al:
            cr.execute('''
                INSERT INTO alerts (typ, msg, val)
                VALUES (?, ?, ?)
            ''', (a['type'], a['msg'], a['val']))
        c.commit()
        c.close()

class AnaTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        l = QVBoxLayout()
        hl = QHBoxLayout()
        hl.addWidget(QLabel("Period:"))
        self.pc = QComboBox()
        self.pc.addItems(["1h", "6h", "24h", "7d"])
        hl.addWidget(self.pc)
        hl.addStretch()
        self.tw = QTabWidget()
        self.ch_tab = QWidget()
        self.init_charts()
        self.tw.addTab(self.ch_tab, "Charts")
        self.ps_tab = QWidget()
        self.init_proc_stats()
        self.tw.addTab(self.ps_tab, "Proc Stats")
        self.al_tab = QWidget()
        self.init_alerts()
        self.tw.addTab(self.al_tab, "Alerts")
        l.addLayout(hl)
        l.addWidget(self.tw)
        self.setLayout(l)

    def init_charts(self):
        vl = QVBoxLayout()
        self.chart_view = QChartView()
        vl.addWidget(self.chart_view)
        self.ch_tab.setLayout(vl)
        self.update_charts()

    def update_charts(self):
        per = self.pc.currentText()
        if per == "1h":
            td = "1 hour"
        elif per == "6h":
            td = "6 hours"
        elif per == "24h":
            td = "1 day"
        else:
            td = "7 days"
        c = sqlite3.connect(self.db.p)
        cr = c.cursor()
        cr.execute(f'''
            SELECT ts, cpu, mem_pct, dsk_pct
            FROM metrics
            WHERE ts > datetime('now', '-{td}')
            ORDER BY ts
        ''')
        rows = cr.fetchall()
        c.close()
        t = QChart()
        t.setTitle("Metrics Over Time")
        ax_x = QDateTimeAxis()
        ax_x.setTitleText("Time")
        ax_y = QValueAxis()
        ax_y.setTitleText("Percent")
        t.addAxis(ax_x, Qt.AlignmentFlag.AlignBottom)
        t.addAxis(ax_y, Qt.AlignmentFlag.AlignLeft)
        cpu_s = QLineSeries()
        cpu_s.setName("CPU %")
        mem_s = QLineSeries()
        mem_s.setName("Memory %")
        dsk_s = QLineSeries()
        dsk_s.setName("Disk %")
        for r in rows:
            dt = QDateTime.fromString(r[0], "yyyy-MM-dd hh:mm:ss")
            cpu_s.append(dt.toMSecsSinceEpoch(), r[1])
            mem_s.append(dt.toMSecsSinceEpoch(), r[2])
            dsk_s.append(dt.toMSecsSinceEpoch(), r[3])
        t.addSeries(cpu_s)
        t.addSeries(mem_s)
        t.addSeries(dsk_s)
        cpu_s.attachAxis(ax_x)
        cpu_s.attachAxis(ax_y)
        mem_s.attachAxis(ax_x)
        mem_s.attachAxis(ax_y)
        dsk_s.attachAxis(ax_x)
        dsk_s.attachAxis(ax_y)
        self.chart_view.setChart(t)

    def init_proc_stats(self):
        vl = QVBoxLayout()
        self.ps_tbl = QTableWidget()
        self.ps_tbl.setColumnCount(5)
        self.ps_tbl.setHorizontalHeaderLabels(["Proc", "Avg CPU %", "Max CPU %", "Avg Mem %", "Runtime"])
        vl.addWidget(self.ps_tbl)
        self.ps_tab.setLayout(vl)
        self.update_proc_stats()

    def update_proc_stats(self):
        per = self.pc.currentText()
        if per == "1h":
            td = "1 hour"
        elif per == "6h":
            td = "6 hours"
        elif per == "24h":
            td = "1 day"
        else:
            td = "7 days"
        c = sqlite3.connect(self.db.p)
        cr = c.cursor()
        cr.execute(f'''
            SELECT name, AVG(cpu), MAX(cpu), AVG(mem_pct), COUNT(*)*5
            FROM proc_hist
            WHERE ts > datetime('now', '-{td}')
            GROUP BY name
            ORDER BY AVG(cpu) DESC
            LIMIT 20
        ''')
        rows = cr.fetchall()
        c.close()
        self.ps_tbl.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.ps_tbl.setItem(i, 0, QTableWidgetItem(str(r[0])))
            self.ps_tbl.setItem(i, 1, QTableWidgetItem(f"{r[1]:.2f}"))
            self.ps_tbl.setItem(i, 2, QTableWidgetItem(f"{r[2]:.2f}"))
            self.ps_tbl.setItem(i, 3, QTableWidgetItem(f"{r[3]:.2f}"))
            self.ps_tbl.setItem(i, 4, QTableWidgetItem(f"{r[4]*5}s"))

    def init_alerts(self):
        vl = QVBoxLayout()
        self.al_tbl = QTableWidget()
        self.al_tbl.setColumnCount(4)
        self.al_tbl.setHorizontalHeaderLabels(["Time", "Type", "Message", "Value"])
        vl.addWidget(self.al_tbl)
        self.al_tab.setLayout(vl)
        self.update_alerts()

    def update_alerts(self):
        c = sqlite3.connect(self.db.p)
        cr = c.cursor()
        cr.execute('''
            SELECT ts, typ, msg, val
            FROM alerts
            ORDER BY ts DESC
            LIMIT 50
        ''')
        rows = cr.fetchall()
        c.close()
        self.al_tbl.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.al_tbl.setItem(i, 0, QTableWidgetItem(str(r[0])))
            self.al_tbl.setItem(i, 1, QTableWidgetItem(str(r[1])))
            self.al_tbl.setItem(i, 2, QTableWidgetItem(str(r[2])))
            self.al_tbl.setItem(i, 3, QTableWidgetItem(f"{r[3]:.2f}"))

class ProcEvM:
    def __init__(self, db):
        self.db = db
        self.known_pids = set()

    def scan(self):
        c = sqlite3.connect(self.db.p)
        cr = c.cursor()
        for p in psutil.process_iter(['pid', 'name']):
            try:
                pid = p.info['pid']
                name = p.info['name']
                if pid not in self.known_pids:
                    cr.execute('''
                        INSERT INTO proc_ev (ev_typ, pid, name)
                        VALUES (?, ?, ?)
                    ''', ("start", pid, name))
                    self.known_pids.add(pid)
            except:
                pass
        c.commit()
        c.close()

class ProcTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.proc_table = QTableWidget()
        self.proc_table.setColumnCount(5)
        self.proc_table.setHorizontalHeaderLabels(["PID", "Name", "CPU %", "Memory %", "RSS (MB)"])
        self.proc_table.setSortingEnabled(True)  # Включаем сортировку по столбцам
        layout.addWidget(self.proc_table)
        self.setLayout(layout)
        self.update_processes()

    def update_processes(self):
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
            try:
                pid = p.info['pid']
                name = p.info['name'] or "N/A"
                cpu = p.info['cpu_percent'] or 0.0
                mem_pct = p.info['memory_percent'] or 0.0
                rss = p.info['memory_info'].rss if p.info['memory_info'] else 0
                rss_mb = rss / (1024 * 1024)
                procs.append((pid, name, cpu, mem_pct, rss_mb))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Сортируем по CPU% (по убыванию)
        procs.sort(key=lambda x: x[2], reverse=True)

        self.proc_table.setRowCount(len(procs))
        for i, (pid, name, cpu, mem_pct, rss_mb) in enumerate(procs):
            self.proc_table.setItem(i, 0, QTableWidgetItem(str(pid)))
            self.proc_table.setItem(i, 1, QTableWidgetItem(name))
            self.proc_table.setItem(i, 2, QTableWidgetItem(f"{cpu:.1f}"))
            self.proc_table.setItem(i, 3, QTableWidgetItem(f"{mem_pct:.1f}"))
            self.proc_table.setItem(i, 4, QTableWidgetItem(f"{rss_mb:.1f}"))

class MainWin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DB()
        self.al_m = AlertM(self.db)
        self.proc_ev_m = ProcEvM(self.db)
        self.init_ui()
        self.metric_col = MetricCol(self.db)
        self.metric_col.sig.connect(self.on_m_upd)
        self.metric_col.start()

        # Таймер для обновления аналитики И процессов
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all)
        self.timer.start(30000)  # каждые 30 сек

        # Доп. таймер для обновления live-процессов (чаще)
        self.proc_timer = QTimer()
        self.proc_timer.timeout.connect(self.proc_tab.update_processes)
        self.proc_timer.start(3000)  # каждые 3 сек

    def init_ui(self):
        self.setWindowTitle("SysMon")
        self.setGeometry(100, 100, 1200, 800)
        self.tw = QTabWidget()

        # Аналитика (история)
        self.ana_tab = AnaTab(self.db)
        self.tw.addTab(self.ana_tab, "Analytics")

        # Live процессы
        self.proc_tab = ProcTab(self.db)
        self.tw.addTab(self.proc_tab, "Processes")

        self.setCentralWidget(self.tw)

    def on_m_upd(self, m):
        self.al_m.chk(m)
        c = sqlite3.connect(self.db.p)
        cr = c.cursor()
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
            try:
                pid = p.pid
                name = p.name()
                cpu = p.cpu_percent()
                mem_pct = p.memory_percent() or 0.0
                mem_rss = p.memory_info().rss if p.memory_info() else 0
                cr.execute('''
                    INSERT INTO proc_hist (pid, name, cpu, mem_pct, mem_rss)
                    VALUES (?, ?, ?, ?, ?)
                ''', (pid, name, cpu, mem_pct, mem_rss))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        c.commit()
        c.close()

    def update_all(self):
        self.ana_tab.update_charts()
        self.ana_tab.update_proc_stats()
        self.ana_tab.update_alerts()
        self.proc_ev_m.scan()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec())