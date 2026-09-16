# TkvUI Roadmap v2 + v3

> Thư viện UI hiện đại, đa nền tảng, dùng chung cho nhiều phần mềm.
> 100% TokenVector (.tkv). Zero Dependency (không Skia/SDL/WPF).
> Trạng thái: v2 P1–P7 **DONE** (đã build + chạy nghiệm thu headless bằng `tkvc.exe`, lint 0 findings) + **P7.5 Live harness DONE** (`examples/TkvUI.Live.tkv`, 27/27 PASS `TKVUI_LIVE_OK` — vong 60fps that: Win32 ULW + Input + Layout + Spring + present_diff) + **P7.6 Input poll thật DONE** (`run_live`: pump `PeekMessage` + `GetMessagePos` + `GetAsyncKeyState`, 62 render + 538 idle/600 vòng, `TKVUI_LIVE_RUN_OK`). P8/P9 (mobile) có khung + example nhưng **chưa verify trên thiết bị thật**; v3 chưa code.
> **v2.1.0 (P1.1 hardening) DONE** — selftest cho 4 module còn thiếu (Core/Graphics/Text/Effects), `detect_platform()` probe runtime thật, iOS/Android gate theo platform (không còn crash `DllNotFoundException`), sửa lỗi `IOSPlatform.present` ghi đè vùng nhớ CGContext, umbrella có `main()` chạy cả suite, thêm `tools/verify.sh` + README/LICENSE/CHANGELOG. Chi tiết §8.
> Toolchain dùng để verify: `D:\TokenVector\3.code\dist\tkvc.exe` (thư viện resolve import theo thư mục FILE NGUỒN — xem §0 ràng buộc *P5–P7*). One-shot: `bash tools/verify.sh` (12 PASS / 0 FAIL / 2 SKIPPED, `TKVUI_VERIFY_OK`).

## 0. Baseline đã có (v1)

| File | Task | Nội dung chính |
|---|---|---|
| `TkvUI.Core.tkv` | 1 | `ColorRgba`, `Point2D`, `Rect2D`, `Matrix3x2`, `PixelSurface` (buffer `list[i64]` ARGB ngoài record), `surface_clear`, `surface_blend_pixel` (SrcOver, `//`/`%`, không bitwise), `surface_fast_blit` |
| `TkvUI.Graphics.tkv` | 2 | `draw_line` (Bresenham + brush), `fill_round_rect`, `stroke_round_rect`, `draw_arc` (Taylor — SAI, chờ P1 fix) |
| `TkvUI.Text.tkv` | 3 | `TextMetrics`, `glyph_pattern` 5x7, `measure_string`, `draw_string` |
| `TkvUI.Effects.tkv` | 4 | `apply_box_blur` 2-pass, `draw_specular_highlight`, `draw_drop_shadow` |
| `TkvUI.Platform.tkv` | 5 | `PlatformWindowHandle`, `Win32Platform` / `X11Platform` / `CocoaPlatform` (stub) |
| `TkvUI.Events.tkv` | 6 | `PointerEventArgs`, `HitTestResult`, `pointer_button_label`, `no_hit` (P5: router đã chuyển sang `TkvUI.Input.tkv`) |
| `TkvUI.Widgets.tkv` | 7 | (P7) UIElement, 15 widget, SpringAnimation + Tween, InvalidationManager, FrameScheduler, RenderLoop, `widget_selftest` |
| `TkvUI.Input.tkv` | P5 | `hit_test_tree` (topmost-first + flags), `EventDispatcher` (pointer capture), `TouchEventArgs`, `GestureEvent`, `GestureRecognizer`, `input_selftest` |
| `TkvUI.Layout.tkv` | P6 | `FlexStyle`/`GridStyle`/`Constraint`, `layout_flex_row/col` (wrap), `layout_stack_row/col`, `layout_grid(+-span)`, DPI, validator + `layout_selftest` |
| `examples/TkvUI.Demo.tkv` | P7 | Notch pill 720x220 + MetricRing lerp `Spring` + panel Flex + present cửa sổ Win32 ULW |
| `examples/TkvUI.DemoMobile.tkv` | P7 | Phone 390x844 + pad 1024x768 (`SplitView`, ListView 10k/20k dòng) + touch pinch/pan/tap |
| `TokenVector.UI.tkv` | umbrella | Gộp 9 module + `tkvui_version()` + `tkvui_selftest()` + `main()` (entry mặc định, chạy cả suite). Không khai `__tkv_extern_assembly__` (P1.1: bản cũ ghi nhầm là có `System.Drawing`) |

