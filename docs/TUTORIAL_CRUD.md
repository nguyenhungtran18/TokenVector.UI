# Tutorial: CRUD app với TokenVector.UI (15 phút)

> Mẫu chạy được: `examples/TkvUI.CrudDemo.tkv` (`crud_run` → `CRUD_TKVUI_OK`).
> Stack: `TkvUI.SQLite` (in-memory) + `TkvUI.Data` (model/proxy) +
> `TkvUI.Widgets.Native` (render). Giới hạn (trung thực): **chưa có
> persistence file** (SQLite module in-memory) và **chưa có vòng lặp GUI
> tương tác** — bản PyQt đối chứng (`tools/bench/crud_pyqt.py`, SQLite file
> + QDialog thật) xem `docs/BENCH.md` §6.4.

## 1. Mở DB + tạo bảng (2 phút)

```python
db = make_sql_db()
sql_open(db, ":memory:")
tn = []; ct = []; cn = []; cy = []; nn = []; pk = []
ts = []; tc = []; tnc = []; rows = []
sql_create_table(db, tn, ct, cn, cy, nn, pk, ts, tc, tnc,
                 "staff", crud_cols(), crud_types())   # helper append, xem CrudDemo
```

Quy ước compiler (bắt buộc): dữ liệu caller giữ trong list, record không
chứa list; dựng list bằng helper `append` (không literal `[..]` inline khi
truyền vào hàm đã suy kiểu); helper định nghĩa TRƯỚC hàm dùng.

## 2. Thêm/sửa/xóa (5 phút)

```python
sql_insert(db, tn, ct, cn, nn, ts, tc, tnc, rows, "staff",
           crud_row("1", "An", "30", "HN"))               # helper, xem CrudDemo
aff = sql_update_rows(db, tn, ct, cn, ts, tc, tnc, rows, "staff",
                      "age", "26", "name", 0, "Binh")   # op 0 ==, 4 = contains
rem = sql_delete_rows(db, tn, ct, cn, ts, tc, tnc, rows, "staff",
                      "name", 0, "Chi")
```

## 3. Sort/filter + render bảng (5 phút)

```python
m = make_sql_tablemodel()
m.bind(sql_table_idx(tn, "staff"))
m.set_sort(2, 2)                                        # cot age, desc
order = []; vis = []
sql_model_refresh(m, ts, tc, tnc, rows, order, vis)     # nap mapping
st = make_mv_table(0.0, 0.0, 340.0, 120.0)
flat = []
sql_model_project(ts, tc, tnc, rows, sql_table_idx(tn, "staff"), flat)
st.render(buf, surf, 0, headers, flat, widths, 4, order, vis)
```

> **Bài học xương máu (Phase 6.4): sau mọi mutation (insert/update/delete)
> PHẢI `sql_model_refresh` lại.** Mapping `order`/`visible` cũ vẫn render
> (guard chống crash) nhưng sai hàng. Demo từng dính bug này và guard đã cứu
> khỏi crash — đừng ỷ lại vào guard.

## 4. Dialog + export (3 phút)

```python
d = make_native_dialog_buttons(x, y, w, h, "Edit", "Save?", 0, 2)
d.show()
d.hide(d.hit_button(px, py))    # 0 = OK/Default, 1 = Cancel
if d.result == 0:
    ...thuc hien update...
```

Export JSON: tự nối chuỗi từ `sql_row_get` (xem `crud_export_json`).

## Checklist trước khi gọi là "xong"

- [ ] Mọi list via helper, không literal inline.
- [ ] Refresh model sau mutation.
- [ ] Hit-test dùng `hit_button`/`cell_hit`, không tự tính toán tọa độ.
- [ ] Chạy `crud_run` tương đương cho app của bạn, expect `*_OK`.
