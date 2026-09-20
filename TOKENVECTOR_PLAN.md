# TokenVector.UI Chiến Thắng PyQt6 - Hành Trình Triển Khai

> **Mục tiêu:** Đánh bại PyQt6/PySide6 cho ứng dụng desktop standard (OS look, rapid dev) với binary < 1MB, no runtime, WASM AOT, text Việt/Bidi tự chủ.
> **Trang thai (2026-09-18):** Phase 1-5 + P2 XONG; verify 30 PASS / 0 FAIL; chi tiet tung phase duoi day.

---

## PHASE 0: FOUNDATION (✅ ĐÃ XONG - 782/782 checks PASS)

| Component | Lines | Tests | Status |
|-----------|-------|-------|--------|
| Core (buffer, color, surface, theme, pool) | 18K | 47/47 | ✅ |
| Graphics (2D, blur, gradient) | 17K | 29/29 | ✅ |
| Text (bitmap, Việt 134 glyph, TTF parser, i18n) | 113K | 160/160 | ✅ |
| Bidi/UAX#9 + HarfBuzz FFI | 56K | 117/122 | ✅ |
| GPU (Vulkan/D3D11/Metal + Shader Pipeline) | 24K | 66/66 | ✅ |
| A11y (tree model + JSON dump) | 15K | 41/41 | ✅ |
| Việt 134 glyph 5×7 | 11K | — | ✅ |
| I18n baked glyphs (Hebrew/Arabic/CJK) | 42K | — | ✅ |
| Platform (Win32 real + stubs) | 69K | 49/49 | ✅ |
| Widgets (15 Ant widgets + RenderLoop + FocusManager) | 122K | 101/101 | ✅ |
| Media (player, playlist, EQ, spectrum) | 53K | 80/80 | ✅ |

**Tổng:** 18 modules, 782 checks, 17/17 PASS

> **Kế hoạch bắt đầu ngay từ Phase 1** — Foundation đã hoàn thiện 100%.

---

## PHASE 1: WIDGET SET NATIVE-LOOK (Tuần 1-3)

**Mục tiêu:** 15 widget cơ bản với theme OS (Win32/Dark/Light/HighContrast).

| Widget | Lines | Effort | Dependency |
|--------|-------|--------|------------|
| Button (push, tool, check, radio, menu) | 300 | ⭐⭐⭐ | Theme engine |
| LineEdit (text, password, search, validator) | 400 | ⭐⭐⭐ | IME, validator |
| ComboBox (editable, model-based) | 300 | ⭐⭐⭐ | Model/View |
| TableView (sort, filter, selection, delegate) | 600 | ⭐⭐⭐⭐ | Model/View/Delegate |
| TreeView (expand/collapse, drag-drop) | 500 | ⭐⭐⭐⭐ | Model/View |
| TabWidget (closable, movable, icon) | 200 | ⭐⭐⭐ | Theme |
| Menu/MenuBar/ContextMenu | 300 | ⭐⭐⭐ | Theme, Action |
| ToolBar/ToolButton | 200 | ⭐⭐⭐ | Theme |
| Dialog (message, file, color, font, progress) | 400 | ⭐⭐⭐⭐ | Native stubs |
| ScrollArea/ScrollBar | 200 | ⭐⭐⭐ | Theme |
| Splitter/DockWidget | 400 | ⭐⭐⭐⭐ | Layout |
| ProgressBar/Slider/SpinBox/DateEdit | 400 | ⭐⭐⭐⭐ | Theme |
| ListView/IconView | 300 | ⭐⭐⭐ | Model/View |
| ToolTip/StatusTip/WhatThis | 100 | ⭐⭐ | Theme |

### Theme Engine (cần thiết trước hết)
| Thành phần | Mô tả |
|------------|-------|
| `Theme` class | Palette, font, metric, radius, shadow |
| `ThemeManager` | Load/save, OS detect, Dark/Light/HighContrast |
| `Style` class | Draw primitive, control, complex |
| Palette: Window, WindowText, Base, AlternateBase, ToolTipBase, ToolTipText, Text, Button, ButtonText, BrightText, Link, Highlight, HighlightedText |
| Metrics: ButtonHeight, IconSize, FrameWidth, ScrollBarWidth, TabBarHeight, MenuBarHeight |

**Deliverable:**
- `TkvUI.Theme.tkv` (~800 lines)
- `TkvUI.Widgets.Native.tkv` (~3000 lines)
- **Test:** 15 widgets chạy, theme switch Dark/Light
> **Ket qua:** `TkvUI.Theme.tkv` (701 dong, THEME 59/59) + `TkvUI.Widgets.Native.tkv` (1553 dong, **16 widget**, NATIVE 48/48). Switch Dark/Light/HC co test. Thieu: DateEdit, IconView, DockWidget, StatusTip/WhatThis, ColumnView.

---

## PHASE 2: MODEL/VIEW/DELEGATE + SQL (Tuần 4-6)

