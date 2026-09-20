# TokenVector.UI (TkvUI)

![Verify](https://img.shields.io/badge/verify-35%20PASS%2F0%20FAIL%2F2%20SKIPPED-green)
![Version](https://img.shields.io/badge/version-2.9.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Binary](https://img.shields.io/badge/binary-649KB-brightgreen)

Thư viện UI đa nền tảng viết **100% bằng TokenVector (`.tkv`)**, zero dependency (không Skia/SDL/WPF/Qt).
Rasterizer, font, effects, layout, widget và cửa sổ native đều tự viết, biên dịch bằng `tkvc.exe` → IL → `.exe`.

- Version: **2.9.0** (`tkvui_version()` trong `TokenVector.UI.tkv`)
- **35 PASS / 0 FAIL / 2 SKIPPED** (`TKVUI_VERIFY_OK`, 2026-09-18)
- **Binary 649 KB** (suite 18 module) | app ~370–430 KB
- **Startup ~31 ms** (trivial) / **Memory 27.6 MB** (idle) | **Text 21.8 ms** (400×54 chars) | Widget <0.001 ms/w
- **Niche độc quyền**: Vietnamese-first (134 glyph precomposed), PDF writer + SQLite in-memory, 16 native-look widgets, DesignerApp interactive
- **WASM**: interp chạy thật (wasmtime DATA_OK), browser canvas demo, AOT closed upstream
- **A11y**: NVDA evidence (control đọc được, TkvUI vô hình) — cần UIA provider Phase 9.2
- License: MIT (xem `LICENSE`)

## Quickstart

```bash
# 1. Build + chay toan bo selftest headless (khong mo cua so)
TKVC=/d/TokenVector/3.code/dist/tkvc.exe bash tools/verify.sh

# 2. Tu build mot module
$TKVC build TkvUI.Layout.tkv --entry layout_selftest --out build/layout_test.exe && build/layout_test.exe

# 3. Build ca thu vien + chay suite (entry mac dinh 'main')
$TKVC build TokenVector.UI.tkv --out build/tkvui_suite.exe && build/tkvui_suite.exe   # -> TKVUI_OK

# 4. Demo co cua so that (Windows, Win32 UpdateLayeredWindow - mo kem console, ESC de thoat)
$TKVC build examples/TkvUI.Demo.tkv    --entry run      --out build/TkvUI.Demo.exe    && build/TkvUI.Demo.exe
$TKVC build examples/TkvUI.Live.tkv    --entry run_live --out build/TkvUI.LiveRun.exe && build/TkvUI.LiveRun.exe
```

`tkvc.exe` mặc định được tìm ở `D:\TokenVector\3.code\dist\tkvc.exe`; đặt biến `TKVC` nếu nằm chỗ khác.

## Cấu trúc

| File | Nội dung |
|---|---|
| `TkvUI.Core.tkv` | `ColorRgba`/`ColorHsla`, `Point2D`, `Rect2D`, `Matrix3x2`, `PixelSurface` (buffer `list[i64]`), Theme token, Insets/CornerRadius, DPI, SurfacePool-lite |
| `TkvUI.Graphics.tkv` | `draw_line` (Bresenham + brush), `fill_round_rect`, `stroke_round_rect`, `draw_arc` (Sin/Cos thật), `draw_polyline`, `clip_rect_intersect`, `draw_image` |
| `TkvUI.Text.tkv` | Font bitmap 5x7 (95 glyph ASCII + **134 glyph tiếng Việt precomposed**), **glyph atlas pre-baked** (`text_atlas_record` + `text_atlas_draw_string` — vẽ bằng blit), `char_code` (mã ASCII qua binary search), `measure_string`, `draw_string` (align/tracking/scale), wrap theo từ + ellipsis, **sequence-aware UTF-8** (`vi_strlen`, `vi_seq_len_at`, `vi_truncate`), **TTF parser/rasterizer đã verify** (`ttf_*`: head/hhea/hmtx/cmap-4/glyf quadratic + scanline fill, synthetic-font selftest) |
| `TkvUI.Effects.tkv` | `apply_box_blur`, `box_blur_pass` (sliding window), **`half_res_blur` (downsample 2× → blur → upsample bilinear, ~2.5× nhanh hơn)**, `kawase_blur` 3-pass, `backdrop_blur` (kính mờ), specular, drop shadow |
| `TkvUI.Platform.tkv` | `detect_platform()` **thật** (probe runtime), Win32 (ULW + DIB) thật, X11/Cocoa (stub có factory `make_x11_platform`/`make_cocoa_platform`), Android/iOS (contract host-driven, có gating), **WinForms interop thật** (`wf_create/set_title/set_bounds/get_bounds/set_opacity/hide/do_events/close` — đã verify headless, không `Show`), **IME Win32** (`ImmGetContext`/`ImmReleaseContext`/`ImmGetCompositionStringW`/`ImmNotifyIME`) + constants/helpers `GCS_COMPSTR`, `GCS_RESULTSTR`, `ime_get_context`, `ime_get_composition_string` |
| `TkvUI.Events.tkv` | Data type sự kiện: `PointerEventArgs`, `HitTestResult`, `pointer_button_label`, `no_hit` |
| `TkvUI.Input.tkv` | `hit_test_tree` topmost-first, `EventDispatcher` (pointer capture), touch + `GestureRecognizer` (tap/pan/pinch) |
| `TkvUI.Layout.tkv` | `FlexStyle`/`GridStyle`/`Constraint`, flex row/col có wrap + cross-align + justify, stack, grid + span, DPI, validator |
| `TkvUI.Widgets.tkv` | `UIElement` + **30 widget** (15 base + `DirectionalPad`/`ControlButton`/`VirtualJoystick` + **`ButtonWidget`/`TextInputWidget` (Vietnamese sequence-aware)** + 10 Ant-inspired: Tag/Badge/Avatar/Alert/Pagination/Steps/Table/Select/Rate/Spin), Spring/Tween, `InvalidationManager`, `FrameScheduler`, `RenderLoop`, `FocusManager` (Tab/Shift-Tab/key routing) |
| `TkvUI.Media.tkv` | **10 widget media player**: `Transport` (prev/play/stop/next), `SeekBar` (progress+buffered+scrub+m:ss), `Volume` (mute + slider ngang/dọc), `Repeat`, `Shuffle`, `Speed`, `Playlist` (virtualized), `Equalizer` (N-band + preset flat/pop/rock/jazz/classical), `Spectrum` (bars + peak falloff), `ABLoop`, `media_format_time` |
| `TkvUI.Font.tkv` | **Windows-only, optional** (không import bởi umbrella): bake font TrueType thật qua GDI (`CreateFontA`+`TextOutA` vào DIB → atlas alpha coverage), `font_measure`/`font_draw_string`; `font_selftest` 11/11 (chạy tay, cần GDI) |
| `TokenVector.UI.tkv` | Umbrella: import 10 module + `main()` chạy toàn bộ selftest |

`examples/` : `Demo` (desktop Win32 thật), `DemoMobile` (phone/pad + touch), `Live` (vòng 60fps + input thật), `MediaDemo` (màn hình player ghép đủ 10 widget media, 8/8), `MediaPlayer` (app nghe nhạc đầy đủ: MCI + spectrum, mở cửa sổ thật — không headless, ngoài verify.sh), `AndroidDemo`, `IOSDemo`, **`VietDemo` (Vietnamese Button/TextInput + platform info, headless)**.
`docs/TkvUI.Roadmap.md` : roadmap v2/v3 + **§0 ràng buộc compiler** (đọc trước khi sửa `.tkv`) + findings từng phase.
`docs/INTEGRATION.md` : **hướng dẫn tích hợp** — app khác import TkvUI như thế nào.
`tkvui.pkg.json` : manifest gói (version, modules, selftest, nền tảng).
`tools/package.sh` : đóng gói release → `dist/TokenVector.UI-<version>.tkvpkg` (+ `.sha256`), `--verify` để build thử từ bản giải nén.
`tools/pack_nupkg.ps1` + `nuget/TokenVector.UI.nuspec` : đóng gói NuGet → `dist/TokenVector.UI.<version>.nupkg` (kèm DLL).
`DEVELOPMENT_PLAN.md` : kế hoạch v3 → parity (text shaping, GPU, a11y, tooling, mobile).

## Kết quả verify (2026-09-16)

| Nhóm | Kết quả |
|---|---|
| `core_selftest` | 47/47 PASS |
| `graphics_selftest` | 29/29 PASS |
| `text_selftest` | **160/160 PASS** (bitmap/atlas cũ 46 + **Tiếng Việt 20** (`vi_strlen`, `vi_seq_len_at`, `vi_truncate`, `draw_string` sequence-aware, `draw_text_block` wrap/ellipsis) + **TTF 64**: readers, bit helpers, emit, bezier/flatten, font synthetic 314B end-to-end, metrics, atlas bake; kèm benchmark atlas ~4× + **i18n baked 18**: `utf8_seq_len`, codepoint/slot lookup, bake 10 glyph thật (times Hebrew/Arabic + msyh CJK) vào atlas, `text_atlas_draw_i18n` — alef gọn 1 cột thay vì 2 box + **fallback 12**: `font_family_resolve` ASCII/Viet/he/cjk/box, `text_draw_fallback`, space blank) |
| `effects_selftest` | 32/32 PASS (kèm benchmark blur: sliding-window O(1)/px; **half-res blur ~2.5× nhanh hơn** full-res) |
| `platform_selftest` | **48/48 PASS** (cũ 24 + **WinForms interop thật 10**: create/set_title/set_bounds/get_bounds roundtrip/opacity/hide/do_events/close trên Form thật, headless + **theme 8**: `theme_detect_os` stub UNKNOWN, `theme_pick` dark/light, `theme_changed` polling + **multi-window 6**: factory, create/present/close 2 cửa sổ thật) |
| `input_selftest` | 41/41 PASS |
| `layout_selftest` | 50/50 PASS |
| `widget_selftest` | **101/101 PASS** (đo thật 2026-09-18; gồm Ant-widget, RenderLoop, FocusManager, IME/backspace Việt + `render_loop_pump_all` 2 checks) |
| `media_selftest` | **80/80 PASS** (transport/seek/volume/repeat/shuffle/speed/playlist/eq/spectrum/ablooop + format_time) |
| `bidi_selftest` | **112/112 PASS** (UAX #9 X/W/N/I + visual order + UTF-8 split Hebrew/Arabic/CJK/emoji + `bidi_draw_visual_atlas`: milestone `"你好 🌍 שלום"` vẽ glyph thật theo đúng thứ tự RTL) |
| `gpu_selftest` | **66/66 PASS** (abstraction + factory + pick + probe 44 + **Vulkan device flow 11** + **Shader pipeline abstraction 9** + **D3D11/Metal stubs 4**) |
| `TkvUI.Live` | `TKVUI_LIVE_OK` (27/27) |
| `TkvUI.DemoMobile` | `TKVUI_MOBILE_OK` (6/6) |
| `TkvUI.MediaDemo` | `TKVUI_MEDIA_DEMO_OK` (8/8) |
| `font_selftest` (`TkvUI.Font`, chạy tay) | **11/11 PASS** (GDI bake + measure/draw; Windows-only, ngoài verify.sh) |
| `TkvUI.AndroidDemo` / `IOSDemo` | `*_SKIPPED` trên Windows (backend mobile cần thiết bị thật) |

## Hỗ trợ nền tảng

| Backend | Trạng thái | Ghi chú |
|---|---|---|
| Win32 | **Thật** | `CreateWindowExW` + `WS_EX_LAYERED`, `CreateDIBSection`, `UpdateLayeredWindow` (present_diff 0 khi frame không đổi) |
| X11 | Stub | Chờ `tkvc` cho phép pinvoke `libX11.so` (linter hiện bắt buộc hậu tố `.dll`) |
| Wayland | Chưa có | Cùng ràng buộc `.so` |
| Cocoa / macOS | Stub | `WinForms` dùng làm vehicle (`wf_*`) khi cần cửa sổ thật |
| Android | Contract host-driven | Cần host cấp JNI env + native ARGB buffer (`set_jni_env`, `set_frame_buffer`, `set_dst_bits`) |
| iOS | Contract host-driven | Cần host cấp buffer RGBA (`set_frame_buffer`); upload pixel do host làm |

`detect_platform()` trả 1=Win32, 2=X11, 3=Wayland, 4=Cocoa, 5=Android, 6=iOS bằng probe runtime
(biến môi trường + file probe qua `mscorlib`), ép được bằng `TKVUI_PLATFORM=1..6` khi test.

## Đóng gói release

```bash
# 1) Source package (.tkvpkg = zip source, có checksum)
bash tools/package.sh --verify
# -> dist/TokenVector.UI-2.3.1.tkvpkg (+ .sha256)
#    PKG_VERIFY_OK = suite build + chay OK tu ban giai nen

# 2) NuGet package + DLL (.nupkg chứa .tkv sources + TokenVector.UI.dll)
powershell -ExecutionPolicy Bypass -File tools/pack_nupkg.ps1
# -> dist/TokenVector.UI.2.3.1.nupkg (~170 KB)
```

`.tkvpkg` là file zip chứa toàn bộ source thư viện (10 module + umbrella + manifest + docs + examples).
App khác chỉ cần giải nén rồi `__tkv_import__ = ["TokenVector.UI"]` — chi tiết ở `docs/INTEGRATION.md`.

`.nupkg` (manifest `nuget/TokenVector.UI.nuspec`) chứa thêm `runtimes/any/native/TokenVector.UI.dll` —
assembly .NET của umbrella (entry `main`, chạy cả selftest) dùng được như tham chiếu .NET; phần source
`.tkv` nằm ở `tkv/` trong package. DLL build bằng `tkvc build TokenVector.UI.tkv` (exe .NET đổi tên `.dll`).

## Giới hạn đã biết

- Text: font bitmap 5x7 + atlas + wrap theo từ đã xong; **TTF parser/rasterizer đã verify trên font synthetic** (sửa 4 bug: tag `hhea`/`hmtx`/`maxp`, offset `segCountX2`, thiếu `j = j + 1`, nested list null runtime). **Chưa** có: shaper/bidi/RTL/emoji/IME, load font thật từ file (cần file-IO — compiler gap), hinting/composite glyph (Phase 1 của `DEVELOPMENT_PLAN.md`); nhãn giữ ASCII.
- WinForms: window/app-level (`create/title/bounds/opacity/hide/do_events/close`) đã nối thật + verify; control-level (`create_control/add/remove/text/font/color/dock/events`) và `Handle` còn stub — cần extern Control-typed + IntPtr (compiler gap).
- Mobile: pixel upload lên `ANativeWindow`/`CALayer` cần host shim (compiler chưa cho pinvoke `.so`/`.dylib`), xem `docs/TkvUI.Roadmap.md §8`.
- Accessibility tree, WebView, Video (FFmpeg), 3D: chưa có (v3 scope).
- Demo desktop mở kèm console (`tkvc`/`ilasm` gắn subsystem CUI; zero-console cần `.subsystem 0x0002`).
- **Trước khi sửa `.tkv`, đọc `docs/TkvUI.Roadmap.md §0`** — compiler TokenVector có nhiều quirk (không `& | >> <<`, không `bool`, cấm nested attribute, record không chứa `list`, trộn width sinh IL unverifiable…).
