# So s√°nh repo TokenVector.UI v·ªõi ƒë·ªëi th·ªß (2026-09-19 ‚Üí refresh 2026-09-24)

> Stars GitHub l·∫•y 2026-09-19, **tra l·∫°i 2026-09-24** (Slint/egui/ImGui ‚Äî s·∫Ω l·ªói th·ªùi, tra l·∫°i khi claim).
> M·ª•c ƒë√≠ch: ƒë·ªãnh v·ªã trung th·ª±c + r√∫t gap list. Kh√¥ng d√πng ƒë·ªÉ qu·∫£ng c√°o.
> **2026-09-24 (Wave A+B):** verify **55/0/2** (`TKVUI_VERIFY_OK`), catalog **93 constructors**,
> Qt ports: App 52/52 + Tree/Dock **31/31 `QTDOCK_OK`**, native **255/255**, breadth 15/15.
> Probe PyQt6 6.11.0 offscreen 9/9 (`tools/bench/func_pyqt_probe.py`) ‚Äî xem ¬ß2b.
> H.264 Baseline decodeÊâìÈÄö + HarfBuzz 14.5 + wire draw-path (L2) ‚Äî c·∫≠p nh·∫≠t ¬ß2/¬ß2b/¬ß8.

---

## 1. Headline

| | TokenVector.UI | PyQt6 | PySide6 | Slint | egui | Dear ImGui |
|---|---|---|---|---|---|---|
| Ng√¥n ng·ªØ | .tkv ‚Üí .NET IL | Python (binding Qt C++) | Python (binding Qt C++, official) | Rust/C++/JS/Python (.slint DSL) | Rust (immediate) | C++ (immediate) |
| License | MIT | GPL-3 / commercial | LGPL-3 / commercial | GPL-3 / commercial (royalty-free) | MIT/Apache-2.0 | MIT |
| Stars | (local, ch∆∞a public ‚Äî **0**) | PyPI dl ~M/th√°ng | PyPI dl ~M/th√°ng | **~23.7k** (2026-09-24) | **~30.5k** (2026-09-24) | **~76k** (2026-09-19) |
| Tu·ªïi / nh·ªãp | 2026-, **46 commits** d√†y, v2.9.0 | t·ª´ 1998, release ƒë·ªÅu | official Qt Co, release ƒë·ªÅu | 2020-, active | 2019-, active | 2014-, active |
| Repo size | **94 file `.tkv`** (~4.2 MB repo tracked) | binding + Qt binary | = PyQt6 | monorepo l·ªõn | crates | single-header + examples |
| Widget | **93 constructors** (Widgets 42 + Native 41 + Media 10; Wave A +10 form-control, Wave B +Dock float/tab/MDI tile/Ribbon/PropGrid/Tree multi/ContextMenu) | **~1000 classes Qt** | = PyQt6 | default set + Material/Fluent/Cupertino/Native | ~30 + custom d·ªÖ | ~60, tool-oriented |
| Test | **verify 55/0/2** headless (~2200+ checks) + LOCALS_OK | pytest/offscreen | = PyQt | GUI automation | **kittest** (a11y-tree) | manual/examples |

---

## 2. So theo t·ª´ng m·∫∑t (b·∫±ng ch·ª©ng ‚Äî refresh 2026-09-24)