Ràng buộc compiler (bắt buộc tuân thủ mọi phase):
- `il_core.tkv`: tokenizer KHÔNG có `& | >> <<` → dùng `//`, `%`.
- Không kiểu `bool` → dùng `i32` 0/1.
- Record chứa `list` gây `OverflowException` → buffer truyền ngoài record.
- `syntax_baseline.tkv`: cấm `self.a.b` (nested attribute) → field phẳng (`bx,by,bw,bh`), hoist `p = self.params`.
- `__tkv_import__` gộp file, CẤM trùng tên hàm/class → mỗi module chỉ giữ code riêng, phụ thuộc qua import.
- Mỗi file phải có ≥ 1 hàm top-level có annotation (kể cả file chỉ chứa class, umbrella) — nếu không `extract_program_file` báo `File khong co ham top-level` (P1: `detect_platform`, `pointer_button_label`, `tkvui_version`).
- Field record chỉ được dùng kiểu record khai báo CÙNG file; tham số/return được dùng kiểu record import (resolve sau merge) (P1: `MetricRingWidget.color` → phẳng hóa `cr,cg,cb,ca`).
- Ctor record đòi đủ mọi field (kể cả field state như `is_rest`) — truyền tường minh (P1: `SpringAnimation(..., 0)`, `EventDispatcher(0.0, 0.0, -1, -1)`).
- CẤM tên method `update` — macro text-level `dict.update` (`dict_type.tkv`) viết lại `<ident>.update(<ident>)` thành vòng lặp dict (P1: đổi thành `step`).
- Trong `int(...)` chỉ dùng literal nguyên (`int(x * 255)`, không `int(x * 255.0)`) — nếu không sinh `ldc.i4 255.0`, ilasm fail.
- Ép f64 tường minh bằng `float(...)` khi số hạng đầu là i32 (`float(c.r) / 255.0`) — nếu không literal float bị ép `ldc.i4`.
- CẤM arithmetic trộn int-computed × f64-computed ( vd `dr * t`, `len(text) * 6 * scale`) — SILENT garbage (`color_lerp` từng trả 255 thay vì 128); luôn viết `float(dr) * t`, `float(len(text) * 6) * scale`. Riêng int-literal × f64 (`7 * scale`, `x + 0.5`, `80 * intensity`) an toàn — literal tự thích nghi.
- Mỗi local chỉ mang 1 kiểu trên mọi nhánh — dùng tên biến riêng cho từng kiểu (P1: `gr` vs `g` trong `color_from_hsla`).
- Arg `list` truyền vào method phải khớp CHÍNH XÁC kiểu phần tử đã suy luận; `list[int]` (không phải `list[i32]`) cho list cờ 0/1, buffer pixel `list[i64]` (P1: `tick(..., springs: "list[int]")`, `present` + `surface_ensure_capacity` để unify).
- Gọi hàm thường (không phải method) để unify kiểu list về `list[i64]` trước khi truyền vào method (P1: `surface_ensure_capacity(pbuf, 16)` trước `present`).
- CẤM arithmetic trộn TkvInt × i32 (vd `(end - pos) * char_w` khi `end/pos` là TkvInt) — corrupt memory (AccessViolation); khởi tạo counter bằng `int(0)` để ép int32 ngay từ đầu rồi tính toán thuần int32 (P2: `measure_block`). TkvInt thuần (cộng/so sánh/gán) an toàn.
- Default args (`= 0`, `= 0.0`) tương thích gọi thiếu positional từ module khác (P2: `draw_string` 6-arg cũ vẫn build sau khi thêm `align/box_w/tracking`).
- Hằng module (`WS_EX_LAYERED = 524288`) VÔ HÌNH trong method record (`KeyError` ở declare) — dùng literal số trực tiếp trong method, giữ const để làm tài liệu (P3).
- Builtin extern (pinvoke/extern_method) có return KHÔNG được gọi dạng lệnh độc lập — phải gán (`rc = win_...(...)`), kể cả trong vòng lặp (P3).
- Trộn i64 + i32-BIẾN (`mem + off`) corrupt âm thầm — literal thì tự thích nghi (`mem + 4` OK); param kiểu `i64` nhận literal OK. Ép mọi offset/địa chỉ về i64 (P3: `win_write_u32_le(mem: i64, off: i64, ...)`).
- `SetLayeredWindowAttributes` và `UpdateLayeredWindow` KHÔNG được dùng chung trên một cửa sổ (ULW trả 87 sau SLA) — P3 dùng ULW độc quyền; uniform-alpha qua blend `{0,0,A,0}` + flags `ULW_COLORKEY|ULW_ALPHA` (= 3) vẫn giữ colorkey (P3: cả 3 combo verified err=0).
- ULW cần struct THẬT (POINT/SIZE/BLENDFUNCTION) — NULL cho 87; viết struct qua `VirtualAlloc` + `wsprintfA %c` (đã verify byte-exact bằng `lstrlen`/`lstrcmpA`); `CreateDIBSection` + `SetPixelV` cho DIB 32bpp top-down (P3: `GetObject(...,128)` = 104 = `sizeof(DIBSECTION)` x64 đã align).
- Contract `present_diff`: caller giữ buffer `shown`, copy `frame→shown` (`surface_fast_blit`) sau mỗi present; frame không đổi → trả 0, không gọi ULW (P3: `DIFF_SAME:0`).
- Lint fail = build fail (trừ `--no-lint`, không khuyến nghị).
- `__tkv_extern_assembly__`: string hoặc list string. `__tkv_extern_method__`: list dict `{name, assembly, class, method, params, returns}`; `mscorlib`/`System`/`System.Core` có sẵn không cần khai báo.
- (P5–P7) Ctor record = **Positional Constructor đúng SỐ FIELD theo thứ tự khai báo** — thân `__init__` KHÔNG quyết định arity (khớp `TOKENVECTOR_EXPERIENCE.md` §2). Gọi thiếu → `SyntaxError: record 'X' can N tham so (...), gap M`; gọi thừa chỉ lộ lúc CHẠY → luôn có hàm `make_*`/factory cho call-site (P5: `EventDispatcher` 12 field; P7: `make_button`, `make_card_notch`, `spring_new`…).
- (P5–P7) `float(<TkvInt>)` = **0.0 IM LẶNG** khi giá trị đến từ literal hoặc phần tử `list[...]` (không sinh `conv.r8`) — counter/int phải khởi tạo bằng `int(0)` rồi mới `float()` (P2 `measure_block` + probe P5: `cnt_list=-1.0` đúng, `avg_from_literal=0.0` sai). `int(phần tử list[i32])` AN TOÀN (probe `int(7)`, `int(-9)`, `int(1000003)`).
- (P5–P7) KHÔNG đọc field trên **kết quả gọi hàm** (`h = hit_test_tree(...)` rồi `h.target_id` ✓; `hit_test_tree(...).target_id` → `SyntaxError: '.target_id' sau 1 bieu thuc phuc tap`).
- (P5–P7) Hằng module OK làm đối số gọi hàm / trong `return` / số học với param (`return x + AA`), nhưng **`KeyError` khi đứng ở RHS phép gán local** (`n = DW * DH` → `KeyError: 'DW'`) — trong thân hàm dùng literal số (P7: `examples/TkvUI.Demo.tkv`).
- (P5–P7) Ternary DSL (`cond ? a : b`) làm `syntax_baseline` chết ở `ast.parse` (`SyntaxError: invalid syntax`) → dùng file entry là build fail; viết `if/else`.
- (P5–P7) Import resolve theo **THƯ MỤC FILE NGUỒN** (không phải CWD như `TOKENVECTOR_EXPERIENCE.md` §5 mô tả — đã kiểm chứng trên `tkvc.exe` 3.code/dist: cùng CWD, file ở gốc build được còn file trong `build/` thì không) → nhờ vậy `examples/TkvUI.Demo.tkv` import `"../TokenVector.UI"` chạy đúng.
- (P5–P7) Nhiều file cùng khai `__tkv_extern_method__` thì MERGE bình thường (`tkv_sqrt` ở Input + `tkv_sin/tkv_cos` ở Graphics cùng build OK).
- (P5–P7) Entry tự động của CLI chỉ nhận tham số/return VÔ HƯỚNG → file thư viện có entry record/list KHÔNG build standalone (`CLI tu dong hien CHI ho tro ... VO HUONG`); verify module qua chuỗi import (`examples/`) hoặc chọn entry vô hướng (`hex_char_to_val`, `text_line_count`, `pointer_button_label`).
- (P5–P7) `__tkv_extern_class__` KHÔNG nằm trong whitelist pragma của linter (`__tkv_import__`, `__tkv_extern_assembly__`, `__tkv_extern_method__`, `__tkv_extern_pinvoke__`) → `TkvUI.Platform.tkv` build standalone sẽ lint-fail (`dict literal with content`) dù hợp lệ khi import. **Upstream: thêm `__tkv_extern_class__` vào whitelist.**
- (P5–P7) Text trong IL: ilasm đọc `ldstr` theo ANSI → giữ nhãn ASCII trong thư viện/demo (`TOKENVECTOR_EXPERIENCE.md` §14); zero-console GUI cần `.subsystem 0x0002` chỉ chèn được qua plugin `extra_classes` (chưa có đường .tkv thuần) → demo Win32 hiện mở kèm console (§13).

