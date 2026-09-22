"""Doi chung chuc nang PyQt6 (offscreen) vs TkvUI — chay that, khong claim chay.

Cac muc: widgets render, mainwindow assembly (mirror QtAppPort), dialog
instantiate, Vietnamese/bidi render, SQL CRUD, PDF print, clipboard,
item-view proxy, media setSource. Modal exec + playback that KHONG lam
duoc offscreen -> ghi nhan trung thuc.

Chay: python3 tools/bench/func_pyqt_probe.py
In FUNC_PYQT_OK n/n hoac FAIL chi tiet.
"""
import os
import sys
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import (QApplication, QPushButton, QLabel, QLineEdit,
                             QTextEdit, QComboBox, QCheckBox, QRadioButton,
                             QSlider, QProgressBar, QSpinBox, QTabWidget,
                             QTableWidget, QTreeWidget, QTreeWidgetItem,
                             QCalendarWidget, QSplitter, QMenuBar, QToolBar,
                             QStatusBar, QDockWidget, QDialogButtonBox,
                             QMainWindow, QMessageBox, QFileDialog,
                             QColorDialog, QFontDialog, QInputDialog,
                             QProgressDialog, QTableView)
from PyQt6.QtGui import QImage, QPainter, QFont, QColor, QPdfWriter, QAction, QTextCursor
from PyQt6.QtCore import Qt, QBuffer, QIODevice
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from PyQt6.QtWidgets import QAbstractItemView

PASS, FAIL = [], []


def check(name, fn):
    try:
        fn()
        PASS.append(name)
        print("  PASS " + name)
    except Exception as e:
        FAIL.append(name)
        print("  FAIL %s (%s: %s)" % (name, type(e).__name__, str(e)[:100]))


def nonblank(img):
    assert img.width() > 0 and img.height() > 0
    gray = img.convertToFormat(QImage.Format.Format_Grayscale8)
    n = img.width() * img.height()
    ptr = gray.constBits()
    ptr.setsize(n)
    data = bytes(ptr)
    assert any(c != 255 for c in data), "blank"


def shot(w):
    img = QImage(w.width(), w.height(), QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.white)
    w.render(img)
    return img


app = QApplication([])

# 1. widgets render
def _widgets():
    ws = [QPushButton("OK"), QLabel("Hi"), QLineEdit("ab"), QTextEdit("tx"),
          QComboBox(), QCheckBox("c"), QRadioButton("r"),
          QSlider(Qt.Orientation.Horizontal), QProgressBar(), QSpinBox(),
          QTabWidget(), QTableWidget(3, 3), QTreeWidget(), QCalendarWidget(),
          QSplitter(), QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)]
    cb = ws[4]
    cb.addItems(["a", "b"])
    tw = ws[11]
    tw.setItem(0, 0, __import__("PyQt6.QtWidgets", fromlist=["QTableWidgetItem"]).QTableWidgetItem("x"))
    tr = ws[12]
    tr.setHeaderLabels(["h"])
    tr.addTopLevelItem(QTreeWidgetItem(["i"]))
    tb = QTabWidget()
    tb.addTab(QLabel("p1"), "T1")
    tb.addTab(QLabel("p2"), "T2")
    ws.append(tb)
    for i, w_ in enumerate(ws):
        w_.resize(200, 100)
        nonblank(shot(w_))
    assert len(ws) == 17


check("widgets.render17", _widgets)


# 2. mainwindow assembly (mirror QtAppPort)
def _mainwin():
    mw = QMainWindow()
    mw.resize(640, 480)
    te = QTextEdit()
    mw.setCentralWidget(te)
    mb = mw.menuBar()
    f = mb.addMenu("File")
    e = mb.addMenu("Edit")
    h = mb.addMenu("Help")
    acts = {}
    for txt, sc in [("New", "Ctrl+N"), ("Open", "Ctrl+O"), ("Save", "Ctrl+S"),
                    ("Print", "Ctrl+P"), ("Exit", "Ctrl+Q"), ("Cut", "Ctrl+X"),
                    ("Copy", "Ctrl+C"), ("Paste", "Ctrl+V")]:
        a = QAction(txt, mw)
        a.setShortcut(sc)
        acts[txt] = a
    f.addActions([acts["New"], acts["Open"], acts["Save"], acts["Print"], acts["Exit"]])
    e.addActions([acts["Cut"], acts["Copy"], acts["Paste"]])
    h.addAction("About")
    tb1 = mw.addToolBar("File")
    tb1.addActions([acts["New"], acts["Open"], acts["Save"]])
    tb2 = mw.addToolBar("Edit")
    tb2.addActions([acts["Cut"], acts["Copy"], acts["Paste"]])
    sb = mw.statusBar()
    sb.showMessage("Ready")
    dock = QDockWidget("Dock", mw)
    dock.setWidget(QLabel("dock"))
    mw.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
    te.setPlainText("Hello\nWorld")
    assert te.toPlainText() == "Hello\nWorld"
    te.selectAll()
    te.copy()
    te.moveCursor(QTextCursor.MoveOperation.End)
    te.paste()
    assert te.toPlainText() == "Hello\nWorldHello\nWorld"
    te.selectAll()
    te.cut()
    assert te.toPlainText() == ""
    te.paste()
    assert te.toPlainText() == "Hello\nWorldHello\nWorld"
    sb.showMessage("Saved x")
    assert sb.currentMessage() == "Saved x"
    assert len(mb.actions()) == 3
    nonblank(shot(mw))


