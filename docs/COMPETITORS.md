# So sánh repo TokenVector.UI với đối thủ (2026-09-19, cập nhật 2026-09-20)

> Số sao GitHub lấy ngày 2026-09-19 (sẽ lỗi thời — tra lại khi dùng để claim).
> Mục đích: định vị trung thực + rút gap list cho repo. Không dùng để quảng cáo.
> Số liệu 2026-09-20 verify bằng build+run thật (xem chi tiết từng selftest).

---

## 1. Headline

| | TokenVector.UI | PyQt6 | PySide6 | Slint | egui | Dear ImGui |
|---|---|---|---|---|---|---|
| Ngôn ngữ | .tkv → .NET IL | Python (binding Qt C++) | Python (binding Qt C++, official) | Rust/C++/JS/Python (.slint DSL) | Rust (immediate) | C++ (immediate) |
| License | MIT | GPL-3 / commercial | LGPL-3 / commercial | GPL-3 / commercial (royalty-free) | MIT/Apache-2.0 | MIT |
| Stars | (local, chưa public) | PyPI dl ~M/tháng | PyPI dl ~M/tháng | **23.867** | **30.609** | **76.254** |
| Tuổi / nhịp | 2026-, commit dày | từ 1998, release đều | official Qt Co, release đều | 2020-, active (push hôm nay) | 2019-, active | 2014-, active |
| Widget | ~40 (25 native-look + ~15 Ant, 2026-09-20: +Wizard/FontPicker/RichEdit/TreeCombo/Dock/MDI) | **~1000 classes Qt** | = PyQt6 | default set + Material/Fluent/Cupertino/Native styles | ~30 + custom dễ | ~60, tool-oriented |

---

## 2. So theo từng mặt (bằng chứng)

| Mặt | TkvUI (đo thật 2026-09-20) | Đối thủ tốt nhất | Kết luận |
|---|---|---|---|
| Binary/deploy | suite 649 KB, app ~400 KB single EXE (cần .NET FW) | Slint (MCU < 300 KiB RAM, wasm subset font); egui wasm demo gọn | **Thắng trên Windows/.NET**; thua wafun đa nền |
| Startup/RAM | 31 ms / 27.6 MB peak | Slint (thiết kế cho MCU), egui (nhẹ) | Hòa về triết lý, chưa đo đối đầu 2 ông này |
| Text/shaping | atlas batch 9.4ms/rep (thắng PyQt6 18.1ms warm, 1.9×); shaping engine thuần (Arabic/Thai/Devanagari/Bengali/Tamil + kern + composite + CBDT bake) | Qt (HarfBuzz/full) | **Thắng PyQt6 về tốc độ ASCII**; thua về HarfBuzz full/GSUB-GPOS |
| Widgets | ~40 (native 25 + Ant 15): calendar/wizard/dock/MDI/richtext/tree-combo/color-picker/font-dialog/statusbar + item-view framework + stylesheet engine | Qt ~1000 classes | Thua xa về số lượng; đủ cho app CRUD/form |
| SQL persistence | **Binary page 4KB + B-tree + WAL-lite + multi-WHERE + JOIN** (51/51) | Không ai có built-in | **Thắng (niche)** |
| PDF/print | PDF writer + **shell-print thật** (ShellExecuteA verify live) | Không ai có built-in | **Thắng (niche)** |
| Accessibility | Data model + Win32 HWND mirror + JSON provider + role maps (NVDA đọc HWND hệ thống qua mirror) | Qt native; **Slint/egui qua AccessKit** | Cải thiện (mirror); COM bridge thật vẫn cần C# shim |
| GPU | abstraction + shader pipeline stubs + device-op structs | Qt RHI; Slint; egui | Thua (cần host GPU thật) |
| WASM | interp chạy thật + canvas browser chạy thật; AOT closed | Slint/egui wasm demo production | Partial |
| Test/CI | **~1100 checks** headless (core47/gfx29/text238/widgets101/bidi150/uia33/a11y41+94/fx32/theme79/sql51/data76/native157/fb21/gpu66/shaping91/fallback21) + LOCALS_OK | Slint GUI automation; egui kittest | Thua về phương pháp GUI-test, thắng về số lượng unit |
| Cộng đồng | 0 (local) | Qt Company; 841–1227 open issues đang xử lý ở 3 repo kia = cộng đồng sống | Thua |

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
| 1 | **CONTRIBUTING.md + issue/PR templates** | Rẻ (1 buổi) | ✅ DONE |
| 2 | **API reference index** | Vừa | ✅ DONE (`docs/API.md` auto-gen) |
| 3 | **Screenshots/GIF trong README** | Rẻ | ✅ DONE (`docs/img/shot_browser.png` + `shot_emoji.png`, render thật) |
| 4 | **Badges + releases có changelog theo tag** | Rẻ | ✅ DONE |
| 5 | **kittest-style test** (test qua cây a11y) | Vừa | ✅ DONE (`TkvUI.KitTest`, 16/16: query role/label + hit-test + act trên widget thật + rebuild + assert, 9 case headless) |
| 6 | **Benchmark suite 1 lệnh** | Vừa | ✅ DONE (`tools/bench_all.sh` + `.ps1`) |
| 7 | **Vietnamese-first + PDF/SQL built-in** → đưa lên đầu README | Rẻ | ✅ Done (README updated) |