## 1. Kiến trúc 8 tầng (v2)

```
Foundation (Core+Math+ThemeToken)
  → Graphics (Rasterizer+Clip+AA)
    → Text (Atlas+Shaper)
      → Effects (Blur/Shadow/Backdrop)
        → Platform PAL (Win32/X11/Wayland/Cocoa/Android/iOS)
          → Input (Pointer+Touch+Gesture)
            → Layout (Flex/Grid/Stack/Constraint, DPI)
              → Widgets (Catalog 15) + Rendering (DirtyRect, VSync, Multi-Window)
```

Đồ thị import (DAG, không vòng):

```
Core ← Graphics ← Effects ─┐
Core ← Text ───────────────┤
Core ← Platform             ├→ Widgets → Umbrella
Core ← Events (→ Input v2) ─┘
Layout (mới, P6) ← Core; Widgets ← Layout
```

## 2. Module chi tiết

### 2.1 TkvUI.Core v2 (P1)
- Giữ: `ColorRgba`, `color_from_rgb/hex/lерp`, `Point2D`, `Rect2D`, `Matrix3x2`, `PixelSurface`, `surface_*`.
- Thêm: `ColorHsla` + `color_from_hsla`/`color_to_hsla`, `ThemeToken` + `theme_default()`/`theme_dark()`, `Insets`, `CornerRadius`, DPI helpers (`dp_to_px`, `px_to_dp`, `dpi_scale_for_platform`), `surface_ensure_capacity` (SurfacePool-lite: caller giữ 1 scratch list qua các frame → zero alloc sau warmup) + `SurfacePoolStats`.

### 2.2 TkvUI.Graphics v2 (P1)
- Fix `draw_arc`: `__tkv_extern_method__` `tkv_sin`/`tkv_cos` → `System.Math.Sin/Cos` (`mscorlib`, `f64→f64`), chuẩn hóa góc về 0–360, sai số < 1px.
- Thêm: `draw_path` (polyline + `closed`), `clip_rect_intersect`, `draw_image` (blit có alpha + scale nearest).

### 2.3 TkvUI.Text v2 (P2)
- Atlas 95 glyph + `TextShaper` (word-wrap, ellipsis, `Left/Center/Right`), `lineHeight`, `letterSpacing`.
- Sửa `draw_string`: bỏ toán tử `<<` (dòng `bit = (mask // (1 << ...))`), tra bit bằng bảng trừ.

### 2.4 TkvUI.Effects v2 (P2)
- `apply_box_blur` 2-pass → Dual Kawase 3-pass O(N) độc lập radius + `backdrop_blur` cho glass.

### 2.5 TkvUI.Platform v2 (P3–P4)
- Interface: `Create(x,y,w,h,topmost,title,alpha)`, `PollEvents`, `SetWindowPos`, `SetAlpha`, `Close`; `Present(buf,surf,handle)`.
- Win32 (P3): `CreateWindowExW` `WS_EX_LAYERED|WS_EX_TOOLWINDOW`, `CreateDIBSection` + `UpdateLayeredWindow` + `BLENDFUNCTION`.
- Linux (P4): `X11Platform` ARGB Visual + `_NET_WM_WINDOW_TYPE_DOCK`; thêm `WaylandPlatform` (`libwayland-client.so`).
- macOS (P4): `CocoaPlatform` `NSPanel` + `CGDataProvider`/`CALayer`.
- `DetectPlatform() -> i32` (1 Win, 2 X11, 3 Wayland, 4 Cocoa, 5 Android, 6 iOS).

