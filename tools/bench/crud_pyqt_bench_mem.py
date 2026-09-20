"""Benchmark CRUD PyQt6 doi chung CHUAN HOA (2026-09-19): in-memory + reps.

Workload giong he TKV `examples/TkvUI.CrudBench.tkv` (sau chuan hoa):
  - 10 reps; moi rep: CREATE TABLE tuoi + INSERT 1000 + SELECT/SORT + UPDATE 1000 + DELETE 1000
  - DB :memory: (tuong duong TKV in-memory lists; khong fsync/file)
  - Report trung binh/rep moi op + runs.

Chay:  QT_QPA_PLATFORM=offscreen python3 tools/bench/crud_pyqt_bench_mem.py
"""
import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtCore import Qt

N = 1000
REPS = 10
SCHEMA = "CREATE TABLE staff(id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INT, city TEXT)"

app = QApplication([])
db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName(":memory:")
assert db.open()

t_ins, t_sel, t_upd, t_del = [], [], [], []
for _ in range(REPS):
    db.exec("DROP TABLE IF EXISTS staff")
    db.exec(SCHEMA)
    m = QSqlTableModel()
    m.setTable("staff")
    m.select()

    t0 = time.perf_counter()
    for i in range(N):
        r = m.rowCount()
        m.insertRow(r)
        m.setData(m.index(r, 1), f"Name{i}")
        m.setData(m.index(r, 2), 20 + (i % 50))
        m.setData(m.index(r, 3), f"City{i % 20}")
    m.submitAll()
    t_ins.append((time.perf_counter() - t0) * 1000.0)

    t0 = time.perf_counter()
    m.setSort(1, Qt.SortOrder.AscendingOrder)
    m.select()
    n = m.rowCount()
    vals = [m.data(m.index(r, 1)) for r in range(n)]
    t_sel.append((time.perf_counter() - t0) * 1000.0)

    t0 = time.perf_counter()
    for i in range(N):
        m.setData(m.index(i, 2), 25)
    m.submitAll()
    t_upd.append((time.perf_counter() - t0) * 1000.0)

    t0 = time.perf_counter()
    for i in range(N - 1, -1, -1):
        m.removeRow(i)
    m.submitAll()
    m.select()
    t_del.append((time.perf_counter() - t0) * 1000.0)


def avg(xs):
    return sum(xs) / len(xs)


print(f"INSERT 1000x{REPS}: avg={avg(t_ins):.1f}ms runs={[f'{t:.0f}' for t in t_ins]}")
print(f"SELECT+SORT 1000x{REPS}: avg={avg(t_sel):.1f}ms runs={[f'{t:.0f}' for t in t_sel]}")
print(f"UPDATE 1000x{REPS}: avg={avg(t_upd):.1f}ms runs={[f'{t:.0f}' for t in t_upd]}")
print(f"DELETE 1000x{REPS}: avg={avg(t_del):.1f}ms runs={[f'{t:.0f}' for t in t_del]}")
print(f"TOTAL avg/rep: {avg(t_ins) + avg(t_sel) + avg(t_upd) + avg(t_del):.1f}ms")
