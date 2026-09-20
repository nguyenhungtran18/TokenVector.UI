# P1 — SQL Persistence: thiết kế (2026-09-19)

## P1.1 Ràng buộc từ khảo sát compiler

- Chỉ có TEXT I/O đã chứng minh: `WriteAllText(path, str)`,
  `ReadAllText(path) -> str`, `File.Exists` (pattern dùng ở
  A11yBridge/Atspi/Designer/Printing/Platform — copy y nguyên, zero rủi ro).
- KHÔNG có: binary read/write, rename/move, delete, flush/fsync.
- String là UTF-16 (.NET); mọi độ dài tính bằng **chars** (không bytes) để
  tránh lệch encoding.
- Không có `find`/`split` builtin → parser dùng cursor scan char-by-char
  (pattern TTF readers đã chứng minh).

## P1.2 Format TKVSQL1 (text, length-prefixed — không escaping)

Mọi chuỗi lưu dạng `<len-dec>\n<raw len chars>\n`; mọi số dạng dòng decimal.
Không delimiter trong payload nên cell chứa `\n`, space, unicode đều an toàn.

```
TKVSQL1\n
<generation>\n            # int, tăng mỗi save (chọn slot mới nhất)
<ntables>\n
mỗi table:
  TABLE\n
  <namelen>\n<name>\n
  <ncols>\n
  <nrows>\n
  mỗi col: <namelen>\n<name>\n<type>\n<notnull>\n<pk>\n
  mỗi cell (row-major): <len>\n<raw>\n
TKVEND\n
<total_cells>\n           # trailer toàn vẹn: đếm + magic đuôi
```

- Cell lưu nguyên dạng string trong `rows` (round-trip lossless theo định
  nghĩa engine; type déclaré ở COL để hiển thị, không ép kiểu).
- Kích thước ước tính: staff 1000×4 (~10 chars/cell) ≈ 60 KB — `+` concat
  O(n²) chấp nhận được ở quy mô này (ghi chú tối ưu sau: chunk-join).

## P1.3 Atomicity không cần rename: dual-slot + generation

Files: `<path>.a`, `<path>.b` (không dùng marker file riêng — generation
nằm trong header, loader tự chọn):

- **Save:** serialize toàn DB vào chuỗi S; đọc generation của cả 2 slot
  (slot lỗi = -1); ghi S với `generation = max+1` vào slot có generation
  NHỎ hơn (ghi đè slot cũ). Crash giữa chừng → slot đang ghi lỗi parse,
  slot còn lại nguyên vẹn + generation cao nhất trong các slot hợp lệ thắng.
- **Load:** parse cả 2 slot (nếu tồn tại); chọn slot hợp lệ có generation
  lớn nhất; nạp vào caller lists (CLEAR trước, pop-all như `sql_snap_copy`);
  rebuild rowid-index cho các bảng đã declare PK (gọi lại `sql_pk_declare`).
- **Tính chất:** không bao giờ mất dữ liệu committed gần nhất còn nguyên;
  trường hợp xấu nhất mất đúng 1 checkpoint đang ghi dở (tương đương
  crash-giữa-commit của SQLite rollback-journal, không cần WAL replay vì
  snapshot là toàn phần).
- Tương lai (cần compiler mới): `File.Move` → single-file + tmp + move,
  bỏ dual-slot.

## P1.4 API (TkvUI.SQLite.tkv, không đổi signature hàm cũ)

- `sql_save(db, tnames, scol_table, scol_name, scol_type, scol_notnull,
  scol_pk, tstart, tcount, tncol, rows) -> i32`
  (0 ok; 1 closed; 9 io-error; dùng `db.path`, tăng `db.persist_gen`).
- `sql_load(db, ...) -> i32` (0 ok; 1 closed; 2 no-file; 8 corrupt —
  cả 2 slot đều lỗi).
- `SqlDb.persist_gen: "i32"` (scalar mới duy nhất; `make_sql_db` là nơi
  dựng duy nhất — đã kiểm chứng).
- Externs mới trong module (copy pattern Printing/Platform):
  `sql_file_write/read/exists`.
- Helpers nội bộ: `sql_pl_line` (đọc 1 dòng qua out-list tái dùng),
  `sql_pl_wstr` (ghi chuỗi length-prefixed), `sql_pl_rstr` (đọc chuỗi
  length-prefixed), `sql_slot_gen` (đọc generation 2 dòng đầu),
  `sql_slot_parse` (parse full slot, CLEAR caller lists trước, bounds-check
  mọi bước, trả generation/-1). Số parse bằng `mv_parse_int` (có sẵn) —
  KHÔNG parse digit thủ công (tránh `ord()` + elif-chain mà compiler không
  nuốt trôi).

## P1.5 Kiểm thử + bench chấp nhận

- Selftest: save→clear→load→verify counts/sum/spot; corrupt slot A
  (ghi rác) → load vẫn OK từ B; generation tăng đơn điệu; rollback sau
  load vẫn đúng (index rebuild, không stale).
- Bench file-backed mới: save+load bảng staff 1000 rows vs PyQt
  `crud_pyqt_bench.py` file-backed (TOTAL 505 ms) — so "persist 1000 rows
  ra file", báo cáo trung thực dù op không trùng khít.