### 2.6 TkvUI.Input v2 (P5, tách từ Events) — DONE
- `TkvUI.Events.tkv` nay chỉ giữ DATA TYPE (`PointerEventArgs`, `HitTestResult`, `pointer_button_label`, `no_hit`); router sang `TkvUI.Input.tkv` vì merge CẤM trùng tên class.
- `hit_test_tree(x,y,ids,xs,ys,ws,hs,flags,n)`: duyệt TOPMOST-first (phần tử cuối = trên cùng), `flags != 0` = bỏ qua widget ẩn/disabled; thêm `hit_test_rect`.
- `EventDispatcher`: `hover_id/down_id/last_event/last_target/prev_event/prev_target/press_x/press_y/drag_dx/drag_dy` + **pointer capture** (giữ chuột thì hover giữ nguyên widget nhận `down`; click chỉ tính khi nhả trong widget đó), `dispatch_move/down/up/cancel`, `event_name()`. Mã: 1 Enter / 2 Leave / 3 Down / 4 Up / 5 Click.
- Touch/gesture: `TouchEventArgs(touch_id,px,py,pressure,radius)` + `make_touch`, `GestureEvent(gtype,scale,dx,dy)`, `GestureRecognizer(touch_down/move/up/to_event/reset)` → TAP (đi ≤ 6px) / PAN / PINCH (`scale = dist/start_dist`, pan theo trung điểm 2 ngón), `tkv_sqrt` = `System.Math.Sqrt`.
- Nghiệm thu: `tkvc.exe build TkvUI.Input.tkv --entry input_selftest` → **41/41 PASS, INPUT_OK** (`OnClick` đúng id, click xuyên widget ẩn, capture, Leave→Enter trong 1 call, pinch scale 2.0, tap vs pan).

### 2.7 TkvUI.Layout (mới, P6) — DONE
- `FlexStyle(dir,gap,pad,align,justify)`, `GridStyle(cols,rows,gap,pad)`, `Constraint` + factory `flex_style/grid_style/constraint`.
- `layout_flex_row/col` (WRAP, per-line cross-align, justify khi 1 dòng), `layout_stack_row/col` (justify + align đầy đủ), `layout_grid` + `layout_grid_cell(...,col_span,row_span)`, `layout_dp/layout_dp_i` (DPI), `layout_measure_total`, `layout_alloc_f64/i32`.
- 3 pass: ngắt dòng (`oline`) → chiều cao dòng (`line_h`) → đặt vị trí; out-list song song `ox,oy,ow,oh` (caller cấp phát, index-write).
- Validator tái dùng: `flex_line_count`, `flex_lines_increasing`, `flex_same_line_same_cross`, `flex_no_overlap`, `flex_within_bounds`.
- Nghiệm thu: `--entry layout_selftest` → **50/50 PASS, LAYOUT_OK** (phone 360 / tablet 768 (align CENTER) / desktop 1280 (SPACE_BETWEEN) + column wrap + stack phone 390x844 + grid + span + constraint + DPI).

### 2.8 TkvUI.Widgets + Rendering (P7) — DONE
- Catalog 15 + `UIElement`: `ButtonWidget` (filled/outline, hover/press lerp), `CardWidget` (pill notch), `MetricRingWidget`, `ProgressBarWidget`, `SwitchWidget`, `SliderWidget`, `TextFieldWidget`, `ListViewWidget` (virtualized: `first_visible/visible_count/scroll_by`), `TabsWidget`, `DialogWidget` (backdrop + OK/Cancel + `hit_button`), `ToastWidget` (fade theo `alpha`), `ChartSparklineWidget`, `BottomSheetWidget` (spring), `NavBarWidget`, `SplitViewWidget` (spring + `pane_a/pane_b`) — mỗi widget có `make_*` factory.
- Theme: Core thêm `theme_light()`, `theme_accent()`, `theme_radius()`; widget đọc bảng màu qua hoist `th = theme_dark()` + `th.on_surface`, màu riêng giữ phẳng `cr,cg,cb,ca: "i64"`.
- Animation: `SpringAnimation` (Semi-implicit Euler, rest < 0.2) + `Tween(from,to,duration,easing)` với `ease_linear/out_cubic/in_out_cubic/out_back`.
- Rendering: `InvalidationManager` (union dirty-rect + coalesce theo vùng + `ack`), `FrameScheduler` (budget theo fps, `begin/end`, đếm `dropped`), `RenderLoop.tick(dt, springs, has_input = 0)` (idle > 30 frame → 0% CPU).
- `run()` đã RỜI file thư viện → `examples/TkvUI.Demo.tkv` (notch pill 720x220 + MetricRing lerp + panel Flex + present cửa sổ Win32 ULW) & `examples/TkvUI.DemoMobile.tkv` (phone 390x844 + pad 1024x768 SplitView + touch pinch/pan/tap).
- Nghiệm thu: `TkvUI.Widgets.tkv --entry widget_selftest` → **27/27 PASS, WIDGETS_OK**; `examples/TkvUI.DemoMobile.tkv --entry run` → **TKVUI_MOBILE_OK (6/6)**.

## 3. Mobile/Pad (P8–P9)

> P1.1: khung `AndroidPlatform`/`IOSPlatform` + 2 example đã có (build + chạy headless), nhưng pixel lên thiết bị thật cần host shim — xem §8.2/§8.3.

