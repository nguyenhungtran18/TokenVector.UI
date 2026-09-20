## Kế hoạch san bằng — 5 mặt trận

### M1. SQL persistence (thua → thắng được nhanh nhất)

**Thiếu chính xác:** `sql_open` chỉ lưu chuỗi path (`TkvUI.SQLite.tkv:73`), không đọc/ghi file; không journal, không index bền vững, không driver ngoài.
**Kế hoạch:**
1. **Binary page format** (S): file header + pages 4KB + B-tree lá đơn giản cho rowid table; `sql_open` đọc, `sql_close`/`checkpoint` ghi. Tái dùng rowid-index trong RAM đã có.
2. **WAL-lite journal** (M): ghi append-only log trước khi sửa page, replay lúc open (crash-safe tối thiểu).
3. **SQL parser tối thiểu** (M): SELECT/WHERE/JOIN 1 cấp cho `sql_select` hiện chỉ lọc 1 điều kiện.
- *Xong khi:* CrudBench chạy được trên file, kill -9 giữa chừng không mất dữ liệu committed, bench file-backed ngang PyQt ±20%.

### M2. Typography (thua xa nhất, cần bền bỉ nhất)

**Thiếu chính xác:** không hinting/composite/kerning (ghi rõ ở `TkvUI.Text.tkv` TTF section), không HarfBuzz (Bidi tự viết mới tới X2–X8), emoji chỉ hộp placeholder, font CONFIG không có (font cố định trong code).
1. **Composite glyphs + kerning** (M): parse `glyf` composite + `kern`/`hmtx` advance đầy đủ trong TTF parser hiện có.
2. **Shaping**: Indic/Thai theo research doc đã có (`PHASE11_2_COMPLEX_SCRIPT.md`) → implement; Arabic presentation forms.
3. **Color emoji CBDT/COLR** (M): thay placeholder `FB_EMOJI` bằng rasterizet thật từ font.
4. **Fontconfig-lite** (S–M): font discovery theo OS + fallback chain có trọng số (thay charset cứng).
- *Xong khi:* render đoạn Arabic/Devanagari/Thai/emoji hỗn hợp pixel-đúng với Qt.

### M3. Widget breadth (50 → ~100)

**Thiếu chính xác:** không có item-view framework thật (model/delegate/view tách rời), dock/wizard/MDI/calendar/richtext, QSS-style theming (Theme hiện tại là record tĩnh).
1. **Item-view framework** (L): `AbstractItemModel` + delegate paint + virtualized view (tái dùng virtualization của ListView hiện có).
2. **Top-10 widget thiếu**: calendar, wizard, dock, MDI area, richtext edit, tree-combo, color picker, font dialog picker, statusbar-manager, systray (theo OS).
3. **Stylesheet engine** (M): selector + cascade tối thiểu thay record Theme tĩnh.
- *Xong khi:* port được 1 app Qt Widgets mẫu (ví dụ examples Qt) mà không thiếu control.

### M4. Cross-platform + GPU + Media (thua cấu trúc)

**Thiếu chính xác:** GPU 54 stubs, AT-SPI là file-bridge, macOS stubs, không decode media.
1. **Backend trừu tượng** (M): tách `PixelSurface` khỏi Win32 (hiện Platform.tkv gọi thẳng user32/GDI) thành interface Backend (Win32 / Cocoa / X11 / WASM-canvas).
2. **GPU thật** (L–XL): bắt đầu từ compute-shader blit/blur (thay vòng IL) rồi tới render pipeline; dùng pinvoke đã chứng minh được ở Platform.
3. **Media decode** (L): pinvoke ffmpeg (như đã làm Win32) — demux + decode + clock, widget Media hiện có chỉ việc hiển thị frame.
- *Xong khi:* cùng 1 app chạy Win + Linux + WASM; blur/render có đường GPU.

### M5. OS integration (a11y/print/dialog/IME)

**Thiếu chính xác:** UIA/AT-SPI là JSON-outbox (screen reader thật không đọc được), in ấn chỉ sinh PDF (không spooler), dialog/IME Win32-only.
1. **UIA provider thật** (M): implement `IRawElementProviderSimple` qua COM interop trên cây widget hiện có (cây + role/state đã có trong A11yBridge — chỉ thiếu COM plumbing).
2. **Print spooler** (S): gửi PDF đã sinh vào spooler OS (Win32 `StartDocPrinter`, CUPS Linux).
3. **AT-SPI D-Bus** (M): thay file-bridge bằng socket D-Bus thật (spec đã document trong code).
- *Xong khi:* NVDA/Narrator đọc được app; Orca trên Linux đọc được.

## Thứ tự đánh (phụ thuộc + ROI)

| Giai đoạn | Việc | Vì sao trước |
|---|---|---|
| **P1** | M1 persistence | Nền cho mọi app thật; engine + rowid đã sẵn; S–M |
| **P2** | M2.1 + M2.2 (composite/kerning + shaping) | Text là mặt tiền cạnh tranh; có sẵn parser để mở rộng |
| **P3** | M5.1 UIA provider | Mở cửa user-base 기업/assistive; cây a11y đã có |
| **P4** | M3 item-view + stylesheet | Cần cho app phức tạp sau khi có persistence |
| **P5** | M4 backend trừu tượng → GPU/media | Đắt nhất, làm sau khi core đã thắng trên Windows |
| **P6** | M2.3/M2.4 emoji + fontconfig, M5 còn lại | Hoàn thiện |

Muốn tôi bắt đầu **P1 (persistence)** ngay — thiết kế page format chi tiết trước rồi implement — hay anh muốn điều chỉnh thứ tự?