### 2.1 Model/View Core
| Class | Lines |
|-------|-------|
| `AbstractItemModel` | 300 |
| `AbstractListModel` | 100 |
| `AbstractTableModel` | 150 |
| `StandardItemModel` (Tree + table) | 400 |
| `SortFilterProxyModel` (sort, filter, recursive) | 400 |
| `StringListModel` | 50 |

### 2.2 Views
| View | Lines |
|------|-------|
| `ListView` (single column, icon/text, selection) | 200 |
| `TableView` (grid, sort, filter, selection, resize) | 400 |
| `TreeView` (hierarchical, expand/collapse, drag-drop) | 500 |
| `ColumnView` (Miller columns) | 200 |

### 2.3 Delegates
| Delegate | Lines |
|----------|-------|
| `ItemDelegate` (base paint/edit/sizeHint) | 200 |
| `StyledItemDelegate` (theme-aware paint) | 150 |
| `SpinBoxDelegate` (numeric editor) | 100 |
| `ComboBoxDelegate` (enum/choice editor) | 100 |
| `DateEditDelegate` (calendar popup) | 150 |

### 2.4 SQL/ORM (SQLite pinvoke)
| Component | Lines |
|-----------|-------|
| `SqliteConnection` (open/close, busy timeout) | 200 |
| `SqliteStatement` (prepare, bind, step, reset, column) | 300 |
| `SqliteTransaction` (begin/commit/rollback, savepoint) | 100 |
| `SqlTableModel` (live sync table ↔ SQLite) | 400 |
| `SqlQueryModel` (read-only query result) | 150 |
| `SqlRelation` (foreign key lookup) | 200 |

**Deliverable:**
- `TkvUI.Data.tkv` (~3500 lines)
- `TkvUI.SQLite.tkv` (~1200 lines)
- **Test:** CRUD app demo chạy được (add/edit/delete/query)
> **Ket qua:** `TkvUI.Data.tkv` (740 dong, DATA 31/31) + `TkvUI.SQLite.tkv` (672 dong, SQLITE 22/22) + `TkvUI.CrudDemo.tkv` (CRUD_TKVUI_OK 8/8). LUU Y: engine **in-memory, KHONG phai SQLite pinvoke** (thieu persistence file); ColumnView + calendar popup chua lam.

---

## PHASE 3: PRINTING/PDF (Tuần 7)

| Component | Lines | Mô tả |
|-----------|-------|-------|
| `PdfDocument` | 300 | Create, add page, save |
| `PdfPainter` | 400 | Draw text, rect, line, image, path |
| `PdfFont` | 300 | Embed TTF, subset, metrics |
| `PrintDialog` | 150 | Native stub (Win32 PrintDlg) |
| `PrintPreview` | 300 | Widget preview pages |
| `Printer` | 200 | QPrinter equivalent (margins, paper, orientation) |

**Deliverable:** `TkvUI.Printing.tkv` (~1500 lines)
- **Test:** Print preview + PDF export từ TableView
> **Ket qua:** `TkvUI.Printing.tkv` (1040 dong, PRINTING 47/47) + `TkvUI.PrintDemo.tkv` (PRINTDEMO_OK). PDF parse Python: 9/9 xref offset byte-exact. Thieu: **TTF embed stub**, raster image placeholder.

---

## PHASE 4: A11Y BRIDGE (Tuần 8)

| Platform | Approach | Blocker | Workaround |
|----------|----------|---------|------------|
| Win32 UIA | COM IRawElementProviderSimple | COM vtable | JSON dump + stub |
| Linux AT-SPI | D-Bus + libatspi | .so pinvoke | JSON dump + stub |
| macOS/iOS | NSAccessibility protocol | ObjC protocol | JSON dump + stub |
| Android | AccessibilityNodeInfo | JNI | JSON dump + stub |

**Deliverable:** `TkvUI.A11yBridge.tkv` (961 dong, ABRIDGE 63/63 — backend pick, role/state maps, UIA guarded, event router, live regions, 4 providers, reader detect, focus tracker, builders, dump that)
- Stub implementations + JSON dump API
- **Test:** NVDA/VoiceOver đọc tree model
> **Ket qua:** `TkvUI.A11yDemo.tkv` (ABDEMO_OK) + NVDA that 2026.1.1 (`docs/A11Y_NVDA.md`): WinForms control doc duoc, **cua so TkvUI vo hinh voi NVDA** (0 utterance) — can UIA provider that (9.2). VoiceOver/TalkBack/Orca CHUA test.

---

## PHASE 5: PACKAGING & TOOLING (Tuần 9-10)

| Tool | Mô tả | Blocker |
|------|-------|---------|
| `tkvc --package` | DONE `tools/pack_app.sh`: EXE don file 370-420KB + manifest + sha256 | (dist/printdemo, abdemo, designer) |
| `tkvc --wasm` | DONE interp (PASS wasmtime DATA_OK) + browser canvas (Chrome headless); **AOT CLOSED** | .NET 9 xoa workload |
| `tkvc --android` | SCRIPT DONE (`tools/pack_apk.sh`) — SKIP thuc te | thieu maui workload |
| `tkvc --ios` | SCRIPT DONE (`tools/pack_ipa.sh`) — SKIP (khong phai macOS) | can Mac that |
| **Designer App** | DONE 2 tang: headless model (DESIGNER_OK) + interactive windowed (DESIGNER_APP_OK, live OK) | (example) |