- P8 Android (10d): `AndroidPlatform` (`Mono.Android`, `ANativeWindow_lock/unlockAndPost`, `Choreographer.postFrameCallback`), gesture pinch.
- P9 iOS + Pad (10d): `IOSPlatform` (`UIKit UIView` + `CADisplayLink`, `libobjc.dylib`), `SplitView` pad.
- `RenderLoop` VSync qua `Choreographer`/`CADisplayLink`; `DPI` scale 2x/3x.

## 4. v3 — Web, 3D, Video decode, Accessibility sâu (8–10 tuần sau v2)

- **TkvUI.Web** (3 tuần): KHÔNG tự viết engine; bridge WebView native (`WebView2` / `WebKitGTK` / `WKWebView` / `android.webkit.WebView`); API `WebViewWidget(url,rect)`, `EvalJS`, `OnMessage`.
- **TkvUI.Video** (3 tuần): KHÔNG tự decode; P/Invoke FFmpeg (`avformat_open_input`, `av_read_frame`, `sws_scale` → YUV→RGBA → `surface_fast_blit`); API `VideoPlayer(path,rect,autoplay)`, `Play/Pause/Seek`; pause → 0% CPU.
- **TkvUI.Accessibility** (2 tuần): bridge `UIAutomation` / `AT-SPI` / `NSAccessibility`+`UIAccessibility` / `AccessibilityNodeInfo`; `UIElement` thêm `a11yLabel`, `role`; cây `a11yTree` từ `Layout`.
- **TkvUI.3D** (3 tuần): v3a software — `Matrix4x4`, `Vertex`, pipeline Model→View→Projection, `RasterizeTriangle` + `DepthBuffer: list[f64]`; v3b tùy chọn GPU (`SharpDX`/Vulkan `SwapChain`, flag build).

## 5. Kế hoạch phase & nghiệm thu

| Phase | Nội dung | Thời gian | Nghiệm thu |
|---|---|---|---|
| P1 | Foundation v2 + Graphics Sin/Cos + tái cấu trúc import | 2d | `surface_blend_pixel` đúng; `draw_arc` 0–360° sai số < 1px; build chain qua import 0 lint |
| P2 | Text v2 + Effects Kawase | 2d | căn lề Center/Right đúng; `backdrop_blur` kính mờ |
| P3 | Platform Win32 thực | 3d | cửa sổ `WS_EX_LAYERED` trong suốt, `Present` không chớp (DONE: ULW độc quyền + colorkey + alpha, verified err=0) |
| P4 | Portability + WinForms vehicle + backend parity (điều chỉnh: X11-native blocked, Cocoa thiếu máy test) | 2d | Mono bit-identical + `WF_OK` 2 runtime (DONE, xem §6) |
| P5 | Input Router + HitTest | 1d | `OnClick` đúng id (DONE: 41/41 PASS `INPUT_OK`, xem §7) |
| P6 | Layout Flex/Grid | 2d | 3 màn hình Flex wrap đúng (DONE: 50/50 PASS `LAYOUT_OK`, xem §7) |
| P7 | Widget catalog 15 + Theme + examples/ | 3d | Demo notch pill + MetricRing lerp qua `Spring` (DONE: 27/27 PASS `WIDGETS_OK` + `TKVUI_MOBILE_OK`, xem §7) |
| P8 | Android backend + Touch | 10d | `Present` via `ANativeWindow`, gesture pinch |
| P9 | iOS backend + Pad + DemoMobile | 10d | `CADisplayLink`, SplitView pad |

Mỗi phase: `tkvc.exe build <file> --entry <func>` + `syntax_baseline` 0 findings (linter CHỈ chạy trên file entry → thư viện chỉ cần sạch khi được build standalone; verify qua chuỗi import). Rủi ro chính: shape `__tkv_extern_method__` sai → validate `name/assembly/class/method/params/returns` trước build; mobile CIL cần `.NET 8` → spike Android trước. Lệnh verify lặp lại được (khuyến nghị dùng script, chấp nhận `*_SKIPPED` cho backend mobile):

```bash
bash tools/verify.sh          # build + chay TAT CA selftest headless, exit != 0 neu FAIL
TKVC=/d/TokenVector/3.code/dist/tkvc.exe bash tools/verify.sh   # ep duong dan tkvc
```

Các lệnh thủ công tương ứng:

```bash
TKVC=/d/TokenVector/3.code/dist/tkvc.exe   # hoặc tkvc.exe trong PATH
mkdir -p build
$TKVC build TkvUI.Input.tkv   --entry input_selftest   --out build/input_test.exe   && build/input_test.exe
$TKVC build TkvUI.Layout.tkv  --entry layout_selftest  --out build/layout_test.exe  && build/layout_test.exe
$TKVC build TkvUI.Widgets.tkv --entry widget_selftest  --out build/widgets_test.exe && build/widgets_test.exe
$TKVC build examples/TkvUI.DemoMobile.tkv --entry run --out build/TkvUI.DemoMobile.exe && build/TkvUI.DemoMobile.exe
$TKVC build examples/TkvUI.Demo.tkv       --entry run --out build/TkvUI.Demo.exe     # mo cua so that (ULW)
$TKVC build examples/TkvUI.Live.tkv       --entry run --out build/TkvUI.Live.exe     && build/TkvUI.Live.exe   # vong 60fps + selftest 27/27
$TKVC build examples/TkvUI.Live.tkv       --entry run_live --out build/TkvUI.LiveRun.exe && build/TkvUI.LiveRun.exe   # cua so that + chuot that, ESC thoat
```

## 6. P4 findings — Portability & Cross-platform windows (DONE)

