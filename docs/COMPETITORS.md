# So sánh repo TokenVector.UI với đối thủ (2026-09-19 → refresh 2026-09-24)

> Stars GitHub lấy 2026-09-19, **tra lại 2026-09-24** (Slint/egui/ImGui — sẽ lỗi thời, tra lại khi claim).
> Mục đích: định vị trung thực + rút gap list. Không dùng để quảng cáo.
> **2026-09-24 (Wave A+B):** verify **55/0/2** (`TKVUI_VERIFY_OK`), catalog **93 constructors**,
> Qt ports: App 52/52 + Tree/Dock **31/31 `QTDOCK_OK`**, native **255/255**, breadth 15/15.
> Probe PyQt6 6.11.0 offscreen 9/9 (`tools/bench/func_pyqt_probe.py`) — xem §2b.
> H.264 Baseline decode打通 + HarfBuzz 14.5 + wire draw-path (L2) — cập nhật §2/§2b/§8.

---

## 1. Headline

| | TokenVector.UI | PyQt6 | PySide6 | Slint | egui | Dear ImGui |
|---|---|---|---|---|---|---|
| Ngôn ngữ | .tkv → .NET IL | Python (binding Qt C++) | Python (binding Qt C++, official) | Rust/C++/JS/Python (.slint DSL) | Rust (immediate) | C++ (immediate) |
| License | MIT | GPL-3 / commercial | LGPL-3 / commercial | GPL-3 / commercial (royalty-free) | MIT/Apache-2.0 | MIT |
| Stars | (local, chưa public — **0**) | PyPI dl ~M/tháng | PyPI dl ~M/tháng | **~23.7k** (2026-09-24) | **~30.5k** (2026-09-24) | **~76k** (2026-09-19) |
| Tuổi / nhịp | 2026-, **46 commits** dày, v2.9.0 | từ 1998, release đều | official Qt Co, release đều | 2020-, active | 2019-, active | 2014-, active |
| Repo size | **94 file `.tkv`** (~4.2 MB repo tracked) | binding + Qt binary | = PyQt6 | monorepo lớn | crates | single-header + examples |
| Widget | **93 constructors** (Widgets 42 + Native 41 + Media 10; Wave A +10 form-control, Wave B +Dock float/tab/MDI tile/Ribbon/PropGrid/Tree multi/ContextMenu) | **~1000 classes Qt** | = PyQt6 | default set + Material/Fluent/Cupertino/Native | ~30 + custom dễ | ~60, tool-oriented |
| Test | **verify 55/0/2** headless (~2200+ checks) + LOCALS_OK | pytest/offscreen | = PyQt | GUI automation | **kittest** (a11y-tree) | manual/examples |

---

## 2. So theo từng mặt (bằng chứng — refresh 2026-09-24)

