# TokenVector.UI (TkvUI)

![Verify](https://img.shields.io/badge/verify-47%20PASS%2F0%20FAIL%2F2%20SKIPPED-green)
![Version](https://img.shields.io/badge/version-2.9.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Binary](https://img.shields.io/badge/binary-649KB-brightgreen)

Thư viện UI đa nền tảng viết **100% bằng TokenVector (`.tkv`)**, zero dependency (không Skia/SDL/WPF/Qt).
Rasterizer, font, effects, layout, widget và cửa sổ native đều tự viết, biên dịch bằng `tkvc.exe` → IL → `.exe`.

- Version: **2.9.0** (`tkvui_version()` trong `TokenVector.UI.tkv`)
- **48 PASS / 0 FAIL / 2 SKIPPED** (`TKVUI_VERIFY_OK`, 2026-09-22 — 30 module + suite 32/32 + 16 example; android/ios SKIPPED, cần thiết bị thật)
- **~2110 checks** qua suite (core 47, text 238, bidi 150, widgets 101, native 164, emoji 107, shaping 91, sqlite 132, video 44, tkvv 56, mjpg 44, mp4 62, …)
- **Binary 649 KB** (suite 26 module) | app ~370–430 KB
- **Startup ~31 ms** (trivial) / **Memory 27.6 MB** (idle) | **Text 9.4 ms** (400×54 chars, thắng PyQt6 ~1.9×) | Widget <0.001 ms/w
- **Niche độc quyền**: Vietnamese-first (134 glyph precomposed), **emoji bake 12 symbol 12×12** (`TkvUI.EmojiData`), PDF writer + SQLite (persist + in-memory), ~40 widget, DesignerApp interactive
- **WASM**: interp chạy thật (wasmtime DATA_OK), browser canvas demo, AOT closed upstream
- **A11y**: NVDA evidence (control đọc được, TkvUI vô hình) — cần UIA provider Phase 9.2
- License: MIT (xem `LICENSE`)

## Screenshots (render thật 100% bằng TkvUI, không mock)

| BrowserDemo (160×90, phóng 3×) | Emoji bake 12×12 (240×48, phóng 3×) |
|---|---|
| ![TkvUI browser demo](docs/img/shot_browser.png) | ![TkvUI baked emoji](docs/img/shot_emoji.png) |

Khung browser: title + button `Go` + progress + slider theo frame (`examples/TkvUI.BrowserDemo.tkv` → base64 RGBA → PNG).
Dải emoji: 12 BMP symbol bake offline từ Segoe UI Symbol (`tools/emoji_gen.py` → `TkvUI.EmojiData.tkv`), vẽ qua `fb_draw_run_emoji`.

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
| `TokenVector.UI.tkv` | Umbrella: import 26 module + `main()` chạy toàn bộ selftest |

`examples/` : `Demo` (desktop Win32 thật), `DemoMobile` (phone/pad + touch), `Live` (vòng 60fps + input thật), `MediaDemo` (màn hình player ghép đủ 10 widget media, 8/8), `MediaPlayer` (app nghe nhạc đầy đủ: MCI + spectrum, mở cửa sổ thật — không headless, ngoài verify.sh), `AndroidDemo`, `IOSDemo`, **`VietDemo` (Vietnamese Button/TextInput + platform info, headless)**, `CrudDemo`/`CrudDemoFull` (đối chứng Phase 6.4), `BenchText`/`BenchWidgets`/`CrudBench` (benchmark), `TkvvBench` (đo fps fast-path TKVV), `BrowserDemo` (render base64 RGBA ra `<canvas>`, 8/8), `PrintDemo`, `A11yDemo`, `Phase1Demo`, `AnimDemo`, `Designer` (+DesignerApp), `Fuzz`, `IMEDemo`, `VideoDemo` (player TKVV 21/21), `QtAppPort` (port Qt Application Example 52/52).
`docs/TkvUI.Roadmap.md` : roadmap v2/v3 + **§0 ràng buộc compiler** (đọc trước khi sửa `.tkv`) + findings từng phase.
`docs/INTEGRATION.md` : **hướng dẫn tích hợp** — app khác import TkvUI như thế nào.
`tkvui.pkg.json` : manifest gói (version, modules, selftest, nền tảng).
`tools/package.sh` : đóng gói release → `dist/TokenVector.UI-<version>.tkvpkg` (+ `.sha256`), `--verify` để build thử từ bản giải nén.
`tools/pack_nupkg.ps1` + `nuget/TokenVector.UI.nuspec` : đóng gói NuGet → `dist/TokenVector.UI.<version>.nupkg` (kèm DLL).
`DEVELOPMENT_PLAN.md` : kế hoạch v3 → parity (text shaping, GPU, a11y, tooling, mobile).

## Kết quả verify (2026-09-22 — `TKVUI_VERIFY_OK`: 47 PASS / 0 FAIL / 2 SKIPPED)

| Nhóm | Kết quả |
|---|---|
| `core_selftest` | 47/47 PASS |
| `graphics_selftest` | 29/29 PASS |
| `text_selftest` | **238/238 PASS** (atlas + Việt + TTF synthetic + i18n baked + fallback, kèm benchmark atlas ~5×) |
| `effects_selftest` | 32/32 PASS (kèm benchmark blur; **half-res blur ~2.5×**) |
| `platform_selftest` | **82/82 PASS** (probe runtime + WinForms interop thật + theme polling + multi-window 2 cửa sổ thật) |
| `input_selftest` | 41/41 PASS |
| `layout_selftest` | 50/50 PASS |
| `widget_selftest` | **101/101 PASS** (Ant-widget, RenderLoop, FocusManager, IME/backspace Việt) |
| `media_selftest` | **80/80 PASS** (transport/seek/volume/repeat/shuffle/speed/playlist/eq/spectrum/ablooop + format_time) |
| `bidi_selftest` | **150/150 PASS** (UAX #9 + visual order + shaping + milestone `"你好 🌍 שלום"` glyph thật RTL) |
| `gpu_selftest` | **66/66 PASS** (abstraction + factory + probe + Vulkan device flow + shader pipeline + D3D11/Metal stubs) |
| `a11y_selftest` | 41/41 PASS |
| `theme_selftest` | 79/79 PASS (palette/metrics + QSS-subset cascade) |
| `native_selftest` | 164/164 PASS |
| `data_selftest` | 76/76 PASS (model/view/delegate + sort/filter proxy) |
| `sqlite_selftest` | 132/132 PASS (CRUD + snapshot tx + rowid-index + persist dual-slot + crash-matrix + kill-9) |
| `printing_selftest` | 63/63 PASS (PDF writer + shell-print) |
| `abridge_selftest` | 94/94 PASS |
| `fallback_selftest` | **37/37 PASS** (resolve/metrics + weighted fontconfig + **emoji raster thật**) |
| `emoji_selftest` (`TkvUI.EmojiData`, mới) | **107/107 PASS** (12 glyph bake + distinct + bounds) |
| `fontdisc_selftest` | 15/15 PASS (weighted matching) |
| `shaping_selftest` | 91/91 PASS (Arabic/Thai/Indic/Bengali/Tamil + lam-alef) |
| `nativedlg_selftest` | 39/39 PASS |
| `ime_selftest` | 37/37 PASS (Telex/VNI + composition) |
| `uia_selftest` / `atspi_selftest` | 33/33 + 22/22 PASS (host-driven provider + HWND mirror) |
| `kittest_selftest` (`TkvUI.KitTest`, mới) | **16/16 PASS** (query role/label + hit-test + act trên widget thật + rebuild + assert, 9 case headless) |
| `video_selftest` (`TkvUI.Video`, mới) | **44/44 PASS** (GIF89a parse + LZW early-change + clock + error paths; s2 gradient 4096px pixel-exact) |
| `tkvv_selftest` (`TkvUI.Tkvv`, mới) | **56/56 PASS** (format custom TKVV: chunk/profile I-P + O(1) seek + reconstruct + clock reuse + fast path presized + errors) |
| `mjpg_selftest` (`TkvUI.Mjpg`, mới) | **44/44 PASS** (MJPEG baseline: parse + Huffman + IDCT + RGB khớp PIL ±2; bench **~106fps @160×120**) |
| `mjpg_hd_selftest` (HD) | **6/6 PASS** (720p đúng pixel, 453ms ~2fps — realtime HD cần bitwise/SIMD, xem CHANGELOG) |
| `videodemo_run` (`examples/TkvUI.VideoDemo`) | **21/21 PASS** (player TKVV: Transport/SeekBar/Speed/ABLoop thật + clock + blit, assert qua pixels) |
| `qtapp_run` (`examples/TkvUI.QtAppPort`, mới) | **52/52 PASS** (port Qt Application Example: MainWindow menus/toolbar/statusbar + RichEdit + DlgFile + Dialog + PDF print + recent + exit, assert state + pixels) |
| `mp4_selftest` (`TkvUI.Mp4`, mới) | **62/62 PASS** (MP4 demux: boxes/tracks/durations/sample-table/extract + realistic co64/ctts/SPS + errors) |
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

- Text: font bitmap 5x7 + atlas + wrap theo từ đã xong; **TTF parser/rasterizer đã verify** (composite, kern format-0, CPAL/COLR-v0 parse+draw, CBDT blit); shaping engine thuần (Arabic/Thai/Indic, 91 check); bidi UAX#9 + fallback chain + **emoji bake 12 symbol**; nhãn giữ ASCII. **Chưa** có: HarfBuzz full (multi-char FFI kẹt compiler), emoji màu/non-BMP (cần cmap12 + bake font màu), load font thật từ file (cần file-IO), hinting.
- WinForms: window/app-level (`create/title/bounds/opacity/hide/do_events/close`) đã nối thật + verify; control-level (`create_control/add/remove/text/font/color/dock/events`) và `Handle` còn stub — cần extern Control-typed + IntPtr (compiler gap).
- Mobile: pixel upload lên `ANativeWindow`/`CALayer` cần host shim (compiler chưa cho pinvoke `.so`/`.dylib`), xem `docs/TkvUI.Roadmap.md §8`.
- Accessibility tree, WebView, Video (FFmpeg), 3D: chưa có (v3 scope).
- Demo desktop mở kèm console (`tkvc`/`ilasm` gắn subsystem CUI; zero-console cần `.subsystem 0x0002`).
- **Trước khi sửa `.tkv`, đọc `docs/TkvUI.Roadmap.md §0`** — compiler TokenVector có nhiều quirk (không `& | >> <<`, không `bool`, cấm nested attribute, record không chứa `list`, trộn width sinh IL unverifiable…).