### 6.1 Cross-runtime: PEVerify + Mono là vòng kiểm chuẩn
- Mọi số nguyên trộn width trong ARITHMETIC (`i32×i64`, `int×float`) là unverifiable IL: `.NET Framework` bỏ qua (cho đáp án đúng/luck), Mono ném `OverflowException`/`InvalidProgramException`.
- Quy tắc cuối (bằng chứng 2 runtime): arithmetic/compare MỌI phía phải CÙNG width (literal tự thích nghi); `float()`/`int()` là cầu nối verifiable duy nhất (`float(i64)`→`conv.r8`, `int(i64)`→`conv.i4`, verified cả 2 phía); `int32→i64` MOVE an toàn mọi runtime với giá trị nhỏ (0–255, probe `WIDE:200,200` cả 2 phía); `i64→i32` narrowing CHỈ an toàn khi giá trị vừa (checked).
- `ColorRgba`/`ColorHsla.a`/`MetricRingWidget.cr..ca`/`color_from_rgb`/`hex_*` đã chuyển `i64`; `color_lerp`/`fill`/`stroke`/`draw_image`/`present-rgb` viết lại single-width; còn lại 14 note PEVerify toàn là small-MOVE (0–255) đã PROVE an toàn bằng run Mono bit-identical.
- Chuẩn verify mới: `PEVerify.exe` 0 lỗi ARITHMETIC + run bit-identical Windows/Mono. Residual Int32↔Long ở ColorRgba-ctor (giá trị 0–255) được chấp nhận có tài liệu.

### 6.2 X11-native bị chặn ở compiler; WinForms là vehicle đa nền tảng
- `__tkv_extern_pinvoke__` regex `dll` bắt buộc `.dll` → KHÔNG khai báo được `libX11.so`/`.dylib`. X11-present native chờ compiler hỗ trợ `.so` (yêu cầu upstream) hoặc hiện thực X11-wire-protocol qua socket (chưa có X server để test).
- Thay thế: `__tkv_extern_class__` + `System.Windows.Forms` (`TkvUI.Platform.tkv`: `wf_create/show/hide/close/set_title/set_opacity/refresh`, property `Text`/`Opacity`) — cửa sổ THẬT trên Windows (.NET FX) và Linux (Mono X11 backend + Xvfb), verified `WF_OK`/`WFLIB_OK` cả 2 phía, STA-safe.
- Linter chỉ check file entry → library chứa pragma thoải mái (verified build không `--no-lint` qua import).
- Giới hạn đã chứng minh: record KHÔNG được chứa field kiểu extern-class; WinForms KHÔNG present được pixel (mọi đường vào `Bitmap` đều cần struct `Color`/`Image`/`Rectangle`); present Linux vẫn là stub cho tới khi có `.so` pinvoke.
- Backend parity: `X11Platform`/`CocoaPlatform` đủ method surface (`present_diff`, `set_alpha/title`, `show_window`, `close_window`, `backend_name`) để app code biên dịch thống nhất; `Win32Platform.backend_name()` + `wf_backend_name()`.

## 7. P5–P7 findings — Input / Layout / Widgets (DONE)

### 7.1 Nghiệm thu headless là mặc định
- Mỗi phase có 1 entry tự kiểm trả về `"INPUT_OK"` / `"LAYOUT_OK"` / `"WIDGETS_OK"` và in `n/N PASS` — chạy được không cần cửa sổ, không cần GPU (lệnh đầy đủ ở cuối §5).
- Đếm PASS/FAIL bằng **accumulator list** (`acc[0]` = PASS, `acc[1]` = tổng) truyền vào hàm check — index-write của list lan ra caller, thay cho việc phải return nhiều giá trị.
- Kiểm tra pixel phải so SNAPSHOT trước/sau (`surface_fast_blit` sang buffer thứ hai + `widget_count_changed`) — đếm `!= màu nền` bị sai khi blend vô tình cho ra đúng màu nền (bài học: `dialog + backdrop` từng ra delta ÂM).

### 7.2 Input router
- `EventDispatcher` dùng **pointer capture**: đang giữ chuột thì hover giữ nguyên widget đã nhận `down` (không bắn Leave/Enter khi kéo ra ngoài); khi nhả, click CHỈ tính nếu điểm nhả còn nằm trong widget đã nhận `down` (verified `release outside -> no click` vs `release inside -> click`).
- 1 lần dispatch có thể sinh 2 sự kiện (Leave→Enter, Up→Click) nên state có 2 slot `prev_event/prev_target` + `last_event/last_target`; mỗi dispatch RESET slot `last` (move không có gì mới → `TKV_EVT_NONE`), nên test phải khẳng định đúng slot.
- Cây widget truyền bằng list SONG SONG (`ids,xs,ys,ws,hs,flags`) vì record không chứa được `list`; `flags != 0` = ẩn/disabled (test: click xuyên widget ẩn xuống nút bên dưới).

### 7.3 Layout
- Wrap + đặt vị trí dùng MỘT con trỏ chạy (`placed_lines` + `cursor`) nên không cần `//` cho chỉ số dòng → tránh hẳn vùng rủi ro `TkvInt × i32`.
- Cross-align theo DÒNG cần 3 pass (ngắt dòng → chiều cao dòng → đặt vị trí); `justify` chỉ áp cho trường hợp 1 dòng (nhiều dòng = START) — ghi rõ trong code.
- Hướng COLUMN đảo vai trục: `flex_same_line_same_cross(oline, ox)`, `flex_no_overlap(oline, oy, oh)`, `flex_lines_increasing(oline, ox)` — test invariant phải rẽ theo `st.dir` mới đúng (bug test đầu tiên: dùng `oy` cho cả 2 hướng).