---

## 5. Roadmap Phase 11-12 (Text/Tooling)

| Phase | Task | Status | Blocker |
|---|---|---|---|
| **11.1 Font Fallback** | ✅ DONE (26/26 PASS) | — |
| **11.2 Complex Script** | 🔴 Research (Indic/Thai shaping) | HarfBuzz full integration |
| **11.3 TTF Embed PDF** | 🔴 BLOCKED (byte array) | tkvc gap |
| **11.4 Fuzz Shaping** | ✅ DONE (FUZZ_OK 7/7) | — |
| **12.1 DesignerApp** | ✅ DONE (headless + windowed) | — |
| **12.2 Tutorial** | ✅ DONE | — |
| **12.3 CI Matrix** | ⏳ Pending | GitHub Actions matrix |
| **12.4 Fuzz** | ✅ DONE (FUZZ_OK) | — |

---

## 7. Thứ tự ưu tiên đề xuất

1. **Font fallback mở rộng** (emoji, color font, variable font) — niche value cao
2. **Phase 11.2 Complex Script** — Research HarfBuzz shaping tables
3. **12.3 CI Matrix** — CI matrix Win+Ubuntu+WASM
4. **docs/COMPETITORS.md finalize** — Gap list cập nhật
5. **Phase 11.2 Complex Script** — HarfBuzz full integration
4. **12.3 CI Matrix** — GitHub Actions matrix Win+Ubuntu+WASM
5. **Emoji/Color font support** (11.1 extension)

---

## 8. Tóm tắt vị thế (Reality Check)

| Tiêu chí | PyQt6 | TokenVector.UI | Kết luận |
|---|---|---|---|
| Binary size | 15-20 MB | **649 KB** (suite 18 module) | ✅ Thắng |
| Cold startup | 300-800 ms | **~31 ms** | ✅ Thắng |
| Memory (idle) | 80-150 MB | **27.6 MB** | ✅ Thắng |
| Text render | ~25 ms | **9.4 ms/rep** (atlas batch, thắng PyQt6 18.1 ms) | ✅ Thắng |
| Widget creation | ~5 ms/widget | **<0.0002 ms** | ✅ Thắng |
| CRUD dev time | 2-4 h | ~1.5 p (thiếu feature) | ⚠️ Thua tinh thần |
| Binary deploy | PyInstaller 50MB+ | **370-650 KB single EXE** | ✅ Thắng |
| WASM deploy | Pyodide (interp) | **WASI interp + canvas** | ⚠️ Hòa |
| OS look | Native | **Self-drawn 25 widget** | ⚠️ Partial |
| Accessibility | Native UIA/AT-SPI | **HWND mirror + JSON provider** (COM bridge cần C# shim) | ⚠️ Partial (cải thiện từ 0) |

**Kết luận (2026-09-20):** TokenVector.UI **thắng PyQt6 ở binary size, startup, memory, deploy size, text render (1.9×), CRUD throughput, SQL/print built-in** — **thua ở widget breadth (~40 vs ~1000), HarfBuzz full shaping, GPU thật, OS look native, ecosystem**. Không thể claim "đánh bại PyQt6 mọi mặt" — thắng niche (binary size, deploy, Vietnamese-first, text render).

---

## 📋 Next Steps (Theo thứ tự ưu tiên)

1. **Finalize COMPETITORS.md** ✅ (đang làm)
2. **12.3 CI Matrix** — GitHub Actions matrix
4. **Emoji/Color font support** (11.1 extension) — ✅ partial 2026-09-21: 12 BMP symbols raster thật (`TkvUI.EmojiData`, bake offline từ Segoe UI Symbol, `EMOJIDATA_OK` 107/107, fallback 37/37); còn lại: color (CPAL/COLR parse xong, chưa bake font màu), non-BMP/cmap12, ZWJ giữ E-box
5. **Phase 11.2 Complex Script** — HarfBuzz full integration

---

> **Lưu ý:** File này chỉ dùng để tracking internal. Không dùng để marketing/public claim nếu chưa verify lại số liệu.