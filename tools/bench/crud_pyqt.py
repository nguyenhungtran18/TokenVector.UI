"""CRUD mau PyQt6 doi chung Phase 6.4: staff.db + QTableView + QSqlTableModel.

GUI that (chay: python3 tools/bench/crud_pyqt.py) + che do scripted headless:
  QT_QPA_PLATFORM=offscreen python3 tools/bench/crud_pyqt.py --selftest
"""
import os
import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableView, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit, QSpinBox, QToolBar, QMessageBox,
)
from PyQt6.QtGui import QAction
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtCore import Qt

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "build", "staff_pyqt.db")


def open_db(path=DB_PATH):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(path)
    if not db.open():
        raise RuntimeError("cannot open db")
    db.exec("CREATE TABLE IF NOT EXISTS staff"
             "(id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INT, city TEXT)")
    return db


class StaffDialog(QDialog):
    def __init__(self, parent=None, name="", age=30, city=""):
        super().__init__(parent)
        self.name_edit = QLineEdit(name)
        self.age_edit = QSpinBox()
        self.age_edit.setRange(0, 150)
        self.age_edit.setValue(age)
        self.city_edit = QLineEdit(city)
        lay = QFormLayout(self)
        lay.addRow("Name:", self.name_edit)
        lay.addRow("Age:", self.age_edit)
        lay.addRow("City:", self.city_edit)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addRow(btns)

    def values(self):
        return (self.name_edit.text(), self.age_edit.value(), self.city_edit.text())


class StaffWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Staff CRUD (PyQt6)")
        self.resize(520, 340)
        self.model = QSqlTableModel(self)
        self.model.setTable("staff")
        self.model.setSort(1, Qt.SortOrder.AscendingOrder)
        self.model.select()
        self.view = QTableView()
        self.view.setModel(self.model)
        self.setCentralWidget(self.view)
        tb = QToolBar()
        self.addToolBar(tb)
        for label, fn in (("Add", self.add_row), ("Edit", self.edit_row),
                          ("Delete", self.delete_row)):
            a = QAction(label, self)
            a.triggered.connect(fn)
            tb.addAction(a)

    def add_row(self, name="New", age=20, city=""):
        r = self.model.rowCount()
        self.model.insertRow(r)
        self.model.setData(self.model.index(r, 1), name)
        self.model.setData(self.model.index(r, 2), age)
        self.model.setData(self.model.index(r, 3), city)
        self.model.submitAll()

    def edit_row(self, row=None, age=None):
        if row is None:
            row = self.view.currentIndex().row()
        if age is not None:
            self.model.setData(self.model.index(row, 2), age)
            self.model.submitAll()

    def delete_row(self, row=None):
        if row is None:
            row = self.view.currentIndex().row()
        self.model.removeRow(row)
        self.model.submitAll()


def selftest():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    open_db()
    win = StaffWindow()
    win.add_row("An", 30, "HN")
    win.add_row("Binh", 25, "HCM")
    win.add_row("Chi", 35, "DN")
    assert win.model.rowCount() == 3, win.model.rowCount()
    win.edit_row(1, 26)
    win.model.select()
    assert win.model.data(win.model.index(1, 2)) == 26
    win.delete_row(2)
    win.model.select()
    assert win.model.rowCount() == 2, win.model.rowCount()
    assert os.path.getsize(DB_PATH) > 0
    print("CRUD_PYQT_OK rows=2 file_bytes=" + str(os.path.getsize(DB_PATH)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if "--selftest" in sys.argv:
        selftest()
    else:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        open_db()
        w = StaffWindow()
        w.show()
        sys.exit(app.exec())