### 7.4 Widgets / examples
- Widget giữ màu riêng phẳng `cr,cg,cb,ca: "i64"` (nested attribute bị lint cấm) hoặc đọc theme qua hoist `th = theme_dark()`; hover/press = `color_lerp` với trắng/đen.
- `ListViewWidget` chỉ vẽ `first_visible()..+visible_count()`: probe phone scroll 900px → `first=50, visible=7/5000`; pad 20.000 dòng → `first=6` (virtualization thật, không vẽ 5.000 dòng).
- Demo desktop tạo cửa sổ Win32 thật (ULW) nhưng **vẫn kèm console** vì tkvc/ilasm gắn subsystem CUI → zero-console cần `.subsystem 0x0002` (chỉ chèn qua plugin `extra_classes`, chưa có đường .tkv thuần; `TOKENVECTOR_EXPERIENCE.md` §13). Nhãn text giữ ASCII (`§14`).
### 7.5 Live harness (P7.5, `examples/TkvUI.Live.tkv` — DONE, 27/27 PASS `TKVUI_LIVE_OK`)
- Noi day mot vong that: Flex dat vi tri → scene 15 widget → `EventDispatcher`/`hit_test_tree` → `InvalidationManager` → `RenderLoop.tick` (idle → sleep 12ms, 0% CPU) → `present_diff` + copy `shown` (contract P3). Nghiem thu: present dau 155.152px; vong anim 62 render + 178 idle/240 frame; assert `diff=0` cho frame giong het.
- `Environment.TickCount` la PROPERTY C# → `__tkv_extern_method__` sinh call `get_TickCount` KHONG ton tai (`MissingMethodException`). Do gio = pinvoke `GetTickCount` (kernel32, stdcall, i32) — duong pinvoke da verify o P3; `Thread.Sleep` (extern_method) van OK vi la method that.
- Ràng buộc list-method MỚI: method đầu tiên nhận list vừa gán literal/append **trong cùng scope** phải đứng SAU một call hàm thường cùng tham số (vd `hit_test_tree(...)` trước `disp.dispatch_move(...)`) — nếu không `OverflowException` (ToI32) ngay runtime dù code build 0 lint. Ghi chú tại chỗ gọi trong Live.
- Assertion điểm chạm lấy TỪ GEOMETRY widget (`e.px = sw.bx + 10.0`) — hardcode số cứng bẻ gãy khi layout đổi (progress bar flex-center cao 8px: click y=112 sai 6px → FAIL).
- `present_diff = 0` chỉ đúng khi `shown` phản chiếu TRẠNG THÁI CUỐI (settled): spring step đến `is_rest` xong phải render + copy `shown` thêm 1 lần trước khi assert — frame cuối cùng đã render có thể near-rest (10.03) nhưng state cuối là rest chính xác (10.00) → diff rơi vãi vài px.
### 7.6 Input poll thật (P7.6, `run_live` — DONE, `TKVUI_LIVE_RUN_OK`)
- Thêm `TkvUI.Platform.tkv`: `win_poll_messages` (pump `PeekMessageA` PM_REMOVE), `win_pointer_x/y` (`GetMessagePos` LOWORD/HIWORD), `win_key_down` (`GetAsyncKeyState`). `run_live` bơm chuột thật vào `EventDispatcher`: hover → nút, giữ kéo → slider (`set_from_pointer`), click → switch/tabs/notch retarget ring; ESC (vk 27) thoát; tự kết thúc sau 600 vòng.
- Spike chốt: pinvoke `returns` chỉ nhận `void/bool/f32/f64/i32/i64/object/str/type/u64` — **KHÔNG có `i16`** → `GetAsyncKeyState` khai `i32` (SHORT sign-extend); `float()` trên giá trị i32 TRẢ TỪ PINVOKE thì ĐÚNG (lstrlen=6 → 6.0) — quirk `float(TkvInt)` chỉ dính giá trị literal/phần tử list.
- **Bug 1 — WM_PAINT (0x0F) không được drain**: ta không `DispatchMessage` nên update region không bao giờ validate → Windows repost WM_PAINT vô hạn → pump>0 mãi → render mỗi vòng (~430ms/frame GDI, 600 vòng không xong). Fix: drain 2 dải loại trừ 15 (A=0..14, B=16..).
- **Bug 2 — WM_INPUT (0x00FF) là input giả**: chuột vật lý repost ~2 WM_INPUT/frame → `pump>0` liên tục → `had_input=1` mỗi vòng → không bao giờ idle. Fix: `win_poll_messages` CHỈ ĐẾM mouse (0x0200..0x020A) + keyboard (0x0100..0x0108) làm input; dải còn lại (A=0..14, B=16..255, C=265..511, D=523..32767) drain im lặng. Sau fix: 62 render (spring) + 538 idle/600 vòng — idle thật sự 0% CPU.
- Toạ độ chuột là screen-space → trừ gốc cửa sổ `wh.x/wh.y` (set_pos thì phải cập nhật gốc). Giới hạn đã ghi: toạ độ âm (màn hình thứ 2 bên trái) chưa hỗ trợ (LOWORD không xử dấu).
- Chưa làm (P8/P9 + v3): `WaylandPlatform`, `CocoaPlatform` thật, `X11Platform` thật (chờ compiler cho pinvoke `.so`), pixel upload lên `ANativeWindow`/`CALayer` (cần host shim — §8.3), multi-window `SurfacePool` runtime, atlas/shaper text đầy đủ (hiện là font 5x7 + wrap theo từ), accessibility tree/Web/Video/3D.
- ~~`DetectPlatform()` mới trả hằng 1~~ → đã sửa ở P1.1 (§8.1).

## 8. P1.1 hardening (DONE) — selftest đầy đủ, platform detection thật, mobile không crash