| M·∫∑t | TkvUI (ƒëo th·∫≠t) | ƒê·ªëi th·ªß t·ªët nh·∫•t | K·∫øt lu·∫≠n |
|---|---|---|---|
| Binary/deploy | suite **1644 KB** (32+ module), app **549 KB**‚Äì3.3 MB single EXE (c·∫ßn .NET FW); NuGet + `.tkvpkg` | Slint (MCU < 300 KiB RAM, wasm); egui wasm g·ªçn; **PyQt PyInstaller 50 MB+** | **Th·∫Øng PyQt deploy**; thua Slint ƒëa n·ªÅn/embedded |
| Startup/RAM | cold-spawn **~1.0 s** (AV+CLR); idle peak **11.0 MB** (trivial) / **~46 MB** (bench text load) | PyQt cold **~0.2 s**, QApp idle **15.6 MB** / load text **15.6 MB** | ‚ö†Ô∏è Thua cold-start c√≥ AV; **th·∫Øng idle**, **thua load-text ~3√ó** |
| Text/shaping | atlas **9.4 ms/rep** (th·∫Øng PyQt6 18.1 ms, **1.9√ó**); engine thu·∫ßn (Arabic/Thai/Deva/‚Ä¶); **HarfBuzz 14.5ÊâìÈÄö + wire draw-path (L2 2026-09-24)** optional `libharfbuzz.dll` | Qt (HarfBuzz/full) | **Th·∫Øng ASCII 1.9√ó**; HB wire thu h·∫πp complex-script ‚Äî thi·∫øu dll ‚Üí fallback engine c≈© |
| Widgets | **93 constructors** (Wave A +10 form, Wave B +Dock float/tab + MDI tile_h + Ribbon + PropGrid + Tree multi-sel + ContextMenu) + wizard/color/font/statusbar/checkbox‚Ä¶ + item-view + stylesheet | Qt ~1000 classes | **Thua s·ªë l∆∞·ª£ng**; Wave A+B ƒë√≥ng gap app CRUD/IDE-ish; ƒë·ªß CRUD/form/desktop admin |
| SQL persistence | **Binary page 4KB + B-tree + WAL-lite + multi-WHERE + JOIN** 132/132 + kill-9 12 cycle; round-trip 1000 rows **~81 ms** | Kh√¥ng ai built-in; QSQLITE **~195 ms** | **Th·∫Øng niche + 2.4√ó** |
| H.264 decode | **Baseline decodeÊâìÈÄö** (C# shim + OpenH264, 8/8 + round-trip 11/12) | QtMultimedia/ffmpeg (full) | Thua breadth; th·∫Øng built-in nh·ªè |
| PDF/print | PDF writer 63/63 + **shell-print th·∫≠t** (ShellExecuteA live) | Kh√¥ng ai built-in | **Th·∫Øng niche** |
| Accessibility | Data model + Win32 HWND mirror + JSON + **KitTest 16/16**; NVDA: chrome ƒë·ªçc ƒë∆∞·ª£c, widget custom **0 utterance** (Phase 9.1) | Qt native UIA; Slint/egui **AccessKit** | ‚ö†Ô∏è Partial ‚Äî COM bridge c·∫ßn C# shim / AccessKit path |
| GPU | abstraction + shader pipeline **stubs** | Qt RHI; egui wgpu | **Thua** (c·∫ßn host GPU th·∫≠t) |
| WASM | **WASI interp ch·∫°y th·∫≠t** (wasmtime DATA_OK) + browser canvas; AOT closed upstream | Slint/egui wasm production | Partial (h√≤a Pyodide-tier) |
| CI | `.github/workflows/ci.yml` **static-only** + issue templates √ó3 + LOCALS_OK | Slint GUI e2e; egui **kittest** | Thua GUI-e2e; c√≥ unit+static gate |
| Cross-plat | Win32 th·∫≠t; **X11/Cocoa stub**; Android/iOS host contract (verify SKIP) | Qt/Slint/egui multi-OS | **Thua** (L8 blocker R7 `.so`) |
| OS look | self-drawn theme Win light/dark/HC (**41 native widgets** after Wave B) | Qt native style / Fluent | ‚ö†Ô∏è Partial (L5) |
| C·ªông ƒë·ªìng | **0 star / 0 issue** (local, 46 commits) | Qt Company; Slint/egui/ImGui **23k‚Äì76k stars** | **Thua** (L10 ‚Äî c·∫ßn public repo) |

---

## 2b. Ma tr·∫≠n parity ch·ª©c nƒÉng (refresh 2026-09-24)

B·∫±ng ch·ª©ng TkvUI = verify **55/0/2** (`TKVUI_VERIFY_OK`); PyQt6 = probe offscreen **9/9**
(`tools/bench/func_pyqt_probe.py`, PyQt 6.11.0/Qt 6.11.2). Modal-exec / playback th·∫≠t
kh√¥ng offscreen ‚Üí ghi nh·∫≠n, kh√¥ng claim.

| Ch·ª©c nƒÉng | TkvUI (b·∫±ng ch·ª©ng) | PyQt6 (probe) | K·∫øt lu·∫≠n |
|---|---|---|---|
| App assembly | **QtAppPort 52/52** (menus/toolbar/statusbar/RichEdit/dialogs/print/recent) | `mainwin.app` PASS | Parity app chu·∫©n |
| Dock/MDI/IDE layout | **QtTreeDockPort 31/31** (dock float/tab + tree multi-sel + MDI tile_h + menubar View) | QMainWindow dock s·∫µn | **Parity coverage** (Wave B 2026-09-24); Qt v·∫´n richer (z-order, save/restore) |
| Widgets render | **93 constructors**; native 255/255 + widgets 167/167 + breadth 15/15 | `widgets.render17` PASS (17) | ƒê·ªß CRUD/form; Qt th·∫Øng breadth + style native |
| Dialogs | NativeDialog + DlgFile/Color/Font (**NATIVEDLG 39/39**) | `dialogs.instantiate6` PASS | Parity instantiate |
| Text Vi·ªát/bidi | 134 glyph precomposed + HB 14.5 **wire draw-path (L2)**; Bidi **194/194** | `text.vi-bidi` PASS | Qt th·∫Øng full khi thi·∫øu dll; TkvUI th·∫Øng ASCII 1.9√ó |
| SQL | **132/132** + kill-9 + round-trip **2.4√ó** | `sql.crud` PASS + filebench 195 ms | TkvUI th·∫Øng niche |
| PDF/print | PDF **63/63** + shell-print th·∫≠t | `print.pdf` PASS | Parity PDF; TkvUI shell-print; Qt print engine |
| Clipboard | Win32 th·∫≠t **12/12** | `clipboard.roundtrip` PASS | TkvUI Windows; Qt cross-plat |
| Item-view | Data proxy/sort/filter **76/76** + SqlTableModel | `itemview.proxy` PASS | Parity c∆° b·∫£n |
| Media | GIF/MJPEG/TKVV + MP4 **62/62** + VideoDemo **21/21** + ClipPlayer **14/14** + **H.264 Baseline 8/8** | `media.setsource` PASS + QtMultimedia full | Thu h·∫πp; Qt th·∫Øng playback + Main/High |
| a11y | HWND mirror + JSON + KitTest **16/16**; NVDA partial | native UIA | Qt th·∫Øng native |
| GPU/WASM | stubs; WASI interp + canvas | Qt RHI; production wasm | Thua GPU; h√≤a WASM tier |

---

## 3. Ph√°t hi·ªán chi·∫øn l∆∞·ª£c: AccessKit

- Slint + egui (+ Bevy, Freya, Xilem) **kh√¥ng t·ª± implement UIA/AT-SPI/NSAccessibility** ‚Äî h·ªç d√πng chung **AccessKit** (abstraction c√¢y a11y + adapter Windows/macOS/Unix-DBus/Android/iOS, c√≥ **C v√† Python bindings**).
- egui b·∫≠t AccessKit m·∫∑c ƒë·ªãnh trong eframe; test qua `egui_kittest` query ƒë√∫ng c√¢y m√† screen reader ƒë·ªçc ‚Äî m√¥ h√¨nh test m√† bridge c·ªßa ta n√™n copy.
- ImGui l√† b·∫±ng ch·ª©ng ng∆∞·ª£c: kh√¥ng a11y ‚Üí blind user b√°o "blank window" (gi·ªëng h·ªát k·∫øt qu·∫£ NVDA c·ªßa ta).
- **Cho Phase 9.2**: m·ª•c ti√™u ƒë√∫ng kh√¥ng ph·∫£i "vi·∫øt COM vtable tay" m√† l√† **b·∫Øn t·ªõi AccessKit C bindings** ‚Äî v·∫´n c·∫ßn `.so/.dll` pinvoke + marshal struct (ƒëang blocked), nh∆∞ng l√† ƒë∆∞·ªùng ƒë√£ c√≥ ng∆∞·ªùi ƒëi, c√≥ test pattern (kittest) ƒë·ªÉ h·ªçc.

---

## 4. Gap list c·ªßa repo (x·∫øp theo r·∫ª ‚Üí ƒë·∫Øt)

| # | Task | Effort | Status |
|---|---|---|---|
| 1 | **CONTRIBUTING.md + issue/PR templates** | R·∫ª (1 bu·ªïi) | ‚úÖ DONE (`CONTRIBUTING.md` + `.github/ISSUE_TEMPLATE` √ó3) |
| 2 | **API reference index** | V·ª´a | ‚úÖ DONE (`docs/API.md` ‚Äî Native 50 fn / Widgets 64 fn, refresh Wave B) |
| 3 | **Screenshots/GIF trong README** | R·∫ª | ‚úÖ DONE (`docs/img/shot_browser.png` + `shot_emoji.png`) |
| 4 | **Badges + releases c√≥ changelog theo tag** | R·∫ª | ‚úÖ DONE (`CHANGELOG.md`, NuGet nuspec, `.tkvpkg`) |
| 5 | **kittest-style test** | V·ª´a | ‚úÖ DONE (`TkvUI.KitTest` 16/16) |
| 6 | **Benchmark suite 1 l·ªánh** | V·ª´a | ‚úÖ DONE (`tools/bench_all.sh` / `.ps1` + `bench_stable`) |
| 7 | **Vietnamese-first + PDF/SQL built-in** ‚Üí README ƒë·∫ßu | R·∫ª | ‚úÖ DONE |
| 8 | **L1 Wave A widget breadth 43‚Üí88** | L | ‚úÖ DONE 2026-09-24 (`3cc205d`) |
| 9 | **L1 Wave B structural + Qt Tree/Dock port** | M | ‚úÖ DONE 2026-09-24 (`d70326e`, QTDOCK 31/31) |
| 10 | **L2 wire HarfBuzz draw path** | M | ‚úÖ DONE 2026-09-24 (`3cc18d0`, leaf + lazy-bake) |
| 11 | **CI matrix Win+Ubuntu (L9)** | M | ‚è≥ `ci.yml` static-only ‚Äî c√≤n ch·∫°y suite tr√™n Ubuntu |
| 12 | **Public repo + first external user (L10)** | S‚ÄìM | ‚è≥ blocker marketing/release |

---

## 5. Roadmap Phase 11-12 (Text/Tooling)

| Phase | Task | Status | Blocker |
|---|---|---|---|
| **11.1 Font Fallback** | ‚úÖ DONE (26/26 PASS) | ‚Äî |
| **11.2 Complex Script** | üü° CoreÊâìÈÄö (HarfBuzz 14.5 pinvoke, Bidi 194/194) ‚Äî c√≤n: wire draw path + atlas lazy-bake HB gids | thi·∫øu leaf module + atlas design |
| **11.3 TTF Embed PDF** | üî¥ BLOCKED (byte array) | tkvc gap |
| **11.4 Fuzz Shaping** | ‚úÖ DONE (FUZZ_OK 7/7) | ‚Äî |
| **12.1 DesignerApp** | ‚úÖ DONE (headless + windowed) | ‚Äî |
| **12.2 Tutorial** | ‚úÖ DONE | ‚Äî |
| **12.3 CI Matrix** | ‚è≥ Pending | GitHub Actions matrix |
| **12.4 Fuzz** | ‚úÖ DONE (FUZZ_OK) | ‚Äî |

---

## 7. Th·ª© t·ª± ∆∞u ti√™n ƒë·ªÅ xu·∫•t

1. **Font fallback m·ªü r·ªông** (emoji, color font, variable font) ‚Äî niche value cao
2. **Wire HarfBuzz v√†o draw path** (leaf `TkvUI.HarfBuzz` + atlas lazy-bake HB gids ‚Äî coreÊâìÈÄö2026-09-23)
3. **12.3 CI Matrix** ‚Äî CI matrix Win+Ubuntu+WASM
4. **docs/COMPETITORS.md finalize** ‚Äî Gap list c·∫≠p nh·∫≠t
5. **Emoji/Color font support** (11.1 extension)

---

## 8. T√≥m t·∫Øt v·ªã th·∫ø (Reality Check ‚Äî 2026-09-24)

| Ti√™u ch√≠ | PyQt6 | TokenVector.UI | K·∫øt lu·∫≠n |
|---|---|---|---|
| Binary size | 15‚Äì20 MB (PyInstaller 50 MB+) | **1644 KB** suite / app **549 KB** | ‚úÖ Th·∫Øng |
| Cold startup | **~0.2 s** | **~1.0 s** (AV+CLR) | ‚ö†Ô∏è Thua (L3) |
| Memory idle | 15.6 MB | **11.0 MB** | ‚úÖ Th·∫Øng |
| Memory load-text | **15.6 MB** | ~46 MB | ‚ùå Thua ~3√ó (pixel i64 + CLR; i32 ho√£n) |
| Text render | ~18.1 ms/rep | **9.4 ms** | ‚úÖ Th·∫Øng 1.9√ó |
| Widget construct | ~12.6 ms/1000 | **<0.16 ms** | ‚úÖ Th·∫Øng |
| Widget render | ~43 ms/1000 | **~30 ms** | ‚úÖ Th·∫Øng 1.4√ó |
| Widget breadth | **~1000 classes** | **93 constructors** | ‚ùå Thua (Wave A+B +16; c√≤n Wave C) |
| CRUD engine in-mem | ~14 ms/rep | **~8 ms** | ‚úÖ Th·∫Øng 1.8√ó |
| SQL file round-trip | 195 ms/1000 rows | **81 ms** | ‚úÖ Th·∫Øng 2.4√ó |
| App port | (g·ªëc Qt) | **QtApp 52/52 + QtTreeDock 31/31** | ‚úÖ Parity (2 ports) |
| Media | full profile + playback | **Baseline H.264 8/8** + TKVV realtime | ‚ö†Ô∏è Niche thu h·∫πp |
| WASM | Pyodide interp | **WASI interp + canvas** | ‚ö†Ô∏è H√≤a tier |
| OS look | native | self-drawn **41 native** | ‚ö†Ô∏è Partial (L5) |
| Cross-plat | full | **Win32 th·∫≠t, X11/Cocoa stub** | ‚ùå Thua (L8) |
| A11y | native UIA | **HWND mirror + KitTest** | ‚ö†Ô∏è Partial (L7) |
| GPU | RHI | stubs | ‚ùå Thua (L4) |
| Ecosystem | massive | **0 star** | ‚ùå Thua (L10) |
| Verify | pytest/offscreen | **55/0/2** + LOCALS_OK | ‚úÖ Unit headless v·ªØng |

**Scorecard nhanh vs 6 ƒë·ªëi th·ªß:**

| | Th·∫Øng | H√≤a | Thua |
|---|---|---|---|
| **vs PyQt6/PySide6** | binary, idle-mem, text 1.9√ó, widget speed, SQL 2.4√ó, PDF/print built-in, clipboard Win, app-port parity, H.264 niche | WASM tier, item-view, dialogs | **breadth ~10√ó**, cold-start, GPU, OS native, cross-plat, ecosystem, a11y native, load-mem |
| **vs Slint** | built-in SQL/PDF/print/media niche | a11y path (c√πng ch∆∞a full) | **stars, embedded/MCU, wasm prod, DSL tooling, cross-plat, CI e2e** |
| **vs egui** | SQL/PDF/print built-in, retained-mode widgets (93) | WASM | **wgpu GPU, stars, kittest, ecosystem, cross-plat** |
| **vs Dear ImGui** | a11y model (ImGui = 0), SQL/PDF, form widgets | speed ballpark | **tooling ecosystem, immediate-mode perf culture, 76k stars, renderer-agnostic** |

**K·∫øt lu·∫≠n (2026-09-24, sau Wave A+B + L2 HB wire):** TokenVector.UI **th·∫Øng PyQt6** ·ªü
binary size, idle memory, text render 1.9√ó, widget create/render, SQL round-trip 2.4√ó,
SQL/PDF/print built-in, clipboard Windows, **app-port parity 2 example**, H.264 Baseline +
HarfBuzz wire ‚Äî **thua** widget breadth (93 vs ~1000), cold-start c√≥ AV, GPU, OS look native,
cross-plat (X11/Cocoa stub), ecosystem (0 star), media full-profile, load-text memory.
Compiler: R1‚ÄìR6/R9/R10/R12 ƒë√£ m·ªü; c√≤n ƒë√≥ng struct l·ªìng/fixed-array, COM call-in, R7 Linux.
Kh√¥ng claim "ƒë√°nh b·∫°i PyQt6 m·ªçi m·∫∑t" ‚Äî **th·∫Øng niche** (deploy, Vietnamese-first, text, persistence, decode nh·ªè)
v√† **ƒë√£ ƒë√≥ng 2 gap l·ªõn L1 (Wave A+B) + L2 (HB wire)** trong 2026-09-24.

---

## üìã Next Steps (Theo th·ª© t·ª± ∆∞u ti√™n ‚Äî 2026-09-24)

1. **L3 cold-start** ‚Äî ƒëo warm/m√°y s·∫°ch + ƒë·∫©y NGEN/AOT (upstream R10)
2. **L9 CI matrix** ‚Äî ch·∫°y suite headless tr√™n Ubuntu (R7 `.so` l√† blocker)
3. **L5 OS look** ‚Äî theme Win11 DPI+accent polish tr√™n 41 native widgets
4. **L7 A11y** ‚Äî C# COM shim / AccessKit path ƒë·ªÉ NVDA ƒë·ªçc widget
5. **L10 public** ‚Äî push repo + NuGet.org + 1 external user
6. **Emoji color / non-BMP** (11.1 extension) ‚Äî partial 12 BMP symbols
7. **L4 GPU compute-blit** tr∆∞·ªõc full render; **L6 FFmpeg Main/High**

---

> **L∆∞u √Ω:** File n√†y ch·ªâ d√πng ƒë·ªÉ tracking internal. Kh√¥ng d√πng ƒë·ªÉ marketing/public claim n·∫øu ch∆∞a verify l·∫°i s·ªë li·ªáu.
---

## 9. –?i chi?u chi ti?t t?ng m?c (2026-09-24 ó khÙng tÛm t?t)

> M?i m?c: **d?nh nghia ? TkvUI l‡m gÏ (b?ng ch?ng s?) ? t?ng d?i th? ? verdict ? gap cÚn l?i**.
> S? TkvUI l?y t? `tools/verify.sh` l?n cu?i **55/0/2** (2026-09-24), selftest in-log, `docs/BENCH.md`.
> S? PyQt6 l?y bench chu?n ho· 2026-09-19/20 + probe `func_pyqt_probe.py` 9/9.
> S? Slint/egui/ImGui: docs cÙng khai + GitHub 2026-09-24 ó **khÙng do runtime trÍn m·y n‡y** (khÙng c‡i) ? ghi "chua do".

### 9.1 NgÙn ng?, runtime, mÙ hÏnh

| H?ng m?c | TokenVector.UI | PyQt6 / PySide6 | Slint | egui | Dear ImGui |
|---|---|---|---|---|---|
| NgÙn ng? vi?t app | **`.tkv`** (TokenVector dialect) ? `tkvc` ? **CIL/.NET IL** ? `.exe` | **Python 3** + binding sang Qt C++ | **`.slint` markup** + logic Rust/C++/JS/Python | **Rust** | **C++** |
| Runtime khi ch?y | **CLR / .NET Framework 4.x** (JIT; NGEN chua b?t) | CPython + Qt DLL (~15ñ20 MB+) | Native (Rust/C++ compiled) | Native (Rust) | Native (C++) |
| MÙ hÏnh retained/immediate | **Retained** (UIElement tree, invalidation, frame scheduler) | **Retained** (QObject widget tree) | **Retained** (declared scene) | **Immediate** (v? l?i m?i frame) | **Immediate** (v? l?i m?i frame) |
| Zero native dep bÍn ngo‡i | **CÛ** ó raster/font/layout/widget t? vi?t; optional: `libharfbuzz.dll`, OpenH264 shim C# | **KhÙng** ó ship Qt DLL + Python | link stack Slint/winit/femtovg | winit/wgpu/glow | user ch?n backend (GL/DX/Vulkan) |
| Compiler/linter riÍng | **CÛ** ó `tkvc` + r‡ng bu?c Roadmap ß0 (c?m bitwise cu, ternary, `pass`, list-append quirk D1Ö) | KhÙng (CPython runtime) | rustc + slint compiler | rustc | cmake/MSVC |

**Verdict:**
- **–?c nh?t:** TkvUI l‡ framework **100% m?t ngÙn ng? t?-host** (UI+raster+SQL+PDF+codec d?u `.tkv`) ó PyQt ph? thu?c Python+Qt, Slint/egui/ImGui l‡ binding/wrapper quanh h? sinh th·i cÛ s?n.
- **Thua DX/IDE:** khÙng cÛ Language Server, IntelliSense, hot-reload nhu Slint Live Preview hay Python REPL.
- **Risk:** compiler `.tkv` cÚn gap (struct l?ng, COM-in, ternary, `.so`) ? blocker L7/L8.

---

### 9.2 License & ph‚n ph?i thuong m?i

| | TokenVector.UI | PyQt6 | PySide6 | Slint | egui | Dear ImGui |
|---|---|---|---|---|---|---|
| License code | **MIT** | **GPL-3** ho?c **commercial** | **LGPL-3** ho?c commercial | **GPL-3** ho?c **royalty-free** (desktop) / commercial (embedded) | **MIT / Apache-2.0** | **MIT** |
| App proprietary d˘ng free? | **CÛ (MIT)** | Ch? paid commercial | **CÛ (LGPL)** v?i di?u ki?n dynamic link | Desktop free qua royalty-free; **embedded thu?ng c?n commercial** | **CÛ** | **CÛ** |
| Patent/codec di kËm | OpenH264 **t?i binary Cisco** (BSD-2 + Cisco tr? MPEG-LA); **c?m x264 GPL** | Qt modules t˘y | = | khÙng ship codec | khÙng | khÙng |

**Verdict:** TkvUI **c˘ng h?ng freedom v?i egui/ImGui** (MIT), **nh? hon PyQt GPL**, **linh ho?t hon Slint embedded**. –i?m b·n h‡ng enterprise nh?: khÙng ph?i tr? Qt commercial license.

---

### 9.3 C?ng d?ng, tu?i d?i, nh?p ph·t tri?n

| | TokenVector.UI | PyQt6/PySide6 | Slint | egui | Dear ImGui |
|---|---|---|---|---|---|
| Tu?i | **~1 nam** (2026-, **46 commits** local) | Qt t? **1998**; binding Python l‚u d?i | **2020ñ** | **2019ñ** | **2014ñ** |
| Stars (tra 2026-09-24) | **0** (chua public) | PyPI download ~M/th·ng (khÙng stars repo) | **~23.7k** | **~30.5k** | **~76k** (2026-09-19) |
| Contributors | 1 (local) | Qt Company + c?ng d?ng l?n | **276** (Slint) | h‡ng tram | **583** (OpenHub) |
| Open issues s?ng | 0 | h‡ng nghÏn across Qt | ~700+ | ~900+ | h‡ng nghÏn PR/issue |
| Release cadence | v2.9.0, commit d‡y daily local | Qt 2◊/nam | 57 releases, 1.17.x | release d?u (0.36.x) | release d?u |
| Docs/tutorial | README + `docs/*` + `TUTORIAL_CRUD` + screenshots | official.qt.io r?t d‡y | slint.dev + book | egui.rs + book | ossus docs + demos |

**Verdict: THUA n?ng (L10).** KhÙng cÛ external user = khÙng cÛ bug report th?t, khÙng cÛ trust signal. **Vi?c c?n l‡m:** public repo + topics + NuGet.org + 3 GIF live.

---

### 9.4 Widget breadth ó li?t kÍ chi ti?t theo nhÛm

**TkvUI catalog = 93 constructors distinct** (d?m `widget_constructor_catalog()` trong umbrella; Widgets 42 + Native 41 + Media 10).

#### 9.4.1 NhÛm form / input (d?i chi?u Qt)

| TkvUI (constructor) | PyQt6 class tuong duong | Ch?t lu?ng TkvUI | Verdict |
|---|---|---|---|
| `make_native_button` / `_default` / `make_button` / `make_button_outline` | `QPushButton` / `QToolButton` | hover/press/disabled/default ring, hit-test | **–?** |
| `make_native_check` + `make_native_checkbox` / `make_native_tristate` | `QCheckBox` (tristate) | 2-state + tri-state | **–?** |
| `make_native_radio` + group | `QRadioButton` + `QButtonGroup` | group id field | **–?** |
| `make_native_lineedit` / `make_native_password` / `make_textinput` | `QLineEdit` (+EchoMode) | placeholder, mask password `*` | **–?** (chua validator regex d?y d? nhu Qt) |
| `make_textfield` | `QLineEdit` style variant | | OK |
| `make_native_combo` | `QComboBox` | popup list, open/close | **–?** (chua editable combo) |
| `make_native_treecombo` | `QComboBox` with TreeView | combo + tree popup | **CÛ** ó Qt cÛ nhung Ìt app d˘ng |
| `make_native_spinbox` | `QSpinBox` | min/max/step | **–?** (chua QDateTimeSpinBox) |
| `make_native_slider` / `make_slider` | `QSlider` | value, groove | **–?** |
| `make_dial` | `QDial` | ±135∞ arc | **CÛ** (Wave A) |
| `make_native_scrollbar` / `make_scrollbar` | `QScrollBar` | orient, page/step | **–?** |
| `make_switch` | `QCheckBox` styled / Material Switch | toggle anim | **CÛ** |
| `make_key_sequence` | `QKeySequenceEdit` | chord Ctrl/Alt/Shift/Meta | **CÛ** (Wave A) |
| `make_native_password` | QLineEdit Password | | OK |

**Thi?u vs Qt (khÙng cÛ trong 93):** `QTextEdit` full rich (cÛ `NativeRichEdit` nhung limited), `QPlainTextEdit` riÍng, `QComboBox` editable+completer, `QDateTimeEdit` full calendar popup variants, `QTimeEdit`, `QDoubleSpinBox` riÍng, `QCommandLinkButton` ? **d„ cÛ** `make_command_link`, `QKeySequenceEdit` ? **d„ cÛ**.

#### 9.4.2 NhÛm display / feedback

| TkvUI | PyQt6 | Verdict |
|---|---|---|
| `make_native_progress` / `make_progress` | `QProgressBar` | –? |
| `make_native_tooltip` | `QToolTip` | –? (state machine show/hide) |
| `make_toast` | khÙng core (c˘ng lib snack) | **TkvUI cÛ s?n** |
| `make_lcd` (7-seg) | `QLCDNumber` | **CÛ** (Wave A) |
| `make_metric_ring` / `make_sparkline` / Ant chart | `QChart` (module riÍng) | TkvUI bundle; Qt c?n QtCharts license/module |
| `make_ant_badge` / `dot` / `tag` / `avatar` | khÙng core Ant | **Niche design-system** |
| `make_native_statusbar` | `QStatusBar` | –? (part labels) |
| `make_tour_tip` | `QTour` (k? t? Qt 6.8, module) | **CÛ** ó parity m?i hon nhi?u b?n Qt cu |

#### 9.4.3 NhÛm container / navigation

| TkvUI | PyQt6 | Wave | Verdict |
|---|---|---|---|
| `make_native_tabs` / `_closable` / `make_tabs` | `QTabBar`/`QTabWidget` | pre | –? (chua movable tabs) |
| `make_toolbox` | `QToolBox` | A | **–?** |
| `make_stacked` | `QStackedWidget` | A | **–?** |
| `make_split_view` / `make_native_splitter` | `QSplitter` | pre | –? (ratio + orient) |
| `make_card` / `notch` | Frame + layout | pre | OK |
| `make_bottom_sheet` | khÙng core | pre | Mobile-ish niche |
| `make_navbar` | `QMenuBar` kh·c | pre | Mobile navbar |
| `make_dialog` / `make_native_dialog` / `buttons` | `QDialog`+`QMessageBox` | pre | Modal-exec **khÙng headless test** |
| `make_native_dock` / `make_native_dock_float` | `QDockWidget` | **B** | **CÛ float+tab+gutter** ó thi?u save/restore geometry, floating MDI children z-order nhu Qt |
| `make_native_mdi` + `tile_horizontal` | `QMdiArea` cascade/tile | **B** | **CÛ tile_h** ó thi?u tile_grid, cascade offset, maximize |
| `make_native_ribbon` | `QCommandBar`/QML ribbon / 3rd party | **B** | **CÛ** group tabs + large/small ó thi?u gallery, contextual tabs |
| `make_native_propgrid` | Qt Property Browser (examples) / 3rd party | **B** | **CÛ** 2-col + category collapse + edit ó thi?u multi-line, custom editors, sorting |
| `make_native_wizard` | `QWizard` | pre/A | linear next/back/cancel ó thi?u watermark, registerPage graph |
| `make_native_groupbox` / `groupcheck` | `QGroupBox` checkable | pre | –? |

#### 9.4.4 Item-view / model

| TkvUI | PyQt6 | Verdict |
|---|---|---|
| `make_native_table` + `TkvUI.Data` MvTable + proxy sort/filter | `QTableView`+`QSortFilterProxyModel` | **–? CRUD** (76/76) |
| `make_native_tree` / `make_native_tree_multi` (expand, ctrl/shift multi, anchor range) | `QTreeView`/`QTreeWidget` | **Wave B** ó multi-sel parity policy; thi?u drag-drop, header sections resize, editing delegates trÍn cell |
| `make_native_listview` / `make_listview` | `QListView` | virtualized-ish (item_h ◊ count) |
| SqlTableModel | `QSqlTableModel` | TkvUI built-in vs Qt sql module |

#### 9.4.5 Menu / chrome app

| TkvUI | PyQt6 | Verdict |
|---|---|---|
| `make_native_menubar` | `QMenuBar` | open menu, hit item ó **QtAppPort 52/52** |
| `make_native_toolbar` | `QToolBar` | –? |
| `make_native_contextmenu` | `QMenu` popup | **Wave B** items+separators+activate ó thi?u icons, shortcut labels, submenu |
| `make_native_systray` | `QSystemTrayIcon` | cÛ factory ó Win32 `Shell_NotifyIcon` m?c wrapper |
| `make_native_richedit` | `QTextEdit`/`QTextDocument` | limited rich (bold/basic) ó **thua xa** Qt rich text engine |
| `make_native_colorpicker` | `QColorDialog` | picker widget ó dialog qua NativeDlg |
| `make_native_fontpicker` | `QFontDialog` | list fonts + preview |
| `make_native_calendar` / `make_calendar` | `QCalendarWidget` | Gregorian Zeller, hit-day |
| `make_datetime_edit` | `QDateTimeEdit` | format vi-VN + calendar popup |

#### 9.4.6 Media widgets (10)

| TkvUI | PyQt6 QtMultimedia |
|---|---|
| Transport, SeekBar, Volume, Repeat, Shuffle, Speed, Playlist, Equalizer(10-band), Spectrum, ABLoop | `QMediaPlayer`+`QAudioOutput`+widgets Ìt (d˘ng QML/custom nhi?u) |

**Verdict media widgets:** TkvUI **bundle UI player d?y d? 10 widget** (Media selftest 80/80); Qt **engine m?nh hon** (codec, HW accel) nhung **UI player khÙng s?n** nhu v?y. HÚa ìUI formî, thua ìdecode/playbackî.

#### T?ng breadth

| | Qt | TkvUI | T? l? |
|---|---|---|---|
| Classes/constructors rough | **~1000** | **93** | **~9%** |
| –? app CRUD/admin/IDE-ish form | 100% | **d? core + Wave B dock/MDI/tree/ribbon/propgrid** | coverage ~**70ñ80% use-case** (u?c lu?ng theo Qt Application Example + Tree/Dock example ported) |
| Chua cÛ n?i b?t | ó | Chart full, WebView, QGraphicsView, QML, Quick3D, DataViz, SerialPort, Network widgets, PrintPreview widget d?y d? | |

**KhÙng claim parity 1:1** (d„ ch?t trong LEVEL_PLAN).

---

### 9.5 Text render & shaping (chi ti?t)

| H?ng m?c | TokenVector.UI | PyQt6 (Qt text) | Slint | egui | ImGui |
|---|---|---|---|---|---|
| Ki?u font | Bitmap 5◊7 ASCII + **134 Vi?t precomposed** + TTF parser/raster + i18n baked (Hebrew/Arabic/CJK) + emoji 12 BMP | System fonts full (QFont) | fontdue/parley (full OTF) | fontdue/ab_glyph | stb_truetype / freetype user |
| Atlas | Pre-baked + lazy-bake gid (HB wire L2) | glyph cache h? th?ng | GPU/atlas | texture atlas | dynamic |
| **–o ASCII 21.6K chars** | **9.4 ms** (atlas blit, GetTickCount) | **13.7ñ18.1 ms** `QPainter.drawText` | chua do | chua do | chua do |
| Speedup | **1.9◊ nhanh hon PyQt** (bench chu?n ho·) | baseline | ó | ó | ó |
| Shaping engine thu?n | Arabic/Thai/Deva/Bengali/Tamil **91/91** | subset | shaper riÍng | limited | limited |
| **HarfBuzz** | **14.5 optional DLL** + **wire draw path `text_atlas_draw_shaped` (L2 DONE 2026-09-24)**; thi?u DLL ? fallback engine cu skip-s?ch 157/157 | **Qt built HarfBuzz always on** | via rustybuzz/harfbuzz crate | rustybuzz optional | user |
| Bidi UAX#9 | **194/194** visual reorder | cÛ | cÛ | partial | partial |
| GSUB/GPOS d?y d? | qua HB khi cÛ DLL; fallback **khÙng full** | full | full HB | HB crate | khÙng |
| Wrap/ellipsis/align | cÛ (theo t? + ellipsis) | full (QTextLayout) | full | basic | basic |
| Rich text | Limited RichEdit | **QTextDocument** full HTML subset | TextEdit limited | markdown optional | markdown optional |
| Vietnamese-first | **134 glyph precomposed + Telex/VNI IME 37/37** | ph? thu?c font system + input method OS | khÙng special | khÙng | khÙng |

**Verdict chi ti?t:**
- **Th?ng t?c d? ASCII** (9.4 vs 18.1 ms) ó do l?i du?c, gi? trong BENCH.
- **Th?ng niche Vi?t** (precomposed bitmap khÙng c?n font OS).
- **HB wire d„ dÛng gap L2** ó complex script render qua atlas khi cÛ DLL; **thua Qt** khi thi?u DLL (Qt luÙn linked HB).
- **Thua rich text** v‡ **font shaping edge cases** (variable font, hinting, color emoji full).
- CÚn: Thai/Deva **box fallback** khi thi?u DLL; do l?i ASCII bench sau Wave B.

---

### 9.6 Layout engine

| | TkvUI (`TkvUI.Layout`) | Qt | Slint | egui | ImGui |
|---|---|---|---|---|---|
| Flex row/col | **CÛ** + wrap + cross-align + justify | `QBoxLayout` (+wrap m?i) | row/col??? | horizontal/vertical | SameLine/Columns |
| Grid + span | **CÛ** `GridStyle` + span | `QGridLayout` | GridLayout |_table | Table |
| Stack | **CÛ** | `QStackedLayout` | `StackedWidget` | ó | ó |
| DPI helpers | **CÛ** | native QScreen | logical px | pixels | pixels |
| Constraint solver /%</> | validator co b?n | khÙng (d˘ng nested) | percent | ó | ó |
| Selftest | **50/50** | ó | ó | ó | ó |

**Verdict:** Layout **d? app form**; Qt deeper (splitter c‚n b?ng, anchor ph?c t?p, QML layout). Slint declarative uu tiÍn designer. TkvUI **hÚa tier utility**, thua tooling.

---

### 9.7 Graphics / rasterizer / effects

| | TkvUI | PyQt6 | Slint | egui | ImGui |
|---|---|---|---|---|---|
| Raster | **T? vi?t** Bresenham, round-rect band-split, arc sin/cos, poly, clip, image blit ó `graphics_selftest 29/29` | QPainter ? engine Qt (Raster/OpenGL/Vulkan) | femtovg/skia-like + GPU | mesh triangles GPU | same ImGui draw lists |
| Pixel format | **`list[i64]`** 8B/px (i32 ho„n ó Ph? l?c M1) | QImage 4B/px typical | RGBA8 | RGBA8 | RGBA8 |
| Effects | box_blur, **half-res 2.1◊**, kawase 3-pass, backdrop, specular, drop-shadow ó `effects 32/32` | QGraphicsBlurEffect, QtGui | trung bÏnh effects | imgui-based blur Ìt | user |
| Compositing | SrcOver t? vi?t, ULW Win32 | QPainter composition modes full | Porter-Duff | blend | blend |
| GPU path | **stub 11/11 device ops** | **Qt RHI** (D3D/Metal/Vulkan/GL) | **wgpu/femtovg GPU** | **wgpu/glow production** | backend user (DX11 ph? bi?n) |

**Verdict:** CPU raster **nhanh cho widget paint** (render 1000 button ~30 ms vs PyQt ~43 ms). **Thua n?ng GPU** (L4) ó Slint/egui/Qt ship GPU; TkvUI chua present 1 frame qua GPU th?t.

---

### 9.8 Input / events / focus / IME

| | TkvUI | PyQt6 | egui | ImGui |
|---|---|---|---|---|
| Hit-test | `hit_test_tree` topmost-first + per-widget `hit_*` | `QWidget.childAt` / event propagation | immediate sense() | ItemHovered |
| Dispatcher | capture, gesture tap/pan/pinch ó `input 41/41` | full event loop + filters | context input | IO AddKeyEvent |
| Focus | FocusManager Tab/Shift-Tab ó widgets selftest | `QWidget.focus` + tab order | focus state | NavInput |
| Keyboard | chord parser (Wave A KeySeq) | QKeySequence full | modifiers | Nav + keys |
| **IME Vi?t** | **Telex/VNI composition Win32 Imm* ó ime 37/37** | qua platform input context | limited | limited |
| Touch | GestureRecognizer | QTouchEvent | pointer | touch optional |

**Verdict:** Input **d? desktop + touch contract**; IME Vi?t **niche th?ng** (Qt ph? thu?c OS IME). Chua cÛ drag-drop gi?a widget, accessibility actions trÍn input.

---

### 9.9 Persistence ó SQL chi ti?t

| H?ng m?c | TokenVector.UI (`TkvUI.SQLite` + Data) | PyQt6 QSQLITE | Slint | egui | ImGui |
|---|---|---|---|---|---|
| Engine | **T? vi?t** page 4KB + B-tree + WAL-lite + dual-slot file `TKVSQL1` | **SQLite C lib** full | khÙng | khÙng | khÙng |
| Selftest | **132/132** + crash matrix + **kill-9 12 cycle** | qua probe `sql.crud` | ó | ó | ó |
| Features | CRUD, multi-WHERE, **JOIN**, snapshot tx, rowid index, SqlTableModel, SqlQuery, SqlRelation | full SQL standard | ó | ó | ó |
| Round-trip 1000 rows file | **~81 ms** | **~195 ms** | ó | ó | ó |
| In-mem CRUD total | **~8 ms/rep** | ~14 ms/rep | ó | ó | ó |
| Crash safety | dual-slot: corrupt 1 slot v?n load; kill-9 tested | SQLite journal/WAL official | ó | ó | ó |
| SQL dialect completeness | **subset m?nh enough CRUD** ó khÙng full SQL (window fn, CTE d?y d?Ö) | SQLite full | ó | ó | ó |

**Verdict: TH?NG niche + 2.4◊ speed** (ghi nh?n fsync). **Thua completeness** (SQLite l‡ standard de facto). Slint/egui/ImGui **khÙng cÛ** ? TkvUI d?c quy?n nhÛm n‡y.

---

### 9.10 PDF / In ?n

| | TkvUI | PyQt6 | Slint/egui/ImGui |
|---|---|---|---|
| PDF writer | **T? vi?t** `PdfDocument`+xref+Base14 fonts+paths+tables ó **printing 63/63** | `QPdfWriter`/`QPdfEngine` | khÙng |
| Shell print | **`ShellExecuteA` th?t** verified live | `QPrinter` + print dialog full (preview, printer enum, page ranges) | khÙng |
| Print preview | PrintPreview widget co b?n | **QPrintPreviewDialog** production | ó |
| HTML?PDF | khÙng | QTextDocument print | ó |

**Verdict:** **–?c quy?n cÛ PDF+print built-in** so v?i Slint/egui/ImGui. **Parity PDF file** v?i PyQt; **thua print engine** (preview/printer discovery).

---

### 9.11 Clipboard OS

| | TkvUI | PyQt6 | egui | ImGui |
|---|---|---|---|---|
| API | `TkvUI.Clipboard` **Win32 CF_TEXT+UNICODE** ó **12/12** ASCII/Vi?t/emoji RT | `QClipboard` cross-plat | winit clipboard | glfw/win32 backend |
| Cross-plat | **Win32 th?t**, X11/Cocoa stub | **Win/mac/X11/Wayland** | multi | multi |

**Verdict:** Windows **d? round-trip**; **thua ph?m vi OS** v?i Qt/egui.

---

### 9.12 Accessibility

| | TkvUI | PyQt6 | Slint/egui | Dear ImGui |
|---|---|---|---|---|
| C‚y a11y | `TkvUI.A11y` role/label/value/states/bounds ó a11y **41/41** | `QAccessible` + UIA/AT-SPI native | **AccessKit** (shared) | **khÙng** ? "blank window" |
| Bridge | HWND mirror + JSON + A11yBridge **94/94** + UIA/AT-SPI stubs **33+22** | native | AccessKit adapters | ó |
| Test | **KitTest 16/16** (query+act trÍn widget th?t) | binding tests | **egui_kittest** query c‚y screen reader | ó |
| NVDA th?t | Phase 9.1: title/chrome OK; **widget custom 0 utterance** | button d?c du?c (WinForms control) | AccessKit ? NVDA (egui production) | fail |
| K? ho?ch | **L7: C# COM shim UiaHost** ho?c AccessKit C bindings | ó | ó | ó |

**Verdict:** TkvUI **? gi?a**: cÛ model+test, **chua nÛi chuy?n du?c NVDA v?i widget custom**. Qt/AccessKit **th?ng**. ImGui **thua c? ta** (0 a11y) ó m?i di?m hi?m TkvUI th?ng ImGui.

---

### 9.13 GPU

| | TkvUI | PyQt6 (RHI) | Slint | egui | ImGui |
|---|---|---|---|---|---|
| API surface | abstraction + factory + probe Vulkan/D3D11/Metal ó gpu **66/66** nhung **device ops stub** | RHI th?t multi-backend | femtovg?GPU | **wgpu** (Vulkan/DX/Metal/GL) | DX11/GL/Vulkan backends ph? bi?n |
| Compute | chua (plan L4 blur kernel) | Qt compute limited | khÙng focus | wgpu compute | khÙng focus |
| Present | ULW CPU Blit | GPU swapchain | GPU | GPU | GPU |

**Verdict: THUA (L4).** C?n host GPU + implement compute-blit tru?c, render sau. Chua do Slint/egui fps th?t trÍn m·y n‡y.

---

### 9.14 WASM / Web

| | TkvUI | PyQt6 | Slint | egui | ImGui |
|---|---|---|---|---|---|
| Ch?y trÍn web | **WASI interp wasmtime DATA_OK** + browser canvas demo (`WASM_STATUS.md`) | Pyodide (heavy) | **wasm production** demos | **eframe wasm** official | wasm demos |
| AOT/size | AOT closed (upstream),AppBundle ~12.4 MB interp | Pyodide tens of MB | opt small | decent | good |
| Interactive app full | partial (selftest pure-compute; canvas frame demo) | partial | full UI | full UI | full UI |

**Verdict:** **HÚa tier interpreter** v?i Pyodide; **thua Slint/egui** (production wasm, small size). KhÙng claim ìweb app productionî.

---

### 9.15 Cross-platform

| Backend | TkvUI | PyQt6 | Slint | egui | ImGui |
|---|---|---|---|---|---|
| **Windows** | **Win32 ULW+DIB th?t** (platform 82/82, multi-window 2 HWND) | full | full | full | full |
| **Linux X11/Wayland** | **stub** ó blocker **R7 `.so` linter tkvc** | full | full | full | full |
| **macOS Cocoa** | **stub** (WinForms vehicle t?m) | full | full | full | full |
| **Android** | contract host-driven (verify **SKIP** c?n thi?t b?) | full | mobile stories | via NDK user | backends |
| **iOS** | contract host (SKIP) | full | mobile | user | backends |
| `detect_platform()` | probe th?t 1..6 + env override | QSysInfo | runtime | std::env | ó |

**Verdict: THUA rı (L8).** Ch? Windows production-ready. Qt th?ng tuy?t d?i multi-OS; Slint/egui cung multi. **Acceptance:** `X11_OK` du?i Xvfb khi R7 m?.

---

### 9.16 OS look / theme / DPI

| | TkvUI | PyQt6 | Slint | egui |
|---|---|---|---|---|
| Theme engine | `TkvUI.Theme` OsPalette 13 roles + Light/Dark/HC ó theme **79/79** + QSS-subset cascade | **native platform style** + QSS + Fusion | Material/Fluent/Cupertino/**Native** styles built-in | ???? customizable, khÙng native Win chrome |
| Widgets self-drawn | **41 native** (post Wave B) self-draw | 1:1 native khi d˘ng style d˙ng | styled declarative | immediate styled |
| DPI | token DPI + validators | **QScreen devicePixelRatio full** | logical px | physical + scale factor |
| Accent color Win11 | **chua** (L5 plan: registry DWM) | qua style engine | themed | themed |
| Follow OS dark realtime | plan WM_SETTINGCHANGE | cÛ | cÛ | cÛ |

**Verdict: Partial (L5).** Thua Qt native + Slint multi-style. –? ìmodern flat light/darkî cho app internal; chua claim ìtrÙng nhu app Explorerî.

---

### 9.17 Hi?u nang ó b?ng bench d?y d? (BENCH.md chu?n ho·)

| # | Benchmark | TkvUI | PyQt6 | T? | Verdict |
|---|---|---|---|---|---|
| 6.2 | Text 21.6K chars/block | **9.4 ms** | 13.7ñ18.1 ms | **~1.9◊** | **TH?NG** |
| 6.3 | Construct 1000 button | **<0.16 ms** | 12.6 ms | **~80◊+** (timer floor) | **TH?NG** |
| 6.3 | Render 1000 button | **~30 ms** | ~43 ms | **~1.4◊** | **TH?NG** |
| 6.4 | CRUD in-mem total/rep | **~8 ms** | ~14 ms | **~1.8◊** | **TH?NG** |
| 6.4c | SQL file RT 1000 rows | **81 ms** | 195 ms | **~2.4◊** | **TH?NG** |
| 6.1 | Memory load-text peak | **~46 MB** | **15.6 MB** | **thua ~3◊** | **THUA** |
| 6.1 | Memory idle trivial | **11.0 MB** | 15.6 MB | **th?ng** | **TH?NG** |
| ó | Cold spawn exe | **~1.0 s** | **~0.2 s** | **thua 5◊** | **THUA (L3)** |
| 6.5 | Blur half-res | 2.1◊ internal | ó | ó | n?i b? |
| MJPEG 160◊120 | ~106 fps | ó | ó | niche |
| MJPEG 720p | ~2 fps | hw decode Qt | ó | **THUA realtime HD** |
| TKVV 720p path | ~100 fps measured | ó | ó | **TH?NG custom codec** |

**?n d?nh gate:** `BENCH_STABLE_OK` median 3-run (ch?ng flake GetTickCount 16 ms).

---

### 9.18 Media / codec / playback

| | TkvUI | PyQt6 QtMultimedia | egui/Slint/ImGui |
|---|---|---|---|
| Demux MP4 | **TkvUI.Mp4 62/62** boxes/tracks/sample table | via ffmpeg/phonon stack | khÙng / user gstreamer |
| Decode H.264 | **Baseline OpenH264 shim 8/8 + RT 11/12** | **full Main/High + HW** | user |
| GIF | parse+LZW **44/44** | QImageReader | limited |
| MJPEG | pure .tkv **44/44 + HD 6/6** | limited | ó |
| Custom TKVV | **56/56 + player 21/21 ~100fps@720p** | ó | ó |
| Audio playback | **chua** (L6 WASAPI plan) | full | ó |
| UI widgets 10 | transport?abloop **80/80** | Ìt s?n, hay QML | ó |
| Clip ingest MP4?TKVV | **ClipPlayer 14/14** | ó | ó |

**Verdict:** Ingest+UI **d? niche player nh?**; **thua Qt** HW decode, audio clock, DRM, adaptive streaming. **KhÙng so** Slint/egui (khÙng media core).

---

### 9.19 Testing / CI / tooling

| | TkvUI | PyQt6 | Slint | egui | ImGui |
|---|---|---|---|---|---|
| Unit/selftest headless | **verify 55 case, ~2200+ checks**, LOCALS_OK | pytest / Qt Test | cargo test | cargo test | test Ìt |
| GUI e2e | **KitTest 16/16** pattern a11y | pytest-qt / offscreen | **playwright-ish demos + CI** | **kittest** official | sample runs |
| Fuzz | **Fuzz 7/7 shaping** | user | user | user | ó |
| Bench | **bench_all + bench_stable BENCH_OK** | tools/bench_*_pyqt.py side-by-side | criterion | criterion | ó |
| CI | `.github/workflows/ci.yml` **static-only** (purity/JSON/shell) ó **chua ch?y suite Win/Ubuntu full** | Qt CI massive | **GitHub Actions build+test+wasm** | Actions + kittest | Actions |
| Issue templates | **◊3** (benchmark/claim/purity) | GitHub full | full | full | full |
| Designer | **DesignerApp headless+windowed** | Qt Designer production | **Live Preview + Figma plugin** | inspector/debug | ó |
| Docs API | `docs/API.md` index | **apidox/qt.io** | book | rustdoc | docs |

**Verdict:** Unit **m?nh so v?i kÌch thu?c** (55 cases). **Thua CI e2e + tooling designer** (Slint Live Preview l‡ gold standard). L9 cÚn ch?y full suite trÍn Actions.

---

### 9.20 Packaging / deploy / startup

| | TkvUI | PyQt6 | Slint | egui |
|---|---|---|---|---|
| Single EXE app | **549 KBñ3.3 MB** (c?n .NET FW trÍn m·y) | PyInstaller **~15ñ50 MB+** | static musl nh? / RCC | static small |
| Package manager | **NuGet** `TokenVector.UI.nupkg` + **`.tkvpkg` zip+sha256** | pip | cargo/cmake | cargo |
| Integrity | `package.sh --verify` PKG_VERIFY_OK | pip hash | crates.io | crates.io |
| Cold start | **~1.0 s** AV+JIT | **~0.2 s** | native fast | native fast |
| Idle RAM | **11 MB** | 15.6 MB | th?p (MCU target) | th?p |

**Verdict:** **Deploy size TH?NG PyQt n?ng**; **startup THUA native+PyQt**. Slint th?ng embedded RAM.

---

### 9.21 Documentation, onboarding, i18n

| | TkvUI | PyQt6 | Slint | egui |
|---|---|---|---|---|
| Quickstart | README verify 1 l?nh | pip install + qml/tutorials?? | book + live preview | book + demo |
| Tutorial CRUD | **`TUTORIAL_CRUD.md` + CrudDemo** | official examples 1000+ | templates | demo crates |
| Screenshots | **2 PNG render th?t** + plan 3 GIF | huge gallery | studio | show case |
| Vietnamese docs | **README + comments VN** | EN/CN/jaÖ | EN | EN |
| API reference | API.md 27 module summary | **Qt docs industry gold** | rustdoc+md | rustdoc |
| Roadmap cÙng khai | LEVEL_PLAN + Roadmap + CHANGELOG | Qt roadmap cÙng ty | public | public |

**Verdict:** Docs **d? internal + contribute**, **thua Qt/ecosystem scale**. L10: GIF + video + nuget.org.

---

### 9.22 Gi?i h?n compiler `.tkv` ?nh hu?ng so s·nh

| Gap (COMPILER_GAPS) | ?nh hu?ng vs d?i th? | Tr?ng th·i |
|---|---|---|
| KhÙng ternary / bitwise (d„ m? R5) / `pass` | Code verbosity; MJPEG cu ch?m | R5 m?; ternary v?n c?m |
| List append quirk D1 ? ToI32 crash | Selftest d? fail sai ch? | **d„ bypass** literal/helper `nv_alloc_*` |
| Struct l?ng / fixed array | KhÙng marshal struct Win32 ph?c t?p th?ng | ch? upstream |
| COM call-in (CCW) | A11y UIA provider th?t | **L7 ch?n C# shim** |
| `.so` pinvoke | Linux/macOS/mobile | **L8 blocker R7** |
| Byte array trong record | Embed TTF v‡o PDF | 11.3 BLOCKED |
| NGEN/AOT (R10) | Cold start L3 | ch? upstream + local nGEN.ps1 |
| P7.5 list-method ordering | API design rule | tu‚n th? |

**Verdict:** Nhi?u ìthua d?i th?î **khÙng ph?i thi?u ˝ tu?ng** m‡ **d?a compiler m?** ó plan d„ map sang L3/L7/L8 + shim C#.

---

### 9.23 Scorecard chi ti?t theo h?ng m?c (TkvUI vs ìd?i th? t?t nh?tî)

| # | H?ng m?c | TkvUI | –?i th? m?nh nh?t | K?t qu? (chi ti?t) |
|---|---|---|---|---|
| 1 | Freedom license | MIT | egui/ImGui MIT | **HÚa nhÛm best** |
| 2 | NgÙn ng? m?t stack self-host | .tkv to‡n stack | khÙng ai | **–?c quy?n** |
| 3 | C?ng d?ng | 0 star | ImGui 76k | **Thua 100%** |
| 4 | Widget count | 93 | Qt ~1000 | **Thua ~10◊** |
| 5 | Widget d? CRUD/IDE form | Wave A+B cover | Qt | **G?n parity use-case** (2 ports) |
| 6 | Text ASCII speed | 9.4 ms | PyQt 18.1 | **Th?ng 1.9◊** |
| 7 | Text complex + HB | HB wire L2 optional | Qt always-HB | **HÚa khi cÛ DLL / thua khi khÙng** |
| 8 | Vi?t/IME | precomposed+Telex/VNI | Qt ph? thu?c OS | **Th?ng niche** |
| 9 | Rich text | limited | QTextDocument | **Thua** |
| 10 | Layout | flex/grid/stack | Qt/QML | **HÚa utility / thua deep** |
| 11 | CPU render widget | 30 ms/1000 | PyQt 43 ms | **Th?ng 1.4◊** |
| 12 | GPU | stub | RHI/wgpu | **Thua** |
| 13 | SQL | built-in 132 + 2.4◊ | QSQLITE / khÙng ai built-in Slint | **Th?ng niche + speed** |
| 14 | PDF+print | built-in 63 + shell | QPdf / khÙng ai | **Th?ng cÛ s?n / hÚa PDF / thua preview** |
| 15 | Clipboard | Win32 12/12 | QClipboard multi-OS | **Th?ng Win / thua multi** |
| 16 | A11y | mirror+KitTest, NVDA partial | Qt native / AccessKit | **Thua production** |
| 17 | Media | Baseline+UI 10 widget+TKVV | QtMultimedia full | **Thua breadth / th?ng UI bundle** |
| 18 | WASM | WASI interp+canvas | Slint/egui prod | **Thua** |
| 19 | Cross-plat | Win32 only real | Qt/Slint/egui multi | **Thua** |
| 20 | OS look | self-drawn 41 + theme 79 | native Qt / Slint styles | **Partial** |
| 21 | Cold start | 1.0 s | 0.2 s | **Thua 5◊** |
| 22 | Idle RAM | 11 MB | PyQt 15.6 / Slint MCU | **Th?ng PyQt / thua MCU** |
| 23 | Load RAM text | 46 MB | 15.6 MB | **Thua 3◊** |
| 24 | Deploy size | 0.5ñ1.6 MB | PyInstaller 50 MB | **Th?ng** |
| 25 | Test headless | 55/0/2 ~2200 checks | Qt tests + probe | **M?nh cho size** |
| 26 | CI | static only | full matrix | **Thua** |
| 27 | Designer | DesignerApp | Qt Designer + Slint preview | **Thua tooling** |
| 28 | Docs scale | d? internal | qt.io gold | **Thua scale** |

---

### 9.24 ìAi th?ng n?u app c?a b?n l‡Öî

| Ki?u app | G?i ˝ th?ng | L˝ do (s? trong file n‡y) |
|---|---|---|
| App CRUD/admin **nh?, single EXE, MySQL-like embedded, ti?ng Vi?t** | **TkvUI** | 549 KB, SQL/PDF built-in, 93 widget d? form, text 1.9◊, license MIT |
| App desktop **da n?n t?ng Win/Mac/Linux** | **Qt / Slint / egui** | TkvUI X11/Cocoa stub |
| App c?n **GPU-heavy / game tool immediate** | **egui / ImGui** | TkvUI GPU stub |
| App **embedded MCU** | **Slint** | RAM/size target Slint |
| App c?n **accessibility production NVDA** | **Qt / egui+AccessKit** | TkvUI 0 utterance widget |
| App c?n **~widget rare 1000 class + rich text + charts** | **Qt** | breadth 10◊ |
| Learning / research **self-hosted stack** | **TkvUI** | 1 ngÙn ng? t? raster?SQL?PDF?codec |
| Tool n?i b? Windows, quan t‚m **startup 0.2 s** | c‚n nh?c **PyQt** ho?c d?i **L3 NGEN** | cold-start gap |

---

### 9.25 Kho?ng c·ch cÚn l?i (gap detail, khÙng l?p LEVEL_PLAN)

1. **Width:** 93 vs ~1000 ó Wave C polish depth t?ng widget (validation, models, delegates, drag-drop) quan tr?ng hon thÍm constructor m?i.
2. **Depth t?ng control:** editable combo, table cell delegates, tree drag, dock save/restore, MDI cascade/max ó ìm?ng nhung cÛî.
3. **Runtime platform:** ch? Windows real ó m? `.so` l‡ kho· L8/L9 Ubuntu.
4. **Perception:** cold-start + load RAM ó NGEN/R12/lazy module.
5. **Trust:** public repo, CI green badge, 1 external issue.
6. **Media audio path** v‡ FFmpeg Main/High (L6).
7. **GPU compute** tru?c raster GPU (L4).
8. **NVDA** qua C# shim (L7).

---

> **Phuong ph·p:** m?i s? TkvUI in ra t? selftest/bench d„ ch?y trÍn m·y dev; m?i s? d?i th? ngo‡i PyQt ghi ngu?n public v‡ **chua reproduce runtime** ó khÙng d˘ng d? claim ìnhanh hon egui/Slintî khi chua c‡i v‡ bench c˘ng workload.
