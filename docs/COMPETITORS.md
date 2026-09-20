# So sánh repo TokenVector.UI với đối thủ (2026-09-19)

> Số sao GitHub lấy ngày 2026-09-19 (sẽ lỗi thời — tra lại khi dùng để claim).
> Mục đích: định vị trung thực + rút gap list cho repo. Không dùng để quảng cáo.

---

## 1. Headline

| | TokenVector.UI | PyQt6 | PySide6 | Slint | egui | Dear ImGui |
|---|---|---|---|---|---|---|
| Ngôn ngữ | .tkv → .NET IL | Python (binding Qt C++) | Python (binding Qt C++, official) | Rust/C++/JS/Python (.slint DSL) | Rust (immediate) | C++ (immediate) |
| License | MIT | GPL-3 / commercial | LGPL-3 / commercial | GPL-3 / commercial (royalty-free) | MIT/Apache-2.0 | MIT |
| Stars | (local, chưa public) | PyPI dl ~M/tháng | PyPI dl ~M/tháng | **23.867** | **30.609** | **76.254** |
| Tuổi / nhịp | 2026-, commit dày | từ 1998, release đều | official Qt Co, release đều | 2020-, active (push hôm nay) | 2019-, active | 2014-, active |
| Widget | ~50 (15 Ant + 16 native-look + media) | **~1000 classes Qt** | = PyQt6 | default set + Material/Fluent/Cupertino/Native styles | ~30 + custom dễ | ~60, tool-oriented |

---

## 2. So theo từng mặt (bằng chứng)

| Mặt | TkvUI (đo thật) | Đối thủ tốt nhất | Kết luận |
|---|---|---|---|
| Binary/deploy | suite 649 KB, app ~400 KB single EXE (cần .NET FW) | Slint (MCU < 300 KiB RAM, wasm subset font); egui wasm demo gọn | **Thắng trên Windows/.NET**; thua wafun đa nền |
| Startup/RAM | 31 ms / 27.6 MB peak | Slint (thiết kế cho MCU), egui (nhẹ) | Hòa về triết lý, chưa đo đối đầu 2 ông này |
| Text/shaping | bitmap 5×7 + TTF parser + bidi + Việt-first; **thua PyQt 21.8 vs 14.2 ms** | Qt (HarfBuzz/full), Slint (fontique+parley 0.10) | Thua rõ |
| Accessibility | **NVDA đọc 0 widget** (đo thật) | Qt native; **Slint/egui qua AccessKit** (egui bật mặc định) | Thua; ImGui cũng 0 (đồng cảnh) |
| Designer | form-model + app tương tác windowed | Qt Designer, Slint (Figma plugin + LSP + SlintPad live-preview) | Thua xa |
| GPU | rasterizer CPU | Qt RHI; Slint (GPU/DMA2D/framebuffer); egui (epaint tessellation) | Thua |
| PDF/SQL built-in | **Có (PDF writer + SQLite in-memory)** | Không ai có cả hai built-in | **Thắng (niche)** |
| WASM | interp chạy thật + canvas browser chạy thật; AOT closed | Slint/egui wasm demo production | Partial |
| Docs | README 94 dòng, tutorial 1, BENCH self-đo | Qt docs khổng lồ; Slint book + API; egui book + a11y guide | Thua xa |
| Test/CI | 30 selftest headless + CI static-only | Slint (GUI test automation trong CI), egui (**kittest**: test qua chính cây a11y!) | Thua về phương pháp |
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
| 3 | **Screenshots/GIF trong README** | Rẻ | 🔄 Pending |
| 4 | **Badges + releases có changelog theo tag** | Rẻ | ✅ DONE |
| 5 | **kittest-style test** (test qua cây a11y) | Vừa | ⏳ Pending (Phase 9.2) |
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
| Text render | ~25 ms | **21.8 ms** (PyQt 14.2 ms) | ❌ Thua ~35% |
| Widget creation | ~5 ms/widget | **<0.0002 ms** | ✅ Thắng |
| CRUD dev time | 2-4 h | ~1.5 p (thiếu feature) | ⚠️ Thua tinh thần |
| Binary deploy | PyInstaller 50MB+ | **370-650 KB single EXE** | ✅ Thắng |
| WASM deploy | Pyodide (interp) | **WASI interp + canvas** | ⚠️ Hòa |
| OS look | Native | **Self-drawn 16 widget** | ⚠️ Partial |
| Accessibility | Native UIA/AT-SPI | **NVDA: TkvUI vô hình** | ❌ Thua |

**Kết luận:** TokenVector.UI **thắng PyQt6 ở binary size, startup, memory, deploy size, CRUD throughput** — nhưng **thua ở text rendering, accessibility, OS look native, ecosystem**. Không thể claim "đánh bại PyQt6 mọi mặt" — chỉ thắng niche (binary size, deploy, Vietnamese-first).

---

## 📋 Next Steps (Theo thứ tự ưu tiên)

1. **Finalize COMPETITORS.md** ✅ (đang làm)
2. **12.3 CI Matrix** — GitHub Actions matrix
4. **Emoji/Color font support** (11.1 extension)
5. **Phase 11.2 Complex Script** — HarfBuzz full integration

---

> **Lưu ý:** File này chỉ dùng để tracking internal. Không dùng để marketing/public claim nếu chưa verify lại số liệu.