# TokenVector.UI (TkvUI)

Thư viện UI đa nền tảng viết **100% bằng TokenVector (`.tkv`)**, zero dependency (không Skia/SDL/WPF/Qt).
Rasterizer, font, effects, layout, widget và cửa sổ native đều tự viết, biên dịch bằng `tkvc.exe` → IL → `.exe`.

- Version: **2.2.0** (`tkvui_version()` trong `TokenVector.UI.tkv`)
- Trạng thái: v2 P1–P7.6 **DONE** + P1.1 hardening + P2.1 glyph atlas (vẽ text bằng blit, nhanh hơn ~vài lần)
- Verify: `bash tools/verify.sh` → **12 PASS / 0 FAIL / 2 SKIPPED** (`TKVUI_VERIFY_OK`)
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
| `TkvUI.Text.tkv` | Font bitmap 5x7 (95 glyph, fallback box cho ký tự ngoài bảng), **glyph atlas pre-baked** (`text_atlas_record` + `text_atlas_draw_string` — vẽ bằng blit), `char_code` (mã ASCII qua binary search), `measure_string`, `draw_string` (align/tracking/scale), wrap theo từ + ellipsis |
| `TkvUI.Effects.tkv` | `apply_box_blur`, `box_blur_pass` (sliding window), **`half_res_blur` (downsample 2× → blur → upsample, ~2.5× nhanh hơn)**, `kawase_blur` 3-pass, `backdrop_blur` (kính mờ), specular, drop shadow |
| `TkvUI.Platform.tkv` | `detect_platform()` **thật** (probe runtime), Win32 (ULW + DIB) thật, X11/Cocoa (stub), Android/iOS (contract host-driven, có gating) |
| `TkvUI.Events.tkv` | Data type sự kiện: `PointerEventArgs`, `HitTestResult`, `pointer_button_label`, `no_hit` |
| `TkvUI.Input.tkv` | `hit_test_tree` topmost-first, `EventDispatcher` (pointer capture), touch + `GestureRecognizer` (tap/pan/pinch) |
| `TkvUI.Layout.tkv` | `FlexStyle`/`GridStyle`/`Constraint`, flex row/col có wrap + cross-align + justify, stack, grid + span, DPI, validator |
| `TkvUI.Widgets.tkv` | `UIElement` + 15 widget (`Button`, `Card`, `MetricRing`, `ProgressBar`, `Switch`, `Slider`, `TextField`, `ListView` virtualized, `Tabs`, `Dialog`, `Toast`, `Sparkline`, `BottomSheet`, `NavBar`, `SplitView`), Spring/Tween, `InvalidationManager`, `FrameScheduler`, `RenderLoop` |
| `TokenVector.UI.tkv` | Umbrella: import 9 module + `main()` chạy toàn bộ selftest |

`examples/` : `Demo` (desktop Win32 thật), `DemoMobile` (phone/pad + touch), `Live` (vòng 60fps + input thật), `AndroidDemo`, `IOSDemo`.
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
| `text_selftest` | 46/46 PASS (kèm benchmark: atlas ~4.2× nhanh hơn classic) |
| `effects_selftest` | 29/29 PASS (kèm benchmark blur: sliding-window O(1)/px; **half-res blur ~2.5× nhanh hơn** full-res) |
| `platform_selftest` | 24/24 PASS |
| `input_selftest` | 41/41 PASS |
| `layout_selftest` | 50/50 PASS |
| `widget_selftest` | 27/27 PASS |
| `TkvUI.Live` | `TKVUI_LIVE_OK` (27/27) |
| `TkvUI.DemoMobile` | `TKVUI_MOBILE_OK` (6/6) |
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
# -> dist/TokenVector.UI-2.1.0.tkvpkg (+ .sha256)
#    PKG_VERIFY_OK = suite build + chay OK tu ban giai nen

# 2) NuGet package + DLL (.nupkg chứa .tkv sources + TokenVector.UI.dll)
powershell -ExecutionPolicy Bypass -File tools/pack_nupkg.ps1
# -> dist/TokenVector.UI.2.1.0.nupkg (~137 KB)
```

`.tkvpkg` là file zip chứa toàn bộ source thư viện (9 module + umbrella + manifest + docs + examples).
App khác chỉ cần giải nén rồi `__tkv_import__ = ["TokenVector.UI"]` — chi tiết ở `docs/INTEGRATION.md`.

`.nupkg` (manifest `nuget/TokenVector.UI.nuspec`) chứa thêm `runtimes/any/native/TokenVector.UI.dll` —
assembly .NET của umbrella (entry `main`, chạy cả selftest) dùng được như tham chiếu .NET; phần source
`.tkv` nằm ở `tkv/` trong package. DLL build bằng `tkvc build TokenVector.UI.tkv` (exe .NET đổi tên `.dll`).

## Giới hạn đã biết

- Text: font bitmap 5x7 + wrap theo từ; **chưa** có font atlas/shaper/bidi/RTL/emoji/IME (Phase 1 của `DEVELOPMENT_PLAN.md`), nhãn giữ ASCII.
- Mobile: pixel upload lên `ANativeWindow`/`CALayer` cần host shim (compiler chưa cho pinvoke `.so`/`.dylib`), xem `docs/TkvUI.Roadmap.md §8`.
- Accessibility tree, WebView, Video (FFmpeg), 3D: chưa có (v3 scope).
- Demo desktop mở kèm console (`tkvc`/`ilasm` gắn subsystem CUI; zero-console cần `.subsystem 0x0002`).
- **Trước khi sửa `.tkv`, đọc `docs/TkvUI.Roadmap.md §0`** — compiler TokenVector có nhiều quirk (không `& | >> <<`, không `bool`, cấm nested attribute, record không chứa `list`, trộn width sinh IL unverifiable…).
