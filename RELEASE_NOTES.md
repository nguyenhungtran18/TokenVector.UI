# TokenVector.UI 1.0.0 — Release Notes

**Date:** 2026-09-24  
**License:** MIT  
**Channel:** first packaged public release (`.nupkg` + `TokenVector.UI.dll` + source `.tkv`)

---

## Headline

TokenVector.UI (TkvUI) **1.0.0** is a cross-platform UI toolkit written **100% in TokenVector (`.tkv`)** with **zero third-party runtime dependencies** (no Skia, SDL, WPF, or Qt). Rasterizer, fonts, layout, widgets, SQLite, PDF, and media codecs ship in one package and compile via `tkvc.exe` → CIL/.NET IL.

| Metric | Value (verified 2026-09-24) |
|---|---|
| Verify suite | **55 PASS / 0 FAIL / 2 SKIPPED** (`TKVUI_VERIFY_OK`) |
| Assertions | **~2200+** |
| Widget catalog | **93 constructors** (Widgets 42 + Native 41 + Media 10) |
| Native-look selftest | **255/255** |
| Text render | **9.4 ms / 21.6K chars** (~1.9× vs PyQt6 same workload) |
| Paint 1000 buttons | **~30 ms** (PyQt6 ≈ 43 ms) |
| SQL file round-trip 1000 rows | **~81 ms** (PyQt6 ≈ 195 ms, ~2.4×) |
| Built-in SQLite | **132/132** + crash matrix + kill-9 |
| Built-in PDF | **63/63** |
| Qt parity ports | `QtAppPort` **52/52**, `QtTreeDockPort` **31/31** |
| App size | ~549 KB–3.3 MB (depends on baked assets) |
| Idle memory | ~11 MB |

---

## What’s in the package

### Contents

- **`TokenVector.UI.dll`** — .NET assembly built from umbrella `TokenVector.UI.tkv` (entry `main` runs the full selftest suite).
- **Full `.tkv` sources** under `tkv/` — import with `__tkv_import__ = ["TokenVector.UI"]`.
- **`README.md`** (English) and **`README.vi.md`** (Tiếng Việt) — package readme.
- **`LICENSE`** (MIT), **`CHANGELOG.md`**, **`RELEASE_NOTES.md`**, **`tkvui.pkg.json`**.
- **`docs/`** — API index, roadmap (incl. compiler §0), integration guide, benchmarks, competitor matrix.
- **`tools/`** — `verify.sh`, `package.sh`.
- **`examples/`** — demos, benchmarks, Qt ports, fuzz, designer, clip player.

### Module map (library)

| Area | Modules |
|---|---|
| Core / render | `Core`, `Graphics`, `Text`, `Viet`, `I18nData`, `HarfBuzz`, `Effects`, `Theme` |
| Platform / input | `Platform`, `Events`, `Input`, `Layout`, `Clipboard`, `Ime` |
| Widgets | `Widgets` (42), `Widgets.Native` (41), `Media` (10), `NativeDlg` |
| Data / persist / print | `Data`, `SQLite`, `Printing` |
| Text advanced | `Bidi`, `Shaping`, `FontFallback`, `FontDiscovery`, `EmojiData` |
| Media codecs | `Video`, `Tkvv`, `Mjpg`, `Mp4` (+ bake data modules) |
| A11y / test | `A11y`, `A11yBridge`, `Uia`, `Atspi`, `KitTest` |
| GPU (abstraction) | `Gpu` |
| Optional | `Font` (GDI), `H264` (OpenH264 shim) |

---

## Highlights by area

### UI & widgets

- **93 distinct constructors** catalogued (`WIDGETS_BREADTH_OK` 15/15).
- **41 native-look widgets** post Wave B: dock float/tab, MDI `tile_horizontal`, ribbon, property grid, tree multi-select, context menu, …
- Flex/grid/stack layout **50/50**; focus, invalidation, frame scheduler, spring/tween.
- **10 media-player widgets** (transport, seek, volume, playlist, EQ, spectrum, A-B loop, …).

### Text & language

- 5×7 bitmap font + **134 Vietnamese precomposed glyphs**; sequence-aware UTF-8.
- Verified TTF parser/rasterizer; optional **HarfBuzz** wire (`text_atlas_draw_shaped`) with clean skip without DLL.
- Bidi UAX#9 **194/194**; complex shaping **91/91** (Arabic/Thai/Indic/Bengali/Tamil).
- **Telex/VNI IME** **37/37**; baked BMP emoji **12 symbols**.

### Persistence & documents

- Pure-`.tkv` **SQLite-compatible** engine: CRUD, JOIN, snapshot tx, dual-slot file, crash matrix, kill-9 — **132/132**.
- Pure-`.tkv` **PDF writer** + shell print — **63/63**.

### Media

- GIF **44/44**, MJPEG baseline **44/44** (~106 fps @ 160×120), HD 720p correct-pixel **6/6** (~2 fps software).
- Custom **TKVV** fast path **56/56** (~100 fps @ 720p software path).
- MP4 demux **62/62** (co64/ctts/elst/SPS).
- Optional H.264 Baseline via OpenH264 shim (skip when DLL missing).