check("mainwin.app", _mainwin)


# 3. dialogs instantiate (khong exec modal offscreen)
def _dialogs():
    m = QMessageBox()
    m.setText("save?")
    m.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    assert m.standardButtons() != 0
    fd = QFileDialog()
    fd.setNameFilter("Text files (*.txt)")
    assert "txt" in fd.nameFilters()[0]
    cd = QColorDialog()
    cd.setCurrentColor(QColor(10, 20, 30))
    assert cd.currentColor().red() == 10
    QFontDialog()
    QInputDialog()
    QProgressDialog("w", "c", 0, 10)
    assert True


check("dialogs.instantiate6", _dialogs)


# 4. Vietnamese + bidi render
def _text():
    img = QImage(400, 120, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.white)
    p = QPainter(img)
    p.setFont(QFont("Arial", 14))
    p.drawText(10, 30, "Tiếng Việt: Xin chào 123")
    p.drawText(10, 60, "مرحبا بالعالم")
    p.drawText(10, 90, "สวัสดีชาวโลก")
    p.end()
    nonblank(img)
    assert img.width() == 400


check("text.vi-bidi", _text)


# 5. SQL CRUD (memory + file)
def _sql():
    for name, dbfile in (("m", ":memory:"), ("f", "build/func_pyqt.db")):
        if dbfile != ":memory:" and os.path.exists(dbfile):
            os.remove(dbfile)
        db = QSqlDatabase.addDatabase("QSQLITE", name)
        db.setDatabaseName(dbfile)
        assert db.open()
        q = QSqlQuery(db)
        assert q.exec("CREATE TABLE t(id INTEGER PRIMARY KEY, v TEXT)")
        db.transaction()
        q.prepare("INSERT INTO t(id,v) VALUES (?,?)")
        for i in range(100):
            q.addBindValue(i)
            q.addBindValue("v%d" % i)
            assert q.exec()
        db.commit()
        assert q.exec("SELECT COUNT(*) FROM t")
        q.next()
        assert q.value(0) == 100
        assert q.exec("UPDATE t SET v='x' WHERE id=5")
        assert q.exec("DELETE FROM t WHERE id=6")
        assert q.exec("SELECT COUNT(*) FROM t")
        q.next()
        assert q.value(0) == 99
        db.close()
    assert os.path.getsize("build/func_pyqt.db") > 0


check("sql.crud", _sql)


# 6. PDF print
def _pdf():
    fn = "build/func_pyqt.pdf"
    if os.path.exists(fn):
        os.remove(fn)
    w = QPdfWriter(fn)
    w.setPageSize(w.pageLayout().pageSize())
    p = QPainter(w)
    p.setFont(QFont("Arial", 12))
    p.drawText(100, 100, "Hello PDF")
    p.drawLine(100, 120, 300, 120)
    p.end()
    assert os.path.getsize(fn) > 1000


check("print.pdf", _pdf)


# 7. clipboard
def _clip():
    cb = app.clipboard()
    cb.setText("abc123")
    assert cb.text() == "abc123"


check("clipboard.roundtrip", _clip)


# 8. item-view proxy
def _proxy():
    from PyQt6.QtCore import QStringListModel, QSortFilterProxyModel
    m = QStringListModel(["b", "a", "c"])
    px = QSortFilterProxyModel()
    px.setSourceModel(m)
    px.sort(0)
    assert px.data(px.index(0, 0)) == "a"
    px.setFilterFixedString("b")
    assert px.rowCount() == 1
    tv = QTableView()
    tv.setModel(px)
    tv.resize(200, 100)
    nonblank(shot(tv))


check("itemview.proxy", _proxy)


# 9. media setSource (khong playback offscreen)
def _media():
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PyQt6.QtCore import QUrl
    pl = QMediaPlayer()
    ao = QAudioOutput()
    pl.setAudioOutput(ao)
    pl.setSource(QUrl.fromLocalFile(os.path.abspath("build/ingest/sample.mp4")))
    assert pl.source().isValid()
    assert pl.mediaStatus() is not None


check("media.setsource", _media)


print("pyqt: %d/%d" % (len(PASS), len(PASS) + len(FAIL)))
if FAIL:
    print("FUNC_PYQT_FAIL " + ",".join(FAIL))
    sys.exit(1)
print("FUNC_PYQT_OK")
