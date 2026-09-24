# Hướng dẫn tích hợp TkvUI

Cách một ứng dụng TokenVector (`.tkv`) nhập và dùng TkvUI v1.0.1.

## 1. Cách lấy thư viện

**Cách A — artifact release (khuyến nghị):** dùng file `dist/TokenVector.UI-<version>.tkvpkg`
(tạo bằng `bash tools/package.sh`; kèm `.sha256` để kiểm tra). Giải nén vào một thư mục
trong project của bạn, giữ nguyên cấu trúc:

```
myapp/
├── TokenVector.UI/          <- giai nen .tkvpkg (thu muc goc cung ten package)
│   ├── TokenVector.UI.tkv   <- umbrella: file duy nhat ban can import
│   ├── TkvUI.Core.tkv ...   <- 49 module (xem `tkvui.pkg.json`)
│   ├── tkvui.pkg.json       <- manifest (version, modules, verify)
│   ├── docs/ examples/ tools/
└── myapp.tkv                <- ung dung cua ban
```

**Cách B — tham chiếu trực tiếp:** nếu cùng máy, chỉ cần trỏ import tới thư mục TkvUI
(import của tkvc resolve theo **thư mục file nguồn**, xem `docs/TkvUI.Roadmap.md §0`).

## 2. Import trong file `.tkv`

Chỉ cần import umbrella — nó kéo theo toàn bộ suite theo DAG, không có vòng:

```python
# -*- coding: utf-8 -*-
"""myapp - ung dung vi du"""
__tkv_import__ = ["TokenVector.UI"]          # neu dat ben trong thu muc TokenVector.UI/
# __tkv_import__ = ["../TokenVector.UI"]     # neu myapp.tkv nam thu muc cha (nhu examples/)

def main() -> "str":
    # 1) Platform + cua so
    pid = detect_platform()
    print("platform=" + str(pid) + " (" + detect_platform_id() + ")")
    plat = Win32Platform(0)                  # pid == 1 tren Windows
    wh = plat.create(100, 100, 480, 360, 0)

    # 2) Surface (buffer nam NGOAI record - rang buoc compiler, xem §0 roadmap)
    buf = []
    n = surf_w * surf_h
    i = 0
    while i < n:
        buf.append(0)
        i = i + 1
    surf = PixelSurface(480, 360, 480)

    # 3) Render 1 frame: theme + widget + layout
    th = theme_dark()
    surface_clear(buf, surf, th.surface)
    card = make_card_notch(0.0, 0.0, 480.0, 120.0, "myapp")
    card.render(buf, surf)

    # 4) Present (Win32 ULW; present_diff tra 0 khi frame khong doi)
    drawn = plat.present(buf, surf, wh)
    plat.close_window(wh)
    return "MYAPP_OK"
```

Build + chạy:

```bash
tkvc.exe build myapp.tkv --entry main --out myapp.exe && myapp.exe
```

Xem ví dụ hoàn chỉnh (cửa sổ thật, vòng 60fps, input thật) trong `examples/`:
`TkvUI.Demo.tkv`, `TkvUI.Live.tkv`, `TkvUI.DemoMobile.tkv`.

## 3. Widget + Input + Layout thường dùng

```python
# widget: moi widget co factory make_* (goi dung so field theo thu tu khai bao)
btn  = make_button(20.0, 140.0, 120.0, 44.0, "OK")
ring = make_metric_ring(160.0, 140.0, 96.0, 96.0, "CPU", 100, 220, 140)

# layout: flex co wrap + cross-align; out-list song song ox,oy,ow,oh do caller cap phat
st = flex_style(0, 10.0, 8.0, 0, 0)          # dir=ROW, gap 10, pad 8, align START, justify START
ox = []; oy = []; ow = []; oh = []
layout_alloc_f64(ox, oy, ow, oh, 4)
layout_flex_row(st, 480.0, 360.0, [120.0,96.0,140.0,80.0], [44.0,96.0,44.0,44.0], 4, ox, oy, ow, oh)

# input: hit_test_tree topmost-first + EventDispatcher co pointer capture
ids = []; xs = []; ys = []; ws = []; hs = []; fl = []
# ... nap geometry widget tu ox/oy/ow/oh ...
disp = make_dispatcher()
# disp.dispatch_move(disp, px, py)  -> hover/leave/enter; dispatch_down/up -> click
```

## 4. Verify sau khi tích hợp

```bash
# trong thu muc giai nen
bash tools/verify.sh                 # -> TKVUI_VERIFY_OK
bash tools/package.sh --verify       # goi lai: build suite tu ban giai nen
```

Hoặc chỉ chạy 1 selftest cần thiết (headless, không mở cửa sổ):

```bash
tkvc.exe build TkvUI.Widgets.tkv --entry widget_selftest --out widgets_test.exe && widgets_test.exe
```

## 5. Lưu ý bắt buộc (tóm tắt §0 roadmap)

- `__tkv_import__` resolve theo **thư mục file nguồn** — đặt path tương ứng vị trí `myapp.tkv`.
- Buffer pixel là `list[i64]` (ARGB) nằm **ngoài** `PixelSurface`; caller giữ buffer qua các frame
  (`surface_ensure_capacity` để tái sử dụng, zero-alloc sau warmup).
- Cấm trộn int-computed × f64-computed; `float()` trên literal từ list trả 0.0 im lặng —
  khởi tạo counter bằng `int(0)` trước.
- Cấm tên hàm/class trùng giữa các module (merge import sẽ đụng nhau) và cấm method tên `update`.
- Tên label giữ ASCII (ilasm đọc `ldstr` theo ANSI).
- Đọc **đầy đủ** `docs/TkvUI.Roadmap.md §0` trước khi viết `.tkv` mới.

## 6. Nền tảng & hạn chế

- Windows: đầy đủ (Win32 ULW thật).
- X11/Wayland/Cocoa: stub/vehicle — xem bảng `platforms` trong `tkvui.pkg.json`.
- Android/iOS: cần host shim cấp JNI env + native buffer; `create()` tự gate theo
  `detect_platform()` và trả handle 0 trên nền tảng khác (demo trả `*_SKIPPED`, không crash).