| Mặt | TkvUI (đo thật) | Đối thủ tốt nhất | Kết luận |
|---|---|---|---|
| Binary/deploy | suite **1644 KB** (32+ module), app **549 KB**–3.3 MB single EXE (cần .NET FW); NuGet + `.tkvpkg` | Slint (MCU < 300 KiB RAM, wasm); egui wasm gọn; **PyQt PyInstaller 50 MB+** | **Thắng PyQt deploy**; thua Slint đa nền/embedded |
| Startup/RAM | cold-spawn **~1.0 s** (AV+CLR); idle peak **11.0 MB** (trivial) / **~46 MB** (bench text load) | PyQt cold **~0.2 s**, QApp idle **15.6 MB** / load text **15.6 MB** | ⚠️ Thua cold-start có AV; **thắng idle**, **thua load-text ~3×** |
| Text/shaping | atlas **9.4 ms/rep** (thắng PyQt6 18.1 ms, **1.9×**); engine thuần (Arabic/Thai/Deva/…); **HarfBuzz 14.5打通 + wire draw-path (L2 2026-09-24)** optional `libharfbuzz.dll` | Qt (HarfBuzz/full) | **Thắng ASCII 1.9×**; HB wire thu hẹp complex-script — thiếu dll → fallback engine cũ |
| Widgets | **93 constructors** (Wave A +10 form, Wave B +Dock float/tab + MDI tile_h + Ribbon + PropGrid + Tree multi-sel + ContextMenu) + wizard/color/font/statusbar/checkbox… + item-view + stylesheet | Qt ~1000 classes | **Thua số lượng**; Wave A+B đóng gap app CRUD/IDE-ish; đủ CRUD/form/desktop admin |
| SQL persistence | **Binary page 4KB + B-tree + WAL-lite + multi-WHERE + JOIN** 132/132 + kill-9 12 cycle; round-trip 1000 rows **~81 ms** | Không ai built-in; QSQLITE **~195 ms** | **Thắng niche + 2.4×** |
| H.264 decode | **Baseline decode打通** (C# shim + OpenH264, 8/8 + round-trip 11/12) | QtMultimedia/ffmpeg (full) | Thua breadth; thắng built-in nhỏ |
| PDF/print | PDF writer 63/63 + **shell-print thật** (ShellExecuteA live) | Không ai built-in | **Thắng niche** |
| Accessibility | Data model + Win32 HWND mirror + JSON + **KitTest 16/16**; NVDA: chrome đọc được, widget custom **0 utterance** (Phase 9.1) | Qt native UIA; Slint/egui **AccessKit** | ⚠️ Partial — COM bridge cần C# shim / AccessKit path |
| GPU | abstraction + shader pipeline **stubs** | Qt RHI; egui wgpu | **Thua** (cần host GPU thật) |
| WASM | **WASI interp chạy thật** (wasmtime DATA_OK) + browser canvas; AOT closed upstream | Slint/egui wasm production | Partial (hòa Pyodide-tier) |
| CI | `.github/workflows/ci.yml` **static-only** + issue templates ×3 + LOCALS_OK | Slint GUI e2e; egui **kittest** | Thua GUI-e2e; có unit+static gate |
| Cross-plat | Win32 thật; **X11/Cocoa stub**; Android/iOS host contract (verify SKIP) | Qt/Slint/egui multi-OS | **Thua** (L8 blocker R7 `.so`) |
| OS look | self-drawn theme Win light/dark/HC (**41 native widgets** after Wave B) | Qt native style / Fluent | ⚠️ Partial (L5) |
| Cộng đồng | **0 star / 0 issue** (local, 46 commits) | Qt Company; Slint/egui/ImGui **23k–76k stars** | **Thua** (L10 — cần public repo) |

---

## 2b. Ma trận parity chức năng (refresh 2026-09-24)

Bằng chứng TkvUI = verify **55/0/2** (`TKVUI_VERIFY_OK`); PyQt6 = probe offscreen **9/9**
(`tools/bench/func_pyqt_probe.py`, PyQt 6.11.0/Qt 6.11.2). Modal-exec / playback thật
không offscreen → ghi nhận, không claim.

| Chức năng | TkvUI (bằng chứng) | PyQt6 (probe) | Kết luận |
|---|---|---|---|
| App assembly | **QtAppPort 52/52** (menus/toolbar/statusbar/RichEdit/dialogs/print/recent) | `mainwin.app` PASS | Parity app chuẩn |
| Dock/MDI/IDE layout | **QtTreeDockPort 31/31** (dock float/tab + tree multi-sel + MDI tile_h + menubar View) | QMainWindow dock sẵn | **Parity coverage** (Wave B 2026-09-24); Qt vẫn richer (z-order, save/restore) |
| Widgets render | **93 constructors**; native 255/255 + widgets 167/167 + breadth 15/15 | `widgets.render17` PASS (17) | Đủ CRUD/form; Qt thắng breadth + style native |
| Dialogs | NativeDialog + DlgFile/Color/Font (**NATIVEDLG 39/39**) | `dialogs.instantiate6` PASS | Parity instantiate |
| Text Việt/bidi | 134 glyph precomposed + HB 14.5 **wire draw-path (L2)**; Bidi **194/194** | `text.vi-bidi` PASS | Qt thắng full khi thiếu dll; TkvUI thắng ASCII 1.9× |
| SQL | **132/132** + kill-9 + round-trip **2.4×** | `sql.crud` PASS + filebench 195 ms | TkvUI thắng niche |
| PDF/print | PDF **63/63** + shell-print thật | `print.pdf` PASS | Parity PDF; TkvUI shell-print; Qt print engine |
| Clipboard | Win32 thật **12/12** | `clipboard.roundtrip` PASS | TkvUI Windows; Qt cross-plat |
| Item-view | Data proxy/sort/filter **76/76** + SqlTableModel | `itemview.proxy` PASS | Parity cơ bản |
| Media | GIF/MJPEG/TKVV + MP4 **62/62** + VideoDemo **21/21** + ClipPlayer **14/14** + **H.264 Baseline 8/8** | `media.setsource` PASS + QtMultimedia full | Thu hẹp; Qt thắng playback + Main/High |
| a11y | HWND mirror + JSON + KitTest **16/16**; NVDA partial | native UIA | Qt thắng native |
| GPU/WASM | stubs; WASI interp + canvas | Qt RHI; production wasm | Thua GPU; hòa WASM tier |

---

## 3. Phát hiện chiến lược: AccessKit

- Slint + egui (+ Bevy, Freya, Xilem) **không tự implement UIA/AT-SPI/NSAccessibility** — họ dùng chung **AccessKit** (abstraction cây a11y + adapter Windows/macOS/Unix-DBus/Android/iOS, có **C và Python bindings**).
- egui bật AccessKit mặc định trong eframe; test qua `egui_kittest` query đúng cây mà screen reader đọc — mô hình test mà bridge của ta nên copy.
- ImGui là bằng chứng ngược: không a11y → blind user báo "blank window" (giống hệt kết quả NVDA của ta).
- **Cho Phase 9.2**: mục tiêu đúng không phải "viết COM vtable tay" mà là **bắn tới AccessKit C bindings** — vẫn cần `.so/.dll` pinvoke + marshal struct (đang blocked), nhưng là đường đã có người đi, có test pattern (kittest) để học.

---

## 4. Gap list của repo (xếp theo rẻ → đắt)

| # | Task | Effort | Status |
|---|---|---|---|
| 1 | **CONTRIBUTING.md + issue/PR templates** | Rẻ (1 buổi) | ✅ DONE (`CONTRIBUTING.md` + `.github/ISSUE_TEMPLATE` ×3) |
| 2 | **API reference index** | Vừa | ✅ DONE (`docs/API.md` — Native 50 fn / Widgets 64 fn, refresh Wave B) |
| 3 | **Screenshots/GIF trong README** | Rẻ | ✅ DONE (`docs/img/shot_browser.png` + `shot_emoji.png`) |
| 4 | **Badges + releases có changelog theo tag** | Rẻ | ✅ DONE (`CHANGELOG.md`, NuGet nuspec, `.tkvpkg`) |
| 5 | **kittest-style test** | Vừa | ✅ DONE (`TkvUI.KitTest` 16/16) |
| 6 | **Benchmark suite 1 lệnh** | Vừa | ✅ DONE (`tools/bench_all.sh` / `.ps1` + `bench_stable`) |
| 7 | **Vietnamese-first + PDF/SQL built-in** → README đầu | Rẻ | ✅ DONE |
| 8 | **L1 Wave A widget breadth 43→88** | L | ✅ DONE 2026-09-24 (`3cc205d`) |
| 9 | **L1 Wave B structural + Qt Tree/Dock port** | M | ✅ DONE 2026-09-24 (`d70326e`, QTDOCK 31/31) |
| 10 | **L2 wire HarfBuzz draw path** | M | ✅ DONE 2026-09-24 (`3cc18d0`, leaf + lazy-bake) |
| 11 | **CI matrix Win+Ubuntu (L9)** | M | ⏳ `ci.yml` static-only — còn chạy suite trên Ubuntu |
| 12 | **Public repo + first external user (L10)** | S–M | ⏳ blocker marketing/release |

---

## 5. Roadmap Phase 11-12 (Text/Tooling)

| Phase | Task | Status | Blocker |
|---|---|---|---|
| **11.1 Font Fallback** | ✅ DONE (26/26 PASS) | — |
| **11.2 Complex Script** | 🟡 Core打通 (HarfBuzz 14.5 pinvoke, Bidi 194/194) — còn: wire draw path + atlas lazy-bake HB gids | thiếu leaf module + atlas design |
| **11.3 TTF Embed PDF** | 🔴 BLOCKED (byte array) | tkvc gap |
| **11.4 Fuzz Shaping** | ✅ DONE (FUZZ_OK 7/7) | — |
| **12.1 DesignerApp** | ✅ DONE (headless + windowed) | — |
| **12.2 Tutorial** | ✅ DONE | — |
| **12.3 CI Matrix** | ⏳ Pending | GitHub Actions matrix |
| **12.4 Fuzz** | ✅ DONE (FUZZ_OK) | — |

---

## 7. Thứ tự ưu tiên đề xuất

1. **Font fallback mở rộng** (emoji, color font, variable font) — niche value cao
2. **Wire HarfBuzz vào draw path** (leaf `TkvUI.HarfBuzz` + atlas lazy-bake HB gids — core打通2026-09-23)
3. **12.3 CI Matrix** — CI matrix Win+Ubuntu+WASM
4. **docs/COMPETITORS.md finalize** — Gap list cập nhật
5. **Emoji/Color font support** (11.1 extension)

---

## 8. Tóm tắt vị thế (Reality Check — 2026-09-24)

| Tiêu chí | PyQt6 | TokenVector.UI | Kết luận |
|---|---|---|---|
| Binary size | 15–20 MB (PyInstaller 50 MB+) | **1644 KB** suite / app **549 KB** | ✅ Thắng |
| Cold startup | **~0.2 s** | **~1.0 s** (AV+CLR) | ⚠️ Thua (L3) |
| Memory idle | 15.6 MB | **11.0 MB** | ✅ Thắng |
| Memory load-text | **15.6 MB** | ~46 MB | ❌ Thua ~3× (pixel i64 + CLR; i32 hoãn) |
| Text render | ~18.1 ms/rep | **9.4 ms** | ✅ Thắng 1.9× |
| Widget construct | ~12.6 ms/1000 | **<0.16 ms** | ✅ Thắng |
| Widget render | ~43 ms/1000 | **~30 ms** | ✅ Thắng 1.4× |
| Widget breadth | **~1000 classes** | **93 constructors** | ❌ Thua (Wave A+B +16; còn Wave C) |
| CRUD engine in-mem | ~14 ms/rep | **~8 ms** | ✅ Thắng 1.8× |
| SQL file round-trip | 195 ms/1000 rows | **81 ms** | ✅ Thắng 2.4× |
| App port | (gốc Qt) | **QtApp 52/52 + QtTreeDock 31/31** | ✅ Parity (2 ports) |
| Media | full profile + playback | **Baseline H.264 8/8** + TKVV realtime | ⚠️ Niche thu hẹp |
| WASM | Pyodide interp | **WASI interp + canvas** | ⚠️ Hòa tier |
| OS look | native | self-drawn **41 native** | ⚠️ Partial (L5) |
| Cross-plat | full | **Win32 thật, X11/Cocoa stub** | ❌ Thua (L8) |
| A11y | native UIA | **HWND mirror + KitTest** | ⚠️ Partial (L7) |
| GPU | RHI | stubs | ❌ Thua (L4) |
| Ecosystem | massive | **0 star** | ❌ Thua (L10) |
| Verify | pytest/offscreen | **55/0/2** + LOCALS_OK | ✅ Unit headless vững |

**Scorecard nhanh vs 6 đối thủ:**

| | Thắng | Hòa | Thua |
|---|---|---|---|
| **vs PyQt6/PySide6** | binary, idle-mem, text 1.9×, widget speed, SQL 2.4×, PDF/print built-in, clipboard Win, app-port parity, H.264 niche | WASM tier, item-view, dialogs | **breadth ~10×**, cold-start, GPU, OS native, cross-plat, ecosystem, a11y native, load-mem |
| **vs Slint** | built-in SQL/PDF/print/media niche | a11y path (cùng chưa full) | **stars, embedded/MCU, wasm prod, DSL tooling, cross-plat, CI e2e** |
| **vs egui** | SQL/PDF/print built-in, retained-mode widgets (93) | WASM | **wgpu GPU, stars, kittest, ecosystem, cross-plat** |
| **vs Dear ImGui** | a11y model (ImGui = 0), SQL/PDF, form widgets | speed ballpark | **tooling ecosystem, immediate-mode perf culture, 76k stars, renderer-agnostic** |

**Kết luận (2026-09-24, sau Wave A+B + L2 HB wire):** TokenVector.UI **thắng PyQt6** ở
binary size, idle memory, text render 1.9×, widget create/render, SQL round-trip 2.4×,
SQL/PDF/print built-in, clipboard Windows, **app-port parity 2 example**, H.264 Baseline +
HarfBuzz wire — **thua** widget breadth (93 vs ~1000), cold-start có AV, GPU, OS look native,
cross-plat (X11/Cocoa stub), ecosystem (0 star), media full-profile, load-text memory.
Compiler: R1–R6/R9/R10/R12 đã mở; còn đóng struct lồng/fixed-array, COM call-in, R7 Linux.
Không claim "đánh bại PyQt6 mọi mặt" — **thắng niche** (deploy, Vietnamese-first, text, persistence, decode nhỏ)
và **đã đóng 2 gap lớn L1 (Wave A+B) + L2 (HB wire)** trong 2026-09-24.

---

## 📋 Next Steps (Theo thứ tự ưu tiên — 2026-09-24)

1. **L3 cold-start** — đo warm/máy sạch + đẩy NGEN/AOT (upstream R10)
2. **L9 CI matrix** — chạy suite headless trên Ubuntu (R7 `.so` là blocker)
3. **L5 OS look** — theme Win11 DPI+accent polish trên 41 native widgets
4. **L7 A11y** — C# COM shim / AccessKit path để NVDA đọc widget
5. **L10 public** — push repo + NuGet.org + 1 external user
6. **Emoji color / non-BMP** (11.1 extension) — partial 12 BMP symbols
7. **L4 GPU compute-blit** trước full render; **L6 FFmpeg Main/High**

---

> **Lưu ý:** File này chỉ dùng để tracking internal. Không dùng để marketing/public claim nếu chưa verify lại số liệu.