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
| Tuổi / nhịp | 2026-, **59 commits** dày, v1.0.1 | từ 1998, release đều | official Qt Co, release đều | 2020-, active | 2019-, active | 2014-, active |
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
| Cộng đồng | mới public trên GitHub (59 commits) | Qt Company; Slint/egui/ImGui **23k–76k stars** | **Thua** (L10 — cần thời gian gây dựng) |

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

---

## 9. Đối chiếu chi tiết từng mục (2026-09-24 — không tóm tắt)

> Mỗi mục: **định nghĩa → TkvUI làm gì (bằng chứng số) → từng đối thủ → verdict → gap còn lại**.
> Số TkvUI: `tools/verify.sh` **55/0/2** (2026-09-24) + selftest in-log + `docs/BENCH.md`.
> Số PyQt6: bench chuẩn hoá 2026-09-19/20 + probe `func_pyqt_probe.py` 9/9.
> Số Slint/egui/ImGui: docs/GitHub 2026-09-24 — **chưa đo runtime trên máy này** → ghi "chưa đo".

### 9.1 Ngôn ngữ, runtime, mô hình

| Hạng mục | TokenVector.UI | PyQt6 / PySide6 | Slint | egui | Dear ImGui |
|---|---|---|---|---|---|
| Ngôn ngữ viết app | **`.tkv`** → `tkvc` → **CIL/.NET IL** → `.exe` | **Python 3** + binding Qt C++ | **`.slint` markup** + Rust/C++/JS/Python | **Rust** | **C++** |
| Runtime | **CLR / .NET FW 4.x** (JIT; NGEN chưa bật) | CPython + Qt DLL (~15–20 MB+) | Native Rust/C++ | Native Rust | Native C++ |
| Retained / immediate | **Retained** (UIElement + invalidation + frame scheduler) | **Retained** (QObject tree) | **Retained** (declared scene) | **Immediate** | **Immediate** |
| Zero native dep ngoài | **Có** — raster/font/layout/widget tự viết; optional `libharfbuzz.dll` + OpenH264 C# shim | **Không** — ship Qt + Python | stack Slint/winit/femtovg | winit/wgpu/glow | backend do user (GL/DX/Vulkan) |
| Compiler riêng | **Có** — `tkvc` + Roadmap §0 (cấm ternary, list-append D1…) | Không | rustc + slint compiler | rustc | cmake/MSVC |

**Verdict:**
- **Độc nhất:** một stack self-host `.tkv` từ raster → SQL → PDF → codec.
- **Thua DX/IDE:** không có LSP/hot-reload như Slint Live Preview.
- **Risk:** gap compiler (struct lồng, COM-in, `.so`) → blocker L7/L8.

---

### 9.2 License & phân phối thương mại

| | TokenVector.UI | PyQt6 | PySide6 | Slint | egui | Dear ImGui |
|---|---|---|---|---|---|---|
| License | **MIT** | **GPL-3** / commercial | **LGPL-3** / commercial | GPL-3 / **royalty-free desktop** / commercial embedded | **MIT / Apache-2.0** | **MIT** |
| App proprietary free? | **Có (MIT)** | Chỉ paid | **Có (LGPL)** dynamic link | Desktop free; **embedded thường cần commercial** | **Có** | **Có** |
| Codec/patent kèm | OpenH264 binary Cisco (BSD-2 + Cisco trả MPEG-LA); **cấm x264 GPL** | Qt modules tùy | = | không ship codec | không | không |

**Verdict:** TkvUI **cùng hạng freedom egui/ImGui**, **nhẹ hơn PyQt GPL**, **linh hoạt hơn Slint embedded**.

---

### 9.3 Cộng đồng, tuổi đời, nhịp phát triển

| | TokenVector.UI | PyQt6/PySide6 | Slint | egui | Dear ImGui |
|---|---|---|---|---|---|
| Tuổi | **2026–**, **59 commits**, v1.0.1 | Qt từ **1998** | **2020–** | **2019–** | **2014–** |
| Stars (2026-09-24) | **0** (chưa public) | PyPI ~M download/th | **~23.7k** | **~30.5k** | **~76k** |
| Contributors | 1 | Qt Company + rất lớn | **276** | hàng trăm | **583** |
| Open issues sống | 0 | nghìn+ across Qt | ~700+ | ~900+ | nghìn+ |
| Docs scale | README + docs/* + tutorial + 2 screenshot | official.qt.io gold | slint.dev + book | egui.rs | docs + demos |

**Verdict: THUA nặng (L10).** Cần public repo + NuGet.org + external user thật.

---

### 9.4 Widget breadth — liệt kê theo nhóm (93 constructors)

**Đếm:** umbrella `widget_constructor_catalog()` = **93** distinct (Widgets 42 + Native 41 + Media 10).

#### 9.4.1 Form / input

| TkvUI | PyQt6 | Chất lượng | Verdict |
|---|---|---|---|
| `make_native_button` / `_default` / `make_button` / `make_button_outline` | `QPushButton`/`QToolButton` | hover/press/disabled/default | **Đủ** |
| `make_native_check` / `make_native_checkbox` / `make_native_tristate` | `QCheckBox` tristate | 2-state + tri | **Đủ** |
| `make_native_radio` + group | `QRadioButton` + `QButtonGroup` | group id | **Đủ** |
| `make_native_lineedit` / `make_native_password` / `make_textinput` | `QLineEdit` | placeholder, mask | **Đủ** (thiếu regex validator đầy đủ) |
| `make_native_combo` | `QComboBox` | popup open/close | **Đủ** (thiếu editable+completer) |
| `make_native_treecombo` | QComboBox+tree | combo tree popup | **Có** |
| `make_native_spinbox` | `QSpinBox` | min/max/step | **Đủ** (thiếu Double/DateTime spin) |
| `make_native_slider` / `make_slider` | `QSlider` | groove+value | **Đủ** |
| `make_dial` | `QDial` | ±135° arc | **Có** (Wave A) |
| `make_native_scrollbar` / `make_scrollbar` | `QScrollBar` | orient/page/step | **Đủ** |
| `make_switch` | styled checkbox | toggle | **Có** |
| `make_key_sequence` | `QKeySequenceEdit` | Ctrl/Alt/Shift/Meta chord | **Có** (Wave A) |
| `make_command_link` | `QCommandLinkButton` | label+description | **Có** (Wave A) |
| `make_datetime_edit` | `QDateTimeEdit` | format vi-VN + calendar popup | **Có** (Wave A) |

**Thiếu vs Qt trong nhóm này:** editable combo+completer, QDoubleSpinBox riêng, full validators, QDateTimeEdit variants đầy đủ.

#### 9.4.2 Display / feedback

| TkvUI | PyQt6 | Verdict |
|---|---|---|
| `make_native_progress` / `make_progress` | `QProgressBar` | **Đủ** |
| `make_native_tooltip` | `QToolTip` | **Đủ** |
| `make_toast` | không core | **TkvUI có sẵn** |
| `make_lcd` | `QLCDNumber` | **Có** (Wave A) |
| `make_metric_ring` / `make_sparkline` / Ant* | QChart (module riêng) | TkvUI bundle; Qt cần QtCharts |
| `make_ant_badge`/`dot`/`tag`/`avatar` | không core | niche design-system |
| `make_native_statusbar` | `QStatusBar` | **Đủ** |
| `make_tour_tip` | `QTour` (Qt ≥6.8) | **Có** — nhiều bản Qt cũ chưa có |

#### 9.4.3 Container / navigation / chrome

| TkvUI | PyQt6 | Wave | Verdict |
|---|---|---|---|
| `make_native_tabs` / `_closable` / `make_tabs` | `QTabWidget` | pre | **Đủ** (thiếu movable tabs) |
| `make_toolbox` | `QToolBox` | A | **Đủ** |
| `make_stacked` | `QStackedWidget` | A | **Đủ** |
| `make_split_view` / `make_native_splitter` | `QSplitter` | pre | **Đủ** ratio+orient |
| `make_card` / `notch` | Frame+layout | pre | OK |
| `make_bottom_sheet` / `make_navbar` | không core | pre | mobile-ish niche |
| `make_dialog` / `make_native_dialog` / `buttons` | `QDialog`+`QMessageBox` | pre | modal-exec **không headless** |
| `make_native_dock` / `make_native_dock_float` | `QDockWidget` | **B** | **float+tab+gutter** — thiếu save/restore geometry, z-order sâu |
| `make_native_mdi` + `tile_horizontal` | `QMdiArea` | **B** | **tile_h** — thiếu tile_grid, cascade, maximize |
| `make_native_ribbon` | QCommandBar / 3rd party | **B** | group tabs + large/small — thiếu gallery, contextual tabs |
| `make_native_propgrid` | Qt Property Browser examples | **B** | 2-col + category collapse + edit — thiếu multi-line/custom editors/sort |
| `make_native_wizard` | `QWizard` | A | linear next/back — thiếu watermark/graph register |
| `make_native_groupbox` / `groupcheck` | `QGroupBox` | pre | **Đủ** |
| `make_native_menubar` / `toolbar` / `contextmenu` / `systray` | QMenuBar/QToolBar/QMenu/QSystemTrayIcon | pre/**B** | QtAppPort 52/52; ContextMenu Wave B items+sep+activate — thiếu icons/submenu/shortcut labels |
| `make_native_richedit` | `QTextEdit`/`QTextDocument` | pre | **limited** — thua xa Qt rich text |
| `make_native_colorpicker` / `fontpicker` / `calendar` / `make_calendar` | QColorDialog/QFontDialog/QCalendarWidget | pre/A | picker widgets + NativeDlg |

#### 9.4.4 Item-view / model

| TkvUI | PyQt6 | Verdict |
|---|---|---|
| `make_native_table` + Data proxy sort/filter **76/76** | `QTableView`+`QSortFilterProxyModel` | **Đủ CRUD** |
| `make_native_tree` / `make_native_tree_multi` (expand, ctrl/shift, anchor range) | `QTreeView`/`QTreeWidget` | **Wave B multi-sel** — thiếu drag-drop, header resize, cell delegates |
| `make_native_listview` / `make_listview` | `QListView` | item_h×count virtualization nhẹ |
| SqlTableModel | `QSqlTableModel` | built-in vs Qt sql module |

#### 9.4.5 Media widgets (10)

Transport, SeekBar, Volume, Repeat, Shuffle, Speed, Playlist, Equalizer N-band, Spectrum, ABLoop — `media_selftest 80/80`.

QtMultimedia: engine codec/HW mạnh nhưng **UI player 10 widget không sẵn** như TkvUI. → **Hòa “UI form”, thua “decode/playback”**.

#### Tổng breadth

| | Qt | TkvUI | Tỷ lệ rough |
|---|---|---|---|
| Classes/constructors | **~1000** | **93** | **~9%** |
| Use-case CRUD/admin/IDE-ish | 100% | core + Wave B dock/MDI/tree/ribbon/propgrid + 2 Qt ports | coverage ~**70–80% use-case** (ước lượng theo Application Example + Tree/Dock port) |
| Vắng mặt nổi bật | — | WebView, QGraphicsView, QML/Quick, DataViz, SerialPort, Network widgets, PrintPreview đầy đủ | — |

**Không claim parity 1:1** (đã chốt LEVEL_PLAN).

---

### 9.5 Text render & shaping

| Hạng mục | TokenVector.UI | PyQt6 (Qt text) | Slint | egui | ImGui |
|---|---|---|---|---|---|
| Font | Bitmap 5×7 + **134 Việt precomposed** + TTF parser + i18n baked + emoji 12 BMP | System QFont full | fontdue/parley full OTF | fontdue/ab_glyph | stb_truetype |
| Atlas | Pre-baked + lazy-bake gid (HB wire L2) | glyph cache OS | GPU/atlas | texture atlas | dynamic |
| **Đo ASCII 21.6K chars** | **9.4 ms** | **13.7–18.1 ms** | chưa đo | chưa đo | chưa đo |
| Tốc độ | **~1.9× nhanh hơn PyQt** | baseline | — | — | — |
| Shaping thuần | Arabic/Thai/Deva/Bengali/Tamil **91/91** | subset | shaper riêng | limited | limited |
| **HarfBuzz** | **14.5 optional + wire `text_atlas_draw_shaped` (L2 DONE)**; thiếu DLL → fallback 157/157 skip-sạch | **Qt always-on HarfBuzz** | rustybuzz/HB crate | rustybuzz optional | user |
| Bidi UAX#9 | **194/194** | có | có | partial | partial |
| GSUB/GPOS đầy đủ | qua HB khi có DLL; fallback **không full** | full | full | HB crate | không |
| Wrap/ellipsis | có | QTextLayout full | full | basic | basic |
| Rich text | limited RichEdit | **QTextDocument** full | limited | markdown opt | markdown opt |
| Việt + IME | **134 precomposed + Telex/VNI 37/37** | phụ thuộc font+IME OS | không special | không | không |

**Verdict:** **Thắng ASCII 1.9×** + **niche Việt**; HB wire **đóng L2**; **thua** khi thiếu DLL vs Qt always-HB; **thua rich text** + hinting/variable/emoji color full. Còn: Thai/Deva box fallback, đo lại bench.

---

### 9.6 Layout engine

| | TkvUI.Layout | Qt | Slint | egui | ImGui |
|---|---|---|---|---|---|
| Flex row/col | **Có** + wrap + cross-align + justify | QBoxLayout | row/col | horizontal/vertical | SameLine |
| Grid + span | **Có** | QGridLayout | Grid | _table | Table |
| Stack | **Có** | QStackedLayout | Stacked | — | — |
| DPI helpers | **Có** | QScreen | logical px | pixels | pixels |
| Selftest | **50/50** | — | — | — | — |

**Verdict:** **Đủ form app**; Qt deep hơn (anchor/QML); Slint declarative ưu designer. **Hòa utility**.

---

### 9.7 Graphics / raster / effects

| | TkvUI | PyQt6 | Slint | egui | ImGui |
|---|---|---|---|---|---|
| Raster | **Tự viết** Bresenham, round-rect band-split, arc, poly, clip, blit — graphics **29/29** | QPainter → Qt engine | femtovg/GPU | mesh GPU | draw lists GPU |
| Pixel | **`list[i64]`** 8B/px (i32 hoãn) | QImage ~4B/px | RGBA8 | RGBA8 | RGBA8 |
| Effects | box, **half-res 2.1×**, kawase, backdrop, specular, shadow — effects **32/32** | QGraphicsBlurEffect | trung bình | ít built-in | user |
| GPU path | **stub device ops** | **Qt RHI** | **GPU** | **wgpu/glow production** | DX11/GL/Vulkan backend user |

**Verdict:** CPU widget paint **nhanh** (30 vs 43 ms/1000). **Thua GPU (L4)** — chưa present 1 frame GPU thật.

---

### 9.8 Input / events / focus / IME

| | TkvUI | PyQt6 | egui | ImGui |
|---|---|---|---|---|
| Hit-test | `hit_test_tree` topmost + per-widget `hit_*` | childAt + propagation | sense() | ItemHovered |
| Dispatcher | capture + gesture tap/pan/pinch — input **41/41** | full event loop + filters | context input | IO events |
| Focus | FocusManager Tab/Shift-Tab | QWidget.focus + tab order | focus state | NavInput |
| Chord/keys | KeySeq Wave A | QKeySequence full | modifiers | Nav+keys |
| **IME Việt** | **Telex/VNI Imm* — ime 37/37** | platform IME | limited | limited |
| Touch | GestureRecognizer | QTouchEvent | pointer | optional |

**Verdict:** Đủ desktop + touch contract; **IME Việt niche thắng**. Chưa drag-drop cross-widget / a11y actions.

---

### 9.9 Persistence — SQL

| Hạng mục | TkvUI.SQLite | PyQt6 QSQLITE | Slint/egui/ImGui |
|---|---|---|---|
| Engine | **Tự viết** page 4KB + B-tree + WAL-lite + dual-slot `TKVSQL1` | **SQLite full** | **không** |
| Selftest | **132/132** + crash matrix + **kill-9 ×12** | probe `sql.crud` | — |
| Features | CRUD, multi-WHERE, **JOIN**, snapshot tx, rowid index, SqlTableModel/Query/Relation | full SQL | — |
| File RT 1000 rows | **~81 ms** | **~195 ms** | — |
| In-mem total/rep | **~8 ms** | ~14 ms | — |
| Crash safety | dual-slot corrupt-1-slot OK | SQLite journal/WAL | — |
| Completeness | **subset CRUD mạnh** — không full SQL (CTE/window…) | SQLite de facto standard | — |

**Verdict: THẮNG niche + 2.4×** (ghi nhận fsync). **Thua completeness** vs SQLite. Slint/egui/ImGui **0** → độc quyền nhóm này.

---

### 9.10 PDF / In ấn

| | TkvUI | PyQt6 | Slint/egui/ImGui |
|---|---|---|---|
| PDF writer | **Tự viết** xref+Base14+paths+tables — printing **63/63** | QPdfWriter/Engine | **không** |
| Shell print | **`ShellExecuteA` live** | QPrinter + dialog full | — |
| Preview | PrintPreview cơ bản | **QPrintPreviewDialog** production | — |
| HTML→PDF | không | QTextDocument print | — |

**Verdict: Độc quyền có PDF+print** vs Slint/egui/ImGui. **Parity PDF file**; **thua print engine** (preview/printer enum).

---

### 9.11 Clipboard OS

| | TkvUI | PyQt6 | egui | ImGui |
|---|---|---|---|---|
| API | Win32 CF_TEXT+UNICODE **12/12** ASCII/Việt/emoji | QClipboard multi-OS | winit clipboard | backend |
| Phạm vi | **Win32 thật**, X11/Cocoa stub | Win/mac/X11/Wayland | multi | multi |

**Verdict:** Windows **đủ RT**; **thua multi-OS**.

---

### 9.12 Accessibility

| | TkvUI | PyQt6 | Slint/egui | Dear ImGui |
|---|---|---|---|---|
| Cây a11y | A11y model **41/41** role/label/value | QAccessible native | **AccessKit** shared | **không** → "blank window" |
| Bridge | HWND mirror + JSON + A11yBridge **94/94** + UIA/AT-SPI **33+22** | native | AccessKit adapters | — |
| Test | **KitTest 16/16** query+act | binding tests | **egui_kittest** | — |
| NVDA thật | Phase 9.1: chrome OK; **widget custom 0 utterance** | control đọc được | AccessKit → NVDA production | fail |
| Kế hoạch | **L7 C# COM shim UiaHost** hoặc AccessKit C | — | — | — |

**Verdict:** **Ở giữa** — có model+test, **chưa nói NVDA với widget custom**. Qt/AccessKit **thắng**. ImGui **thua cả ta**.

---

### 9.13 GPU

| | TkvUI | PyQt6 RHI | Slint | egui | ImGui |
|---|---|---|---|---|---|
| Surface | abstraction+probe Vulkan/D3D11/Metal — gpu **66/66** nhưng **ops stub** | RHI multi-backend | femtovg→GPU | **wgpu** production | DX11/GL/Vulkan phổ biến |
| Compute | chưa (plan L4 blur) | limited | không focus | wgpu compute | không focus |
| Present | ULW CPU blit | swapchain | GPU | GPU | GPU |

**Verdict: THUA (L4).** Chưa đo Slint/egui fps thật trên máy này.

---

### 9.14 WASM / Web

| | TkvUI | PyQt6 | Slint | egui | ImGui |
|---|---|---|---|---|---|
| Web | **WASI interp wasmtime DATA_OK** + browser canvas | Pyodide heavy | **wasm production** | **eframe wasm** | demos |
| AOT/size | AOT closed; AppBundle ~12.4 MB | PyODIDE tens MB | opt small | decent | good |
| App full UI web | partial (pure-compute + canvas frame) | partial | **full** | **full** | **full** |

**Verdict:** **Hòa tier interpreter** (Pyodide); **thua Slint/egui production wasm**.

---

### 9.15 Cross-platform

| Backend | TkvUI | PyQt6 | Slint | egui | ImGui |
|---|---|---|---|---|---|
| **Windows** | **Win32 ULW+DIB thật** (platform **82/82**, 2 HWND multi-window) | full | full | full | full |
| **Linux X11/Wayland** | **stub** — blocker **R7 `.so`** | full | full | full | full |
| **macOS Cocoa** | **stub** | full | full | full | full |
| **Android** | host contract (verify **SKIP**) | full | mobile | NDK user | backends |
| **iOS** | host contract (SKIP) | full | mobile | user | backends |
| detect_platform | probe thật 1..6 + env | QSysInfo | runtime | std::env | — |

**Verdict: THUA rõ (L8).** Chỉ Windows production-ready. **Acceptance:** `X11_OK` Xvfb khi R7 mở.

---

### 9.16 OS look / theme / DPI

| | TkvUI | PyQt6 | Slint | egui |
|---|---|---|---|---|
| Theme | OsPalette 13 roles + Light/Dark/HC — theme **79/79** + QSS-subset | **native style** + QSS + Fusion | Material/Fluent/Cupertino/**Native** | custom, không native Win chrome |
| Widgets | **41 native** self-draw (post Wave B) | 1:1 native đúng style | declarative styled | immediate styled |
| DPI | token DPI + validator | **QScreen DPR full** | logical px | physical+scale |
| Accent Win11 | **chưa** (L5 registry DWM) | style engine | themed | themed |
| Follow OS dark realtime | plan WM_SETTINGCHANGE | có | có | có |

**Verdict: Partial (L5).** Đủ “modern flat light/dark”; **chưa claim** “trông như Explorer”.

---

### 9.17 Hiệu năng — bench đầy đủ (BENCH.md chuẩn hoá)

| # | Benchmark | TkvUI | PyQt6 | Tỷ | Verdict |
|---|---|---|---|---|---|
| 6.2 | Text 21.6K chars/block | **9.4 ms** | 13.7–18.1 ms | **~1.9×** | **THẮNG** |
| 6.3 | Construct 1000 button | **<0.16 ms** | 12.6 ms | **~80×+** (timer floor) | **THẮNG** |
| 6.3 | Render 1000 button | **~30 ms** | ~43 ms | **~1.4×** | **THẮNG** |
| 6.4 | CRUD in-mem total/rep | **~8 ms** | ~14 ms | **~1.8×** | **THẮNG** |
| 6.4c | SQL file RT 1000 rows | **81 ms** | 195 ms | **~2.4×** | **THẮNG** |
| 6.1 | Memory load-text peak | **~46 MB** | **15.6 MB** | **thua ~3×** | **THUA** |
| — | Memory idle trivial | **11.0 MB** | 15.6 MB | **thắng** | **THẮNG** |
| — | Cold spawn exe | **~1.0 s** | **~0.2 s** | **thua 5×** | **THUA (L3)** |
| 6.5 | Blur half-res | 2.1× internal | — | — | nội bộ |
| — | MJPEG 160×120 | ~106 fps | — | — | niche |
| — | MJPEG 720p | ~2 fps | hw decode | — | **THUA realtime HD** |
| — | TKVV 720p path | ~100 fps đo | — | — | **THẮNG custom codec** |

Gate: `BENCH_STABLE_OK` median 3-run (chống flake GetTickCount ~16 ms).

---

### 9.18 Media / codec / playback

| | TkvUI | PyQt6 QtMultimedia | Slint/egui/ImGui |
|---|---|---|---|
| Demux MP4 | **Mp4 62/62** | ffmpeg stack | không / user |
| H.264 | **Baseline OpenH264 8/8 + RT 11/12** | **Main/High + HW** | user |
| GIF | **44/44** | QImageReader | limited |
| MJPEG | pure **44/44 + HD 6/6** | limited | — |
| TKVV custom | **56/56 + player 21/21 ~100fps@720p** | — | — |
| Audio clock | **chưa** (L6 WASAPI plan) | full | — |
| UI 10 widget | transport→abloop **80/80** | ít sẵn (hay QML) | — |
| MP4→TKVV ingest | **ClipPlayer 14/14** | — | — |

**Verdict:** Ingest+UI **đủ niche player nhỏ**; **thua Qt** HW/audio/adaptive. Không so Slint/egui (không media core).

---

### 9.19 Testing / CI / tooling

| | TkvUI | PyQt6 | Slint | egui | ImGui |
|---|---|---|---|---|---|
| Unit headless | **verify 55 case ~2200+ checks** + LOCALS_OK | pytest / Qt Test | cargo test | cargo test | ít |
| GUI e2e | **KitTest 16/16** | pytest-qt offscreen | CI demos | **kittest** official | manual |
| Fuzz | **Fuzz 7/7** | user | user | user | — |
| Bench | **bench_all + bench_stable OK** | side-by-side pyqt scripts | criterion | criterion | — |
| CI | `ci.yml` **static-only** — **chưa suite Win/Ubuntu full** | Qt CI massive | **Actions build+test+wasm** | Actions+kittest | Actions |
| Issue templates | **×3** | full | full | full | full |
| Designer | **DesignerApp headless+windowed** | Qt Designer production | **Live Preview + Figma** | inspector | — |
| Docs API | `docs/API.md` index | **apidox/qt.io** | book | rustdoc | docs |

**Verdict:** Unit **mạnh cho kích thước**; **thua CI e2e + designer tooling** (Slint Live Preview gold). L9 còn full suite trên Actions.

---

### 9.20 Packaging / deploy / startup

| | TkvUI | PyQt6 | Slint | egui |
|---|---|---|---|---|
| Single EXE | **549 KB–3.3 MB** (cần .NET FW) | PyInstaller **15–50 MB+** | static musl nhỏ | static nhỏ |
| Package | **NuGet** + **`.tkvpkg`+sha256** | pip | cargo/cmake | cargo |
| Verify package | `package.sh --verify` PKG_VERIFY_OK | pip hash | crates.io | crates.io |
| Cold start | **~1.0 s** AV+JIT | **~0.2 s** | native fast | native fast |
| Idle RAM | **11 MB** | 15.6 MB | MCU target thấp | thấp |

**Verdict:** **Deploy size THẮNG PyQt**; **startup THUA** native+PyQt. Slint thắng embedded RAM.

---

### 9.21 Documentation, onboarding, i18n

| | TkvUI | PyQt6 | Slint | egui |
|---|---|---|---|---|
| Quickstart | README 1 lệnh verify | pip + tutorials海量 | book + live preview | book + demos |
| Tutorial CRUD | **TUTORIAL_CRUD + CrudDemo** | official examples 1000+ | templates | demo crates |
| Screenshots | **2 PNG thật** + plan 3 GIF | gallery huge | studio | show case |
| Vietnamese docs | **README + comments VN** | multi-lang official | EN | EN |
| API ref | API.md summary 27 module | **Qt docs gold** | rustdoc | rustdoc |
| Roadmap public | LEVEL_PLAN + Roadmap + CHANGELOG | Qt company roadmap | public | public |

**Verdict:** Đủ internal+onboard; **thua scale**. L10: GIF + video + nuget.org.

---

### 9.22 Giới hạn compiler `.tkv` ảnh hưởng so sánh

| Gap | Ảnh hưởng | Trạng thái |
|---|---|---|
| Cấm ternary / `pass`; bitwise đã mở R5 | verbosity; MJPEG cũ chậm | R5 mở; ternary vẫn cấm |
| List append D1 → ToI32 crash | selftest dễ fail | **đã bypass** literal/`nv_alloc_*` |
| Struct lồng / fixed array | marshal Win32 phức tạp | chờ upstream |
| COM call-in (CCW) | UIA provider thật | **L7 → C# shim** |
| `.so` pinvoke | Linux/macOS/mobile | **L8 blocker R7** |
| Byte array record | Embed TTF vào PDF | 11.3 BLOCKED |
| NGEN/AOT (R10) | cold start L3 | upstream + `nGEN.ps1` local |
| P7.5 list-method order | API design | tuân thủ |

**Verdict:** Nhiều “thua đối thủ” **do compiler mẹ**, đã map sang L3/L7/L8 + shim C#.

---

### 9.23 Scorecard chi tiết theo hạng mục

| # | Hạng mục | TkvUI | Đối thủ mạnh nhất | Kết quả |
|---|---|---|---|---|
| 1 | Freedom license | MIT | egui/ImGui MIT | **Hòa best** |
| 2 | Self-host một stack | .tkv toàn stack | không ai | **Độc quyền** |
| 3 | Cộng đồng | 0 star | ImGui 76k | **Thua 100%** |
| 4 | Widget count | 93 | Qt ~1000 | **Thua ~10×** |
| 5 | Widget đủ CRUD/IDE form | Wave A+B + 2 ports | Qt | **Gần parity use-case** |
| 6 | Text ASCII speed | 9.4 ms | PyQt 18.1 | **Thắng 1.9×** |
| 7 | Text complex + HB | HB wire L2 optional | Qt always-HB | **Hòa có DLL / thua không DLL** |
| 8 | Việt/IME | precomposed+Telex/VNI | Qt phụ thuộc OS | **Thắng niche** |
| 9 | Rich text | limited | QTextDocument | **Thua** |
| 10 | Layout | flex/grid/stack | Qt/QML | **Hòa utility** |
| 11 | CPU render widget | 30 ms/1000 | PyQt 43 ms | **Thắng 1.4×** |
| 12 | GPU | stub | RHI/wgpu | **Thua** |
| 13 | SQL | built-in 132 + 2.4× | QSQLITE / Slint 0 | **Thắng niche+speed** |
| 14 | PDF+print | built-in 63 + shell | QPdf / Slint 0 | **Thắng có sẵn** |
| 15 | Clipboard | Win32 12/12 | QClipboard multi | **Thắng Win / thua multi** |
| 16 | A11y | mirror+KitTest, NVDA partial | Qt / AccessKit | **Thua production** |
| 17 | Media | Baseline + UI 10 + TKVV | QtMultimedia full | **Thua breadth / thắng UI** |
| 18 | WASM | WASI interp+canvas | Slint/egui prod | **Thua** |
| 19 | Cross-plat | Win32 only real | Qt/Slint/egui multi | **Thua** |
| 20 | OS look | self-drawn 41 + theme 79 | native Qt / Slint styles | **Partial** |
| 21 | Cold start | 1.0 s | 0.2 s | **Thua 5×** |
| 22 | Idle RAM | 11 MB | PyQt 15.6 / Slint MCU | **Thắng PyQt / thua MCU** |
| 23 | Load RAM text | 46 MB | 15.6 MB | **Thua 3×** |
| 24 | Deploy size | 0.5–1.6 MB | PyInstaller 50 MB | **Thắng** |
| 25 | Test headless | 55/0/2 ~2200 | Qt tests + probe | **Mạnh cho size** |
| 26 | CI | static only | full matrix | **Thua** |
| 27 | Designer | DesignerApp | Qt Designer + Slint preview | **Thua tooling** |
| 28 | Docs scale | đủ internal | qt.io gold | **Thua scale** |

---

### 9.24 “Ai thắng nếu app của bạn là…”

| Kiểu app | Thắng | Lý do (số trong file) |
|---|---|---|
| CRUD/admin **nhỏ, single EXE, tiếng Việt, built-in SQL/PDF** | **TkvUI** | 549 KB, SQL/PDF built-in, 93 widget đủ form, text 1.9×, MIT |
| Desktop **đa nền tảng Win/Mac/Linux** | **Qt / Slint / egui** | TkvUI X11/Cocoa stub |
| **GPU-heavy / game tool** | **egui / ImGui** | TkvUI GPU stub |
| **Embedded MCU** | **Slint** | RAM/size target |
| **A11y production NVDA** | **Qt / egui+AccessKit** | TkvUI 0 utterance widget |
| **~1000 class + rich text + charts** | **Qt** | breadth 10× |
| Research **self-hosted stack** | **TkvUI** | 1 ngôn ngữ raster→SQL→PDF→codec |
| Windows nội bộ, cần **startup 0.2 s** | **PyQt** hoặc đợi **L3 NGEN** | cold-start gap |

---

### 9.25 Khoảng cách còn lại (gap detail)

1. **Width:** 93 vs ~1000 — Wave C **depth** từng widget (validation, models, delegates, drag-drop) quan trọng hơn thêm constructor.
2. **Depth control:** editable combo, table cell delegates, tree drag, dock save/restore, MDI cascade/max — “mỏng nhưng có”.
3. **Platform:** chỉ Windows real — mở `.so` là khoá L8/L9 Ubuntu.
4. **Perception:** cold-start + load RAM — NGEN / R12 / lazy module.
5. **Trust:** public repo, CI green badge, 1 external issue.
6. **Media audio** + FFmpeg Main/High (L6).
7. **GPU compute** trước raster GPU (L4).
8. **NVDA** qua C# shim (L7).

---

> **Phương pháp:** mọi số TkvUI in ra từ selftest/bench đã chạy máy dev; số Slint/egui/ImGui lấy public docs — **chưa reproduce cùng workload** → không claim “nhanh hơn egui/Slint” khi chưa cài bench.