### Platform & a11y

- **Win32 production** (ULW + DIB, multi-window); X11/Cocoa stubs (compiler `.so` pinvoke gap).
- A11y tree + UIA/AT-SPI host-driven providers; **KitTest 16/16**.
- NVDA: chrome controls readable; custom widgets still need a real UIA provider (roadmap L7).

### Qt parity (headless-proven)

- `QtAppPort` — Qt Application Example **52/52**.
- `QtTreeDockPort` — Qt Tree/Dock **31/31**.

---

## Benchmarks (vs PyQt6 / Qt 6.11 — `docs/BENCH.md`)

| Workload | TkvUI | PyQt6 | Ratio |
|---|---|---|---|
| Text 21.6K chars/block | **9.4 ms** | 13.7–18.1 ms | **~1.9× faster** |
| Construct 1000 buttons | **< 0.16 ms** | 12.6 ms | timer-floor win |
| Paint 1000 buttons | **~30 ms** | ~43 ms | **~1.4× faster** |
| CRUD in-memory total/rep | **~8 ms** | ~14 ms | **~1.8× faster** |
| SQL file RT 1000 rows | **~81 ms** | ~195 ms | **~2.4× faster** |
| Idle memory | **~11 MB** | 15.6 MB | smaller |
| Cold start | **~1.0 s** | ~0.2 s | slower (L3 / NGEN) |
| Load-text peak | ~46 MB | 15.6 MB | larger |

Slint / egui / Dear ImGui numbers are **not** re-measured on this machine — see `docs/COMPETITORS.md` §9.

---

## Install / consume

### NuGet

```bash
nuget push dist/TokenVector.UI.1.0.0.nupkg -ApiKey <KEY> -Source https://api.nuget.org/v3/index.json
```

```powershell
# From a .NET project that references the packaged assembly:
#   runtimes/any/native/TokenVector.UI.dll
# Source .tkv lives under tkv/ for tkvc consumers.
```

### Source package (`.tkvpkg`)

```bash
bash tools/package.sh --verify
# -> dist/TokenVector.UI-1.0.0.tkvpkg (+ .sha256)
```

### Import from any `.tkv` app

```text
__tkv_import__ = ["TokenVector.UI"]
```

See `docs/INTEGRATION.md`.

### Rebuild package locally

```powershell
powershell -ExecutionPolicy Bypass -File tools/pack_nupkg.ps1
# -> dist/TokenVector.UI.1.0.0.nupkg  (+ TokenVector.UI.dll under stage)
```

---

## Known limitations (honest scope)

1. **Windows-only production** — X11/Wayland/Cocoa stubs; Android/iOS host contracts only.
2. **Cold start ~1.0 s** — .NET JIT + AV; NGEN/AOT is roadmap L3.
3. **GPU** — abstraction + probes; present path still CPU/ULW (L4).
4. **A11y** — bridges + tests ship; NVDA silent on custom widgets until UIA provider (L7).
5. **H.264** — Baseline via optional OpenH264; Main/High + audio clock need FFmpeg/WASAPI (L6).
6. **HarfBuzz** — full shaped path requires `libharfbuzz.dll`; without it, clean skip.
7. **WinForms** — window-level real; control-level still stub (compiler gap).
8. **CI** — static workflow only; full suite runs on the dev machine via `tools/verify.sh`.

---

## Compatibility

| Requirement | |
|---|---|
| Compiler | `tkvc.exe` (TokenVector) — see `tkvui.pkg.json` `toolchain` |
| Runtime | .NET Framework 4.x (CLR) for the packaged DLL |
| OS (verified) | Windows x64 |
| License | MIT |

**Before editing `.tkv` sources:** read `docs/TkvUI.Roadmap.md` §0 (compiler constraints: no `bool`, no bitwise, no nested attributes, records cannot contain `list`, list-append quirk D1, …).

---

## Checksums & verify

After packaging:

```bash
# Source package
sha256sum dist/TokenVector.UI-1.0.0.tkvpkg

# Full suite (must be green before publish)
TKVC=/path/to/tkvc.exe bash tools/verify.sh
# expected: TKVUI_VERIFY_OK (55 PASS / 0 FAIL / 2 SKIPPED)
```

---

## Roadmap after 1.0.0

| Level | Goal |
|---|---|
| L3 | Cold-start: NGEN/AOT |
| L4 | GPU compute-blit present path |
| L5 | OS look polish (Win11 DPI + accent) |
| L6 | FFmpeg Main/High + WASAPI audio clock |
| L7 | NVDA via C# COM UIA shim |
| L8 | Linux X11 (`.so` pinvoke) |
| L9 | CI matrix (Ubuntu + Windows full verify) |
| L10 | Public repo + NuGet.org + external users |

Full plan: `docs/LEVEL_PLAN.md`.

---

## Credits

- **Author:** Nguyen Hung Tran  
- **Repository:** https://github.com/nguyenhungtran18/TokenVector  
- **License:** MIT — see `LICENSE`

---

*Numbers above are from the 2026-09-24 verify/bench run on the development machine. Re-run `tools/verify.sh` after any toolchain change.*