### 8.1 `detect_platform()` probe runtime thật
- Trước: `return 1` hằng số. Nay probe qua `mscorlib` (không dùng API Windows-only) nên chạy được cả Win/Mono: `__tkv_extern_method__` thêm `tkv_getenv` (`System.Environment.GetEnvironmentVariable`, str→str) và `tkv_file_exists` (`System.IO.File.Exists`, str→bool).
- Thứ tự probe: `TKVUI_PLATFORM` (override 1..6, tiện test) → `ANDROID_ROOT`/`ANDROID_DATA`/`/system/build.prop` (5) → `/var/mobile` (6) → `/System/Library/CoreServices` (4) → `WAYLAND_DISPLAY` (3) → `DISPLAY` (2) → `windir` (1) → fallback 1 (Win32 là backend duy nhất đầy đủ).
- `detect_platform_id()` trả tên backend (`win32`/`x11`/`wayland`/`cocoa`/`android`/`ios`).
- Spike P1.1: `tkv_getenv` OK nhưng biến không tồn tại trả **null** → `len(null)` = `NullReferenceException`; phải nối chuỗi trước (`tkv_getenv(name) + "|"` — `String.Concat` null-safe). `System.Environment.get_OSVersion` → `MissingMethodException: System.Object System.Environment.get_OSVersion()` (kiểu trả về khai báo phải khớp CHÍNH XÁC kiểu thật) → không dùng property getter của `Environment`.
- `File.Exists` khai `returns: "bool"` chạy tốt; so sánh `== True` / `== False` được (dù §0 cấm dùng `bool` cho biến, chỗ này là giá trị trả về của extern).

### 8.2 Backend mobile gate theo platform (hết crash)
- `AndroidPlatform.create()` / `IOSPlatform.create()` kiểm `detect_platform()` TRƯỚC khi gọi pinvoke native → ngoài nền tảng tương ứng trả `PlatformWindowHandle(handle=0, …)` + in lý do, không gọi `android.dll`/`libobjc.dll` (trước đây `examples/TkvUI.IOSDemo.tkv` chết `DllNotFoundException: libobjc.dll` ngay trên Windows).
- `examples/TkvUI.AndroidDemo.tkv` / `IOSDemo.tkv` trả `ANDROID_DEMO_SKIPPED` / `IOS_DEMO_SKIPPED` khi handle = 0 (verify coi là pass).

### 8.3 Contract host-driven cho pixel (và bug ghi đè bộ nhớ iOS)
- **Bug đã sửa**: `IOSPlatform.present()` cũ gọi `CGBitmapContextCreate(0, …)` (data=NULL) rồi ghi pixel bằng `win_wsprintf(ctx + i*4, …)` → ghi thẳng vào vùng nhớ của **đối tượng CGContext** (corrupt trên thiết bị). Nay không ghi vào con trỏ lạ; upload do host đảm nhiệm.
- `AndroidPlatform.present()` cũ dùng `VirtualAlloc`/`wsprintf` (API **Windows**) trên đường Android → đã bỏ. Nay host phải cấp `set_jni_env(env)` + `set_frame_buffer(src)` + `set_dst_bits(bits)`, sau đó gọi shim `Java_com_tokenvector_TkvUI_copyPixels` + `ANativeWindow_unlockAndPost`; thiếu một trong ba → trả 0 kèm log.
- `IOSPlatform.set_frame_buffer(ptr)` giữ buffer RGBA native của host cho đường upload (host vẽ/upload bằng CoreGraphics).
- Lý do chưa thể tự upload từ thư viện: compiler bắt buộc pinvoke kết thúc `.dll` (không khai được `libc.so`/`libSystem.dylib`) và không có primitive `memcpy`/`Marshal.WriteByte` khớp signature → **giữ nguyên yêu cầu upstream như §6.2**.

### 8.4 Selftest phủ hết module
- Thêm `core_selftest` (47), `graphics_selftest` (29), `text_selftest` (29), `effects_selftest` (24), `platform_selftest` (24) — 4 module Core/Graphics/Text/Effects trước đây KHÔNG có test nào. Quy ước: acc list (`acc[0]`=PASS, `acc[1]`=tổng), trả `"<MODULE>_OK"` / `"<MODULE>_FAIL"`.
- `TokenVector.UI.tkv` thêm `tkvui_selftest()` + `main()` → entry mặc định nên `tkvc build TokenVector.UI.tkv` chạy được **không cần `--entry`**; gom 8 module: `CORE_OK / GRAPHICS_OK / TEXT_OK / EFFECTS_OK / PLATFORM_OK / INPUT_OK / LAYOUT_OK / WIDGETS_OK` → `TKVUI_OK`.
- `tools/verify.sh`: build + run 12 case headless, `exit != 0` khi FAIL, `*_SKIPPED` coi như pass; log từng case trong `build/verify/`. Các demo mở cửa sổ thật (`TkvUI.Demo`, `run_live`) vẫn chạy tay.
- Khi viết test mới cần nhớ: `int()` trên i64 **hạ xuống i32** (so sánh hằng packed > 2^31 phải tách kênh màu), `for`/`range` + counter giữ i32, không nested attribute trên kết quả hàm (`corner_uniform(8.0).br` → lint fail, phải hoist local).

### 8.5 Repo hygiene
- Thêm `README.md`, `CHANGELOG.md`, `LICENSE` (MIT), `.gitignore` (`build/`, `.freebuff/`, `*.exe`, `*.il`).
- `build/` còn artifact mồ côi (`ui_test.*`, `platform_test.*`, `umbrella.*`) không có source `.tkv` tương ứng → đã ignore, không tính là nguồn; `tools/verify.sh` sinh lại artifact có kiểm chứng ở `build/verify/`.
- Version: `tkvui_version()` = `2.1.0`.
