# TokenVector.UI (TkvUI)

![Verify](https://img.shields.io/badge/verify-55%20PASS%2F0%20FAIL%2F2%20SKIPPED-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Catalog](https://img.shields.io/badge/widgets-93%20constructors-brightgreen)

A cross-platform UI library written **100% in TokenVector (`.tkv`)** — zero third-party runtime dependencies (no Skia, SDL, WPF, or Qt).

The rasterizer, font stack, effects, layout engine, widgets, persistence (SQLite), PDF writer, and media codecs are all implemented in this repo and compiled with `tkvc.exe` → CIL/.NET IL → `.exe`.

English | [Tiếng Việt](README.vi.md)

## Highlights

| Area | Status (2026-09-24) |
|---|---|
| **Version** | **1.0.0** (`tkvui_version()` in `TokenVector.UI.tkv`) |
| **Verify** | **55 PASS / 0 FAIL / 2 SKIPPED** (`TKVUI_VERIFY_OK`, 57 cases; Android/iOS need real devices) |
| **Checks** | **~2200+** assertions across the suite |
| **Widget catalog** | **93 constructors** — Widgets 42 + Native 41 + Media 10 (`WIDGETS_BREADTH_OK` 15/15) |
| **Binary / app size** | Suite exe ~1644 KB · apps ~549 KB–3.3 MB (depends on baked assets) |
| **Startup / memory** | Cold ~1.0 s · idle ~11 MB · load-text peak ~46 MB |
| **Text render** | **9.4 ms / 21.6K chars** (≈1.9× faster than PyQt6 on the same workload) |
| **Widget paint** | **~30 ms / 1000 buttons** (PyQt6 ≈ 43 ms) |
| **SQL (file RT)** | **~81 ms / 1000 rows** vs PyQt6 QSQLITE ~195 ms (≈2.4×) |
| **Vietnamese text** | 134 precomposed glyphs · Telex/VNI IME **37/37** |
| **Persistence / print** | Built-in SQLite **132/132** · PDF writer **63/63** |
| **License** | **MIT** |

### What makes this project distinctive

- **Single-language stack:** UI, raster, text, SQL, PDF, GIF/MJPEG/MP4/TKVV codecs — all `.tkv`.
- **Vietnamese-first typography:** 134 precomposed diacritics + sequence-aware UTF-8 + Telex/VNI composer.
- **Optional HarfBuzz wire:** shaped draw path when `libharfbuzz.dll` is present; clean skip when missing.
- **Qt parity ports (headless-proven):** `QtAppPort` **52/52**, `QtTreeDockPort` **31/31**.
- **Custom video path:** TKVV fast-path ~**100 fps @ 720p** (software); MJPEG baseline ~106 fps @ 160×120.
- **WASM:** interpreter path runs (wasmtime `DATA_OK`); browser canvas demo; AOT closed upstream.
- **A11y:** a11y tree + UIA/AT-SPI host-driven providers + KitTest 16/16; NVDA still needs a real UIA provider (roadmap L7).

## Screenshots (rendered 100% by TkvUI — not mock-ups)

| BrowserDemo (160×90, 3× zoom) | Baked emoji strip (240×48, 3× zoom) |
|---|---|
| ![TkvUI browser demo](docs/img/shot_browser.png) | ![TkvUI baked emoji](docs/img/shot_emoji.png) |

Browser frame: title + `Go` button + progress + slider driven by frames (`examples/TkvUI.BrowserDemo.tkv` → base64 RGBA → PNG).  
Emoji strip: 12 BMP symbols baked offline from Segoe UI Symbol (`tools/emoji_gen.py` → `TkvUI.EmojiData.tkv`), drawn via `fb_draw_run_emoji`.

## Quickstart

```bash
# 1) Build + run every selftest headless (no windows)
TKVC=/d/TokenVector/3.code/dist/tkvc.exe bash tools/verify.sh
# -> TKVUI_VERIFY_OK  (55 PASS / 0 FAIL / 2 SKIPPED)

# 2) Build a single module
$TKVC build TkvUI.Layout.tkv --entry layout_selftest --out build/layout_test.exe && build/layout_test.exe

# 3) Build the umbrella suite (default entry `main`)
$TKVC build TokenVector.UI.tkv --out build/tkvui_suite.exe && build/tkvui_suite.exe   # -> TKVUI_OK

# 4) Real Win32 window demos (UpdateLayeredWindow; console opens; ESC quits)
$TKVC build examples/TkvUI.Demo.tkv --entry run      --out build/TkvUI.Demo.exe    && build/TkvUI.Demo.exe
$TKVC build examples/TkvUI.Live.tkv --entry run_live --out build/TkvUI.LiveRun.exe && build/TkvUI.LiveRun.exe
```

`tkvc.exe` is expected at `D:\TokenVector\3.code\dist\tkvc.exe` by default; set `TKVC` if it lives elsewhere.

## Repository layout

| Path | Contents |
|---|---|
| `TkvUI.Core.tkv` | `ColorRgba`/`ColorHsla`, `Point2D`, `Rect2D`, `Matrix3x2`, `PixelSurface` (`list[i64]`), theme tokens, insets, DPI, surface pool |
| `TkvUI.Graphics.tkv` | Bresenham lines, filled/stroked round rects, arcs, polylines, clip, image blit |
| `TkvUI.Text.tkv` | 5×7 bitmap font (95 ASCII + **134 Vietnamese precomposed**), pre-baked glyph atlas, measure/draw/wrap/ellipsis, verified TTF parser/rasterizer, `text_atlas_draw_shaped` (HarfBuzz wire) |
| `TkvUI.Viet.tkv` | Vietnamese bitmap glyphs + sequence-aware UTF-8 helpers |
| `TkvUI.HarfBuzz.tkv` | Optional leaf FFI for `libharfbuzz.dll`; missing DLL → clean skip |
| `TkvUI.Effects.tkv` | Box blur, half-res blur (~2.1×), Kawase, backdrop blur, specular, drop shadow |
| `TkvUI.Platform.tkv` | Runtime platform probe, real Win32 (ULW+DIB), X11/Cocoa stubs, Android/iOS host contracts, WinForms interop, Win32 IME |
| `TkvUI.Events.tkv` / `TkvUI.Input.tkv` | Event args, topmost hit-test, dispatcher + capture, touch gestures |
| `TkvUI.Layout.tkv` | Flex (wrap/cross/justify), grid+span, stack, DPI validator — **50/50** |
| `TkvUI.Widgets.tkv` | `UIElement` + **42 widgets** (base, Ant-inspired, Wave A breadth), spring/tween, invalidation, frame scheduler, focus |
| `TkvUI.Widgets.Native.tkv` | **41 native-look widgets** (button…tree multi-sel, dock float/tab, MDI tile, ribbon, property grid, context menu, …) — **255/255** |
| `TkvUI.Media.tkv` | **10 media-player widgets** (transport, seek, volume, playlist, EQ, spectrum, A-B loop, …) |
| `TkvUI.Data.tkv` | Model/view/delegate + sort/filter proxy — **76/76** |
| `TkvUI.SQLite.tkv` | Pure-`.tkv` SQL engine (CRUD, snapshot tx, dual-slot file, crash matrix) — **132/132** |
| `TkvUI.Printing.tkv` | Pure-`.tkv` PDF writer + shell print — **63/63** |
| `TkvUI.Bidi.tkv` / `TkvUI.Shaping.tkv` | UAX#9 bidi **194/194** · complex shaping **91/91** |
| `TkvUI.Video*.tkv` / `TkvUI.Tkvv*.tkv` / `TkvUI.Mjpg*.tkv` / `TkvUI.Mp4*.tkv` | GIF, TKVV, MJPEG, MP4 demux in pure `.tkv` |
| `TkvUI.A11y*.tkv` / `TkvUI.Uia.tkv` / `TkvUI.Atspi.tkv` / `TkvUI.KitTest.tkv` | Accessibility model, bridges, kittest-style GUI tests |
| `TokenVector.UI.tkv` | Umbrella: imports the suite and runs `main()` |
| `tkvui.pkg.json` | Package manifest (version, modules, selftests, platforms) |
| `tools/verify.sh` | One-shot build + headless run of all cases |
| `tools/package.sh` / `tools/pack_nupkg.ps1` | `.tkvpkg` + `.nupkg` packaging |
| `docs/` | Roadmap, API index, benchmarks, competitors matrix, compiler constraints |
| `examples/` | Demos, benchmarks, Qt ports, fuzz, designer, clip player |

Notable examples: `Demo`, `Live` (60 fps), `MediaDemo`, `CrudDemo`, `BrowserDemo`, `VideoDemo`, **`QtAppPort` (52/52)**, **`QtTreeDockPort` (31/31)**, `ClipPlayer` (14/14), `Designer`/`DesignerApp`, `Fuzz`, `AndroidDemo`/`IOSDemo` (device-gated).

## Verify results (2026-09-24 — `TKVUI_VERIFY_OK`: 55 PASS / 0 FAIL / 2 SKIPPED)

| Group | Result |
|---|---|
| `core_selftest` | 47/47 |
| `graphics_selftest` | 29/29 |
| `text_selftest` | **239/239** (atlas + Vietnamese + synthetic TTF + i18n bake + fallback) |
| `effects_selftest` | 32/32 |
| `platform_selftest` | **82/82** (runtime probe + WinForms interop + multi-window) |
| `input_selftest` | 41/41 |
| `layout_selftest` | 50/50 |
| `widget_selftest` | **167/167** |
| `widgets_breadth_selftest` | **15/15 `WIDGETS_BREADTH_OK`** — catalog **93** |
| `media_selftest` | 80/80 |
| `bidi_selftest` | **194/194** |
| `harfbuzz_selftest` / `hbwire_selftest` | **`HBWIRE_OK`** (clean skip without DLL) |
| `gpu_selftest` | 66/66 (abstraction + probes; present path still ULW/CPU) |
| `a11y_selftest` | 41/41 |
| `theme_selftest` | 79/79 |
| `native_selftest` | **255/255** (41 native-look widgets post Wave B) |
| `data_selftest` | 76/76 |
| `sqlite_selftest` | 132/132 (+ crash matrix + kill-9) |
| `printing_selftest` | 63/63 |
| `abridge_selftest` | 94/94 |
| `fallback_selftest` | 37/37 |
| `emoji_selftest` | 107/107 |
| `fontdisc_selftest` | 18/18 |
| `clipboard_selftest` | 12/12 (Win32 ASCII/Việt/emoji round-trip) |
| `shaping_selftest` | 91/91 (Arabic/Thai/Indic/Bengali/Tamil) |
| `nativedlg_selftest` | 39/39 |
| `ime_selftest` | 37/37 (Telex/VNI) |
| `uia_selftest` / `atspi_selftest` | 33/33 + 22/22 |
| `kittest_selftest` | 16/16 |
| `video_selftest` (GIF) | 44/44 |
| `tkvv_selftest` | 56/56 |
| `mjpg_selftest` / `mjpg_hd_selftest` | 44/44 + 6/6 |
| `mp4_selftest` | 62/62 |
| `videodemo_run` | 21/21 |
| `qtapp_run` | **52/52 `QTAPP_OK`** |
| `qttd_run` | **31/31 `QTDOCK_OK`** |
| `clipplayer_run` | 14/14 |
| `suite` (`TokenVector.UI.tkv`) | `TKVUI_OK` |
| `Live` / `DemoMobile` / `MediaDemo` | `TKVUI_LIVE_OK` / `TKVUI_MOBILE_OK` / `TKVUI_MEDIA_DEMO_OK` |
| `AndroidDemo` / `IOSDemo` | `*_SKIPPED` on Windows (need real devices) |

Reproduce with:

```bash
TKVC=/path/to/tkvc.exe bash tools/verify.sh
```

## Platform support

| Backend | Status | Notes |
|---|---|---|
| **Win32** | **Production** | `CreateWindowExW` + `WS_EX_LAYERED`, `CreateDIBSection`, `UpdateLayeredWindow` |
| X11 | Stub | Blocked on `tkvc` allowing pinvoke of `libX11.so` (linter currently requires a `.dll` suffix) |
| Wayland | Not started | Same `.so` constraint |
| Cocoa / macOS | Stub | WinForms vehicle (`wf_*`) used when a real window is required |
| Android | Host contract | Host supplies JNI env + native ARGB buffer |
| iOS | Host contract | Host supplies RGBA buffer; host uploads pixels |

`detect_platform()` returns `1=Win32, 2=X11, 3=Wayland, 4=Cocoa, 5=Android, 6=iOS` via runtime probes; override with `TKVUI_PLATFORM=1..6` in tests.

## Benchmarks (normalized head-to-head — see `docs/BENCH.md`)

| Workload | TkvUI | PyQt6 / Qt 6.11 | Ratio |
|---|---|---|---|
| Text 21.6K chars/block | **9.4 ms** | 13.7–18.1 ms | **~1.9× faster** |
| Construct 1000 buttons | **< 0.16 ms** | 12.6 ms | timer-floor win |
| Paint 1000 buttons | **~30 ms** | ~43 ms | **~1.4× faster** |
| CRUD in-memory total/rep | **~8 ms** | ~14 ms | **~1.8× faster** |
| SQL file round-trip 1000 rows | **~81 ms** | ~195 ms | **~2.4× faster** |
| Idle memory (trivial app) | **~11 MB** | 15.6 MB | **smaller** |
| Cold start | **~1.0 s** | ~0.2 s | **slower (L3 / NGEN)** |
| Load-text peak memory | ~46 MB | 15.6 MB | **larger** |

Timer note: TkvUI uses `GetTickCount` (~16 ms quantum); PyQt uses `perf_counter` (µs). Gate: `BENCH_STABLE_OK` (median of 3 runs).

Slint / egui / Dear ImGui figures are **not** re-measured on this machine — see `docs/COMPETITORS.md` §9 for the public-docs comparison and explicit gaps.

## Packaging

```bash
# 1) Source package (.tkvpkg = zip + checksum)
bash tools/package.sh --verify
# -> dist/TokenVector.UI-<version>.tkvpkg (+ .sha256)
#    PKG_VERIFY_OK = suite builds and runs from the extracted tree

# 2) NuGet package + DLL
powershell -ExecutionPolicy Bypass -File tools/pack_nupkg.ps1
# -> dist/TokenVector.UI.<version>.nupkg
```

Consumers either unpack `.tkvpkg` and `__tkv_import__ = ["TokenVector.UI"]`, or reference the NuGet package (source under `tkv/`, optional `TokenVector.UI.dll`). Integration guide: `docs/INTEGRATION.md`.

## Known limitations

- **Cross-platform:** only Windows is production-ready today; X11/Cocoa are stubs (compiler pinvoke `.so` gap).
- **Text:** full HarfBuzz shaping needs `libharfbuzz.dll`; without it, shaped paths skip cleanly. Color emoji / non-BMP and hinting are not done.
- **GPU:** abstraction + probes exist; present path is still CPU/ULW (roadmap L4).
- **Cold start ~1.0 s:** .NET JIT + AV; NGEN/AOT is the planned lever (roadmap L3).
- **A11y:** model + bridges + tests ship, but NVDA does not yet read custom widgets (needs real UIA provider — L7).
- **Media:** H.264 Baseline via optional OpenH264 shim; Main/High + audio clock need FFmpeg/WASAPI (L6).
- **WinForms:** window-level interop is real; control-level APIs are still stubs (compiler gap).
- **Demos** launch with a console window (`tkvc`/`ilasm` CUI subsystem).
- **Before editing `.tkv`:** read `docs/TkvUI.Roadmap.md` §0 (compiler constraints: no `bool`, no bitwise ops, no nested attributes, records cannot contain `list`, list-append quirk D1, …).

## Documentation

| Doc | Purpose |
|---|---|
| `docs/LEVEL_PLAN.md` | L1–L10 leveling plan vs competitors |
| `docs/COMPETITORS.md` | Detailed competitor matrix (§9 = 25-category deep dive) |
| `docs/BENCH.md` | Normalized head-to-head benchmarks |
| `docs/API.md` | Module / function index |
| `docs/TkvUI.Roadmap.md` | v2/v3 roadmap + **§0 compiler constraints** |
| `docs/INTEGRATION.md` | How other apps import TkvUI |
| `docs/COMPILER_GAPS.md` | Known `tkvc` gaps and workarounds |
| `CHANGELOG.md` | Release history |
| `DEVELOPMENT_PLAN.md` | v3 plan toward broader parity |

## License

MIT — see [`LICENSE`](LICENSE).
