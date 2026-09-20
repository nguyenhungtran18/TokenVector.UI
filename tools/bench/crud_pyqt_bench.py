"""Benchmark CRUD PyQt6 doi chung: 1000 rows add/sort/select/update/delete.

Chay:  QT_QPA_PLATFORM=offscreen python3 tools/bench/crud_pyqt_bench.py
"""
import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtCore import Qt

DB = "build/staff_pyqt_bench.db"
if os.path.exists(DB):
    os.remove(DB)

app = QApplication([])
db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName(DB)
assert db.open()
db.exec("CREATE TABLE staff(id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INT, city TEXT)")

m = QSqlTableModel()
m.setTable("staff")
m.select()

t0 = time.perf_counter()
for i in range(1000):
    r = m.rowCount()
    m.insertRow(r)
    m.setData(m.index(r, 1), f"Name{i}")
    m.setData(m.index(r, 2), 20 + (i % 50))
    m.setData(m.index(r, 3), f"City{i % 20}")
m.submitAll()
t_ins = (time.perf_counter() - t0) * 1000.0

t0 = time.perf_counter()
m.setSort(1, Qt.SortOrder.AscendingOrder)
m.select()
n = m.rowCount()
vals = [m.data(m.index(r, 1)) for r in range(n)]
t_sel = (time.perf_counter() - t0) * 1000.0

t0 = time.perf_counter()
for i in range(1000):
    m.setData(m.index(i, 2), 25)
m.submitAll()
t_upd = (time.perf_counter() - t0) * 1000.0

t0 = time.perf_counter()
for i in range(999, -1, -1):
    m.removeRow(i)
m.submitAll()
m.select()
t_del = (time.perf_counter() - t0) * 1000.0

print(f"INSERT 1000: {t_ins:.0f}ms")
print(f"SELECT+SORT 1000: {t_sel:.0f}ms")
print(f"UPDATE 1000: {t_upd:.0f}ms")
print(f"DELETE 1000: {t_del:.0f}ms")
print(f"TOTAL: {t_ins + t_sel + t_upd + t_del:.0f}ms")
print(f"rows_after={m.rowCount()} file_bytes={os.path.getsize(DB)}")