---

## TIMELINE & MILESTONES

| Phase | Tuần | Deliverable | Test Target |
|-------|------|-------------|-------------|
| **Phase 1: Native Widgets** | DONE `TkvUI.Widgets.Native` + `Theme` | 16 widgets 48/48, switch D/L/HC |
| **Phase 2: Model/View/Delegate** | DONE `TkvUI.Data` + `SQLite` (in-memory) | CrudDemo 8/8 |
| **Phase 3: Printing/PDF** | DONE `TkvUI.Printing` | preview + export + xref byte-exact |
| **Phase 4: A11y Bridge** | DONE `TkvUI.A11yBridge` | JSON dump + NVDA evidence (vo hinh) |
| **Phase 5: Tooling** | DONE pack_app/wasm-interp+canvas/apk+ipa-scripts/DesignerApp | EXE + wasmtime PASS |

**Tổng: ~10 tuần (~2.5 tháng)**

---

## SUCCESS CRITERIA: "ĐÁNH BẠI PyQt6"

| Benchmark | PyQt6 | TokenVector.UI Target | Measurement |
|-----------|-------|----------------------|-------------|
| **Binary size** | 15-20 MB | **649 KB** (suite 18 module; app ~400KB) DONE | dist + build sizes |
| **Cold startup** | 300-800 ms | **~31 ms** trivial / 40-60 ms selftest DONE | measure-command |
| **Memory (idle)** | 80-150 MB | **27.6 MB** vs PyQt 38.5 MB DONE | BENCH.md 6.1 |
| **Text render (atlas)** | ~25 ms | **21.8 vs 14.2 ms — THUA** | BENCH.md 6.2 |
| **Widget creation** | ~5 ms/widget | **<0.0002 vs 0.0123**, ca 2 qua DONE | BENCH.md 6.3 |
| **CRUD app dev time** | 2-4 gio | ca 2 <2h nhung **PyQt nhanh/du hon — THUA tinh than** | BENCH.md 6.4 |
| **Binary deploy** | PyInstaller 50MB+ | **370-650 KB single EXE** (can .NET FW) DONE | pack_app.sh |
| **WASM deploy** | Pyodide (interp) | **interp chay that** (wasmtime); **AOT CLOSED** | WASM_STATUS.md |
| **OS look** | Native | theme + 16 widget **tu ve**; khong control native — PARTIAL | theme switch test |
| **Accessibility** | Native UIA/AT-SPI | NVDA: control that doc duoc, **TkvUI vo hinh** — PARTIAL | A11Y_NVDA.md |

---

## RESOURCE REQUIREMENTS

| Role | Số lượng | Note |
|------|----------|------|
| **Core dev (compiler + runtime)** | 1 | Compiler fixes cho gaps |
| **UI dev (widgets/theme)** | 1 | Phase 1-2 |
| **Data dev (SQL/Model/View)** | 1 | Phase 2 |
| **Platform specialist (Win32)** | 0.5 | Win32 printing, A11y |
| **Platform specialist (Linux/macOS)** | 0.5 | X11/Wayland/Cocoa stubs |
| **WASM specialist** | 0.5 | Phase 5 |

**Total: ~4.5 FTE × 10 weeks = 45 nhân-tuần**

---

## RISK MITIGATION

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Compiler gaps không fix kịp | High | High | Workaround stubs + workaround tests |
| Theme engine không OS-native | Medium | High | Fallback: custom theme + OS detect |
| A11y bridge không xong | High | Medium | JSON dump + stub là MVP |
| WASM AOT .NET 9 delay | Low | Medium | Fallback: interpreter mode |
| Hiring dev đủ skill | Medium | High | Cross-train, doc tốt |

---

## GO/NO-GO DECISION

**GO** nếu:
- [x] Phase 1 Widgets xong 80% DONE (16 widgets, 48/48)
- [x] Phase 2 Model/View/Delegate DONE (CrudDemo 8/8)
- [x] Theme engine switch Dark/Light/HighContrast DONE (co test)
- [x] CRUD demo < 2 gio DONE (ca 2 phut do, chi tiet BENCH.md 6.4)

**NO-GO** nếu:
- Compiler gaps không fix được sau 4 weeks
- Widget set không cover 80% use case
- Binary size > 2MB

---

## TRANG THAI: DA TRIEN KHAI XONG (2026-09-18)

Phase 1-5 + P2 (6, 7.3, 8.3-8.5, 9.1, 12.1, 12.2, 12.4) hoan thanh, verify **30 PASS / 0 FAIL**.
File nay giu nguyen de doi chieu ke hoach goc; tien do P2 xem `TOKENVECTOR_PLAN_P2.md`.
GO/NO-GO: khong dieu kien NO-GO nao kich hoat (binary 649KB < 2MB, gaps co workaround).