"""Benchmark PyQt6 doi chung file-backed: 1000 rows memory->file->memory.

Cung workload voi TkvUI bench_persist (staff 1000 rows, save+load snapshot):
WRITE = executemany INSERT 1000 rows + commit (1 transaction), close;
READ = reopen + SELECT * fetchall. Do rieng 2 pha, x5 reps nhu ben TKV.

Chay: QT_QPA_PLATFORM=offscreen python3 tools/bench/crud_pyqt_filebench.py
"""
import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtSql import QSqlDatabase, QSqlQuery

DB = "build/staff_pyqt_filebench.db"

app = QApplication([])

rows = [(i + 1, f"Name{i}", 20 + (i % 50), f"City{i % 20}") for i in range(1000)]

w_ms, r_ms = [], []
for rep in range(5):
    if os.path.exists(DB):
        os.remove(DB)
    db = QSqlDatabase.addDatabase("QSQLITE", f"c{rep}")
    db.setDatabaseName(DB)
    assert db.open()
    q = QSqlQuery(db)
    assert q.exec("CREATE TABLE staff(id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INT, city TEXT)")
    t0 = time.perf_counter()
    db.transaction()
    q.prepare("INSERT INTO staff(id,name,age,city) VALUES (?,?,?,?)")
    for r in rows:
        q.addBindValue(r[0])
        q.addBindValue(r[1])
        q.addBindValue(r[2])
        q.addBindValue(r[3])
        assert q.exec()
    db.commit()
    db.close()
    w_ms.append((time.perf_counter() - t0) * 1000.0)

    t0 = time.perf_counter()
    db2 = QSqlDatabase.addDatabase("QSQLITE", f"r{rep}")
    db2.setDatabaseName(DB)
    assert db2.open()
    q2 = QSqlQuery(db2)
    assert q2.exec("SELECT id,name,age,city FROM staff")
    back = []
    while q2.next():
        back.append((q2.value(0), q2.value(1), q2.value(2), q2.value(3)))
    db2.close()
    r_ms.append((time.perf_counter() - t0) * 1000.0)
    assert len(back) == 1000, len(back)

w_ms.sort()
r_ms.sort()
print(f"WRITE 1000 x5 (median): {w_ms[2]:.0f}ms {sorted([round(x) for x in w_ms])}")
print(f"READ 1000 x5 (median): {r_ms[2]:.0f}ms {sorted([round(x) for x in r_ms])}")
print(f"TOTAL round-trip median: {w_ms[2] + r_ms[2]:.0f}ms")
print(f"file_bytes={os.path.getsize(DB)}")
