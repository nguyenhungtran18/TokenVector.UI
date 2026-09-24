# Compiler Gaps (tkvc) — Tổng hợp từ thực tế build/run

> Nguồn sự thật cho mọi giới hạn compiler gặp trong quá trình phát triển
> TokenVector.UI (2026-09-18 → 2026-09-20). Mỗi mục: triệu chứng thật,
> cách tái hiện, workaround đang dùng, và đề xuất fix upstream.
> Tham chiếu thêm: `DEVELOPMENT_PLAN.md §3`, `docs/TkvUI.Roadmap.md §0`.
> Spec đầy đủ + acceptance test: `docs/UPSTREAM_REQUIREMENTS.md` (R1–R12).

---

## §0. Trạng thái ticket maintainer (vòng verify 23/09 tối, gộp từ `COMPILER_FIX_LIST.md`)

> Mỗi mục đã đối chiếu bằng probe chạy thật trên exe. Mục nào mở rồi thì
> xuống archive (§D), không hỏi lại.

### §0.1. Đã có câu trả lời (không cần sửa gì thêm)

- **Q-1. Ngữ nghĩa `len()`** — ✅ CHỦ Ý, GIỮ CHARS. Maintainer xác nhận giữ
  chars. Migration của repo đứng yên, mục này đóng.

### §0.2. Còn lại (sau vòng verify 23/09 tối)

- **F-2. Struct marshal qua pinvoke (R1)** — ✅ MỞ, VERIFY ĐỘC LẬP.
  Syntax thật (mò bằng probe + message lỗi): `__tkv_struct__` dict +
  `new_Point()` + pinvoke param `"Point*"` + đọc/ghi `p.x`. Bẫy đã gặp:
  khai list string thì lờ im lặng; `Point(0,0)` không tồn tại; truyền `list`
  báo sai kiểu (message tiếng Việt chỉ rõ cần biến kiểu struct).
  Verify: `GetCursorPos` rc=1 + tọa độ thật. Giới hạn còn lại (theo
  maintainer, chưa tự kiểm): field chỉ scalar blittable — struct lồng /
  fixed-array chưa có. `SBufferInfo.pData[3]` của OpenH264 rơi vào giới hạn
  này → đường **shim C# vẫn là chính** cho H.264.
- **F-4 còn lại. Expose COM / struct params (R8-phần-2, thu hẹp dần).**
  Vtable CALLS đã mở + verify độc lập (AddRef d=1) — xong. Theo maintainer:
  expose COM đã mở (F4c cũ, `com_call0(p, 3)` → 7, `this` nguyên vẹn) —
  repo CHƯA TỰ VERIFY, để ticket probe tiếp theo. Còn thiếu sau đó: method
  có struct params (nay R1 đã mở cho scalar — kiểm tiếp khi cần).
- **F-3 còn lại. Form full-identity inline** — ✅ SỬA XONG, VERIFY 50.
  Tuple đã chạy từ trước (PROBER3A_OK); nay full-inline cũng parse đúng
  (tên, token, version) và chạy ra 50. Cả 3 form xanh.
- **R11. Diagnostics** — THEO MAINTAINER ĐÃ CÓ (chưa tự kiểm). Biến
  undeclared → lỗi compile kèm số dòng; >240 locals → chặn rõ ràng. Repo
  giữ `tools/check_locals.py` chạy tay cho chắc; sẽ bỏ khi nào tự verify
  thấy message mới.

### §0.3. Chờ môi trường, không phải compiler (ghi nhận)

- **R7 runtime Linux**: build đã chấp nhận `.so`; chưa kiểm runtime vì thiếu
  máy Linux. Cần CI/runner Linux hoặc xác nhận từ maintainer.
- **R3 trên máy khác**: tuple đã xanh ở đây; nếu maintainer cần matrix
  (x86/x64, .NET Framework/Core) thì báo để chạy thêm.

---

## Nhóm A — Chặn tính năng lớn (cần upstream mới mở được)

### A1. Integer literal/typeflow 64-bit (ngưỡng 2³¹)
- **Triệu chứng:** mọi giá trị nguyên ≥ 2147483648 đều nổ, ở 1 trong 3 tầng:
  - Compile (linter/codegen): `KeyError` / `SyntaxError` khi fold hằng.
  - Runtime: `System.OverflowException: gia tri int qua lon: khong vua int64`
    tại `TkvInt.ToI64` (vd `fd_reg_open_key`, probe `nv_render_probe`).
  - `int("2147483648")` ném `System.Number.ParseInt32` (parse bằng Int32).
- **Đã thử (đều fail):** literal thập phân, hex `0x80000002` (linter cấm),
  cộng dồn runtime (`1073741824+1073741824`, `1000000000+...`), doubling
  loop ×31, string parse, `Int64.Parse` (không tồn tại trong tkv).
- **Workaround:** stub headless-safe trả 0 (pattern chung của repo);
  pinvoke `fd_pinv_*` giữ khai báo sẵn, chỉ thay body khi upstream sửa.
- **Unblock khi sửa:** registry scan (HKEY_*), Vulkan `vkCreateInstance`/
  `vkCreateDevice` (handle), mọi pinvoke param >2³¹.
- **Đề xuất upstream:** cho hex literal + hậu tố kiểu i64; typeflow i64 đúng
  qua `TkvInt.ToI64` (giữ bit pattern, không ném với giá trị vừa i64).

### A2. Đọc out-buffer / out-handle (FFI 2 chiều)
- **Triệu chứng:** không có primitive cấp phát + đọc bộ nhớ native trả về
  qua con trỏ out-param. Đã vét 11 cơ chế (2026-09-18), chốt BLOCKED.
- **Các chỗ dính:** Vulkan `vkEnumeratePhysicalDevices` (device array),
  `RegQueryValueExA` (đọc tên file font), XImage/event struct (X11),
  HarfBuzz multi-char (`hb_buffer_get_glyph_infos/positions` stride mismatch),
  `GetTextExtentPoint32A` (đọc SIZE struct → phải fallback advance TB).
- **Workaround:** stub trả 0 + logic single-char/fallback
  (HarfBuzz single-char shaping đúng; `font_measure` fallback 12px/char).
- **Đề xuất upstream:** primitive `alloc(n)` + `read_u8/u16/u32/i32/u64(addr)`
  + `memcpy`; cho `extern_method` reference đúng identity assembly thật
  (hiện gán cứng Framework 4.0.0.0/b77a → DLL managed riêng FileLoadException).

### A3. Pinvoke `.so`/`.dylib` (Linux/macOS)
- **Triệu chứng:** linter bắt buộc `.dll`, từ chối cứng `libvulkan.so`,
  `libatspi.so`, `.dylib` (kể cả `--no-lint` — flag không tồn tại).
- **Unblock khi sửa:** X11/Wayland thật, AT-SPI D-Bus, Android/iOS pixel thật
  (kèm `memcpy`/`Marshal.WriteByte`).
- **Workaround:** stub handle-gated + headless-safe (`X11Platform`,
  `CocoaPlatform`, `AtspiProvider`).

### A4. COM vtable / ObjC msgSend / JNI trực tiếp
- **Triệu chứng:** không gọi được COM (`IRawElementProviderSimple`),
  ObjC protocol (`NSAccessibility`), JNI (`AccessibilityNodeInfo`).
- **Workaround (kiến trúc chính thức):** .tkv làm **data provider**
  (tree JSON + Win32 HWND mirror + outbox events), **host shim** (C#/Swift/Java)
  implement native API. Win32 HWND mirror (`uia_mirror_build`) cho UIA đọc
  được ngay không cần COM.
- **Đề xuất upstream:** không bắt buộc — kiến trúc host-driven đã đủ;
  chỉ cần A1+A2 để shim mạnh hơn.

---

## Nhóm B — Thiếu toán tử/hàm (có workaround rẻ)

### B1. Bitwise `&`, `>>`, `<<`
- **Triệu chứng:** `&` không compile; `<<` parse fail (`expect_op`).
- **Workaround:** helpers `bit1/bit2/bit4/bit8/bit16/bit32`
  (`v % 2`, `//` + `%`), `get_bit_mask(col)`. Đã đo: `//`/`%` chi phối
  nhưng atlas vẫn đạt 9.4ms/rep (thắng PyQt6 1.9×).
- **Đo mới 2026-09-22 (MJPEG):** bit-reader `//`+`%` + vòng lặp Huffman/IDCT
  thuần khiến 720p decode mất 453ms (~2fps; profile: Huffman ~9%, IDCT
  float ~60%). Kể cả optimize hết (AAN + reuse + lookahead ≈ 2.5×) cũng
  chỉ ~5fps@720p — realtime HD cần bitwise/SIMD, không có đường vòng.
- **Đề xuất upstream:** `&`, `|`, `>>`, `<<`, mask operators
  (kỳ vọng blur/blend nhanh thêm ~1.5–2×; codec nhanh ~10×).

### B2. `chr()` không tồn tại
- **Triệu chứng:** `SyntaxError: ham 'chr' khong ton tai`.
- **Workaround:** lookup table ASCII 0–127 bằng `if` chain
  (`char_code_from_i64` trong `TkvUI.SQLite.tkv`).
- **Đề xuất upstream:** builtin `chr(code)`.

### B3. `int()` parse bằng Int32
- **Triệu chứng:** `int("2147483648")` ném `ParseInt32` (thấy ở FontDiscovery).
- **Workaround:** tránh parse số >2³¹; dùng arithmetic nhỏ (vẫn dính A1
  nếu kết quả ≥2³¹).
- **Đề xuất upstream:** `int()` parse 64-bit (hoặc `int64()` riêng).

---

## Nhóm C — Ràng buộc cú pháp (linter/codegen)

### C1. Single-line `if` bị cấm
- Mọi `if` phải multi-line. Single-line `if x: ...` → lỗi compile.

### C2. Ternary `a if cond else b` bị cấm
- Linter: `ternary expression ... dung cu phap rieng cua DSL: 'cond ? a : b'`
  (nhưng `? :` cũng không được document rõ). Workaround: `if/else` block
  với biến tạm (`ok = 0; if cond: ok = 1`).

### C3. `pass` không parse được
- `SyntaxError: khong dich duoc dong: 'pass'`. Workaround: xóa dòng
  (block `if` rỗng vẫn compile được nếu chỉ còn comment... thực tế: bỏ `pass`).

### C4. Raw string `r"..."` không hỗ trợ
- Workaround: escape thủ công (`"Software\\Microsoft\\..."`).

### C5. Hex/underscore number literal bị cấm
- `0x1F`, `1_000`, `1e10` → linter từ chối. Workaround: decimal thuần
  (đau ở hằng Win32/TTF tag — phải tính tay, dễ sai như tag `'kern'`
  1801810539 vs đúng 1801810542; nên verify bằng công thức
  `b0*16777216+b1*65536+b2*256+b3`).

### C6. String constant ở module-level không ổn định
- `FONT_DIR_SYSTEM = "Fonts"` ở module-level gây `KeyError` lúc infer.
  Workaround: bọc trong hàm (`def FONT_DIR_SYSTEM() -> "str": return "Fonts"`).
  (Integer constants module-level như `ATLAS_COUNT = 95` vẫn OK.)

### C7. Biến global mutable ở module-level bị cấm
- Không `global`, không list/dict mutable module-level (`_HKEY_VALUES = []`
  → lỗi `Assign`). Workaround: function-scoped locals, caller-owned lists,
  helper trả list mới (`vi_all_pairs()`, `_hkey_values()`).

### C8. Tên pinvoke/extern trùng builtin
- `fd_reg_open_key` (pinvoke) trùng tên Mgọi wrapper → `trung ten voi builtin`.
  Workaround: prefix pinvoke `fd_pinv_*`, wrapper `fd_*`.

### C9. Param extern chỉ nhận kiểu cơ bản
- `list[i64]` làm param `__tkv_extern_method__` → lỗi
  (`chi ho tro ['bool','f32','f64','i32','i64','object','str',...]`).
  Workaround: binary I/O qua `str` (`WriteAllText`/`ReadAllText`, mỗi char = 1 byte).

### C10. Entry point CLI chỉ nhận trả về vô hướng
- Entry trả `list` → lỗi (`CHI ho tro return VO HUONG... hoac tuple`).
  Workaround: entry trả `str` status (`"TEXT_OK"`), data qua file/buffer.

### C11. Attribute access trên biểu thức phức tạp bị cấm
- `dk.left_rect().x` (`.x` trên kết quả method-call) → lỗi
  (`'.x' sau 1 bieu thuc phuc tap... CHI ho tro khi... handle-type`).
- Workaround: gán biến trung gian trước (`lr = dk.left_rect()` rồi `lr.x`).
  (Phát hiện ở NativeDockPanel, 2026-09-20.)

### C12. Pinvoke không được gọi trần (standalone statement)
- `win_destroy_window(wh)` / `tray_wsprintf_s(...)` dạng lệnh độc lập →
  lỗi `dung o dang lenh doc lap (khong gan bien) - khong tim thay ham`.
- Workaround: luôn gán (`rc = ...`, `drc = ...`), kể cả khi không dùng.
  (Hàm thường như `mem_free`, `draw_string` gọi trần vẫn OK.)
  (Phát hiện ở NativeSysTray, 2026-09-20.)

---

## Nhóm D — Suy luận kiểu mong manh (đã có workaround, ghi để tránh)

### D1. Local `list` suy kiểu sai khi truyền vào method
- **Case:** `rbuf = []` + `append(0)` suy thành `List<TkvInt>`(?) thay vì
  `List<Int64>`; call `sbr.render(rbuf, ...)` sinh `TkvInt::ToI64` lên cả
  list → `OverflowException` (vụ NativeStatusBar/tab render).
- **Tinh chỉnh (NativeTreeCombo, 2026-09-20):** method + `list[i32]` inline
  (`tcf = []; tcf.append(1)`) crash NGAY CẢ trên class cũ đã chứng minh
  (`NativeTreeView.toggle`), trong khi `flags = [int(0), int(0)]` literal
  thì xanh. Quy tắc thực nghiệm:
  - `x = []; x.append(int)` → SAI cho method params `list[i32]/list[i64]`
    (functions vẫn OK; method + `list[str]` OK).
  - `x = [int(0), ...]` literal → ĐÚNG.
  - `x = []; x.append("str")` → ĐÚNG cho `list[str]`.
  - Helper có return-type tường minh → ĐÚNG mọi kiểu.
- **Workaround (đã chứng minh ×2):** helper `nv_alloc_buf(n) -> "list[i64]"`,
  `nv_alloc_i32`, hoặc literal `[int(...), ...]`.
- **Đề xuất upstream:** annotation biến local (`x: "list[i64]" = []`)
  hoặc suy kiểu từ call-site.

### D2. Record arity inference mong manh
- **Case:** thêm field thứ 9 (`kern_data`) vào `TtfFont` → compiler vẫn báo
  record "can 8 tham so" dù khai báo đủ 9 field + 9 init params
  (trong khi `GlyphAtlas` 12 field compile bình thường). Revert về 8 + truyền
  `kern_data` qua param tường minh thì hết.
- **Workaround:** giữ record gọn; thread dữ liệu phụ qua function params
  (đúng style `hmtx`/`cmap` đã làm).
- **Đề xuất upstream:** kiểm tra lại đếm field/init-param của record.

### D3. Tên biến chưa khai báo không báo lỗi
- **Case:** probe dùng biến `mode` chưa định nghĩa vẫn **compile + chạy**
  (compiler tự cho giá trị mặc định?). Cực kỳ nguy hiểm cho correctness.
- **Đề xuất upstream:** lỗi `bien '<name>' chua duoc khai bao` ở compile-time.

### D4. Giới hạn locals (~256, slot aliasing)
- **Case đã chứng minh:** `text_selftest` 272 locals → crash ngẫu nhiên,
  fix bằng tách hàm; checker `tools/check_locals.py` (limit 240).
- **Workaround:** giữ mỗi function <240 locals; chạy checker sau mỗi build.

### D5. Arity dispatch theo tên (nghi ngờ, chưa kết luận)
- 20 method cùng tên `render` khác arity; IL `callvirt` resolve đúng class,
  nhưng hành vi crash tương quan với arity (4 OK / 6 crash / 10 OK trong
  module khác). Chưa isolate dứt điểm; workaround hiện tại (typed buffer)
  đã xanh nên hạ ưu tiên.

### D6. Method trùng tên BCL resolve sai trong vòng lặp (ĐÃ ISOLATE 2026-09-22)
- **Vấn đề:** gọi `record.insert(...)` (trùng `List<T>.Insert`) khi receiver
  và arg đều là param, đặt TRONG thân `while`, compiler emit IL `callvirt
  ... NativeRichEdit::Insert(int32, !0)` → `MissingMethodException` lúc chạy.
  Cùng call ở straight-line (param hay local đều được) emit đúng
  `'insert'(List<string>, string)`.
- **Case đã chứng minh:** probe tạm (đã xóa sau isolate): straight-line đúng
  cả 3 biến thể (literal/var/slice); while-loop sai cả 3 biến thể (if/else,
  sequential-if, literal) — đọc IL trực tiếp. `newline` (không trùng tên BCL)
  trong cùng loop vẫn đúng → trigger là trùng tên BCL + trong loop.
- **Workaround:** wrapper gọi thẳng-hàng (`qa_put1` bind receiver sang local
  rồi gọi `ed.insert`), loop gọi wrapper. Đã xanh 52/52 ở
  `examples/TkvUI.QtAppPort.tkv`.
- **Liên quan D5:** có thể cùng họ dispatch-theo-tên, nhưng D6 đã isolate dứt
  điểm và có workaround chắc chắn (không cần chờ upstream).
- **Update 2026-09-22: ĐÃ SỬA upstream** (tkvc build 22:14) — `edit.insert`
  trong loop emit đúng, workaround `qa_put1` trong QtAppPort đã gỡ, 52/52
  giữ xanh.

---

## Nhóm E — Tooling/packaging (ngoài compiler core)

| # | Gap | Workaround hiện tại |
|---|-----|---------------------|
| E1 | Không `--target library` (DLL hiện là exe đổi tên) | Đổi tên exe → dll trong nupkg |
| E2 | Không `.subsystem 0x0002` (zero-console) | Chấp nhận console kèm theo |
| E3 | Không primitive spawn/wait, socket | Giữ stub; D-Bus/AT-SPI qua file-bridge |
| E4 | Không `Marshal`/`memcpy` | Vòng IL thuần (chậm hơn nhưng đúng) |
| E5 | ECMA key không trích được (delay-sign) | Shim C# 20 dòng khi upstream sửa identity |

## Nhóm F — Bộ nhớ & triển khai (nguồn: BENCH.md Phụ lục M1)

Bối cảnh đo thật: `bench_text.exe` peak ~46MB vs PyQt6 ~15.6MB.
Breakdown: floor CLR ~10MB + pixel `list[i64]` 8B/px (~16MB backing, gồm
doubling waste ~7MB) + ~19MB chưa tách được (cần profiler/NGEN).

### F1. Primitive `reserve(n)` (preallocate list capacity)
- **Vấn đề:** `buf = []; while i < n: buf.append(0)` gây doubling waste
  ~7MB cho surface 1.088M px (slope đo 8B/elem, waste ~7MB).
- **Đã thử:** `[0]*n` → compiler báo lỗi, không có cách làm từ phía user.
- **Workaround:** không có (scratch reuse chỉ giảm churn gen0, không giảm peak).
- **Đề xuất upstream:** `reserve(lst, n)` / list constructor có capacity.

### F2. Triển khai NGEN / AOT thật
- **Vấn đề:** ~19MB (atlas + glyph tables + strings + JIT heap) chưa tách
  được — cần CLR profiler/NGEN, máy không có elevation để xác minh.
- **Đề xuất upstream:** hỗ trợ NGEN deployment hoặc `--target` native.

### F3. Migration pixel `list[i64]` → `list[i32]` (ĐÃ ĐÁNH GIÁ → HOÃN)
- **Kết luận đo:** chỉ cứu ~4.5MB (→ ~41MB, vẫn thua 2.6×) với rủi ro
  refactor toàn repo (mọi `buf` signature, atlas, blend). **Không làm.**
- Ghi ở đây để khỏi đào lại.

---

## Ma trận unblock (sửa 1 gap → mở nhiều mặt trận)

| Fix upstream | M1 persistence | M2 shaping/emoji | M3 widgets | M4 GPU/media | M5 a11y/print |
|---|---|---|---|---|---|
| A1 (i64 literals/typeflow) | WAL LSN/page_no lớn | — | — | Vulkan handles | HKEY_* registry |
| A2 (out-buffer read) | WAL replay verify | HarfBuzz multi-char | — | `vkEnumerate*`, XImage | `RegQueryValueEx`, AT-SPI |
| A3 (`.so`/`.dylib`) | — | — | — | X11/Wayland/media | AT-SPI D-Bus |
| B1 (bitwise ops) | CRC32 nhanh | blend/blur ~1.5-2× | — | compute blit | — |
| D1 (local annotation) | — | Ít crash bí ẩn | Ít crash bí ẩn | — | — |
| D3 (undeclared-var error) | An toàn chung toàn repo | — | — | — | — |
| F1 (`reserve(n)`) | WAL page buf | Atlas/abuf/scratch peak -7MB | — | Texture staging | — |
| F2 (NGEN/AOT) | — | ~19MB chưa tách được | — | — | — |

## Thứ tự đề xuất gửi upstream
1. **D3** (undeclared-var) + **D4-doc** — rẻ, chống bug âm thầm.
2. **A1** (i64) — mở nhiều nhất với ít việc nhất.
3. **A2** (out-buffer) — mở Vulkan/HarfBuzz/registry-read.
4. **B1** (bitwise) — perf toàn diện.
5. **F1** (`reserve`) — giảm ~7MB peak, rẻ nếu làm cùng A1.
6. **A3** (`.so`/`.dylib`) + **E** (packaging) + **F2** — khi làm Linux/macOS thật.

---

## §D. ĐÃ MỞ — archive, đừng hỏi lại (gộp từ `COMPILER_FIX_LIST.md` §D)

- R2 native buffers = `alloc/free/read/write_u8/i32/i64`, `read_ansi`
  (Clipboard + registry + GUID-bytes dùng thật).
- R4/D6 insert trong loop đúng (gỡ workaround `qa_put1`, qtapp 52/52).
- R5 bitwise `& | >> <<` (MJPEG hot paths, pixels bit-identical).
- R6 i64 literal (HKEY >2³¹ chạy thật, fd 18/18).
- R9 `chr()` · F-1 `ord()` (ConvertToUtf32/FromUtf32; lưu ý đã biết:
  `ord()` ném với lone surrogate nên `bidi_is_surrogate` vẫn phải kẹp biên
  `chr(0xD7FF)`/`chr(0xE000)` — đừng "sửa hộ" chỗ này).
- R10 `--target library` + `--subsystem` (đã smoke: DLL 29KB ra đúng).
- R12 `reserve()` (build + chạy OK, chưa áp dụng rộng).
- R3-tuple `[(name, None, None)]` (PROBER3A_OK) + full-identity inline
  (parse tên/token/version, verify 50); bare form ra Framework identity
  là by-design.
- R1 struct: `__tkv_struct__` dict + `new_Name()` + param `"Name*"` +
  field access (verify `GetCursorPos` rc=1 + tọa độ thật); giới hạn còn
  lại: field scalar blittable (lồng/fixed-array chưa có).
- Vtable dispatch `(iface_var, slot, ...args)` (VTCOM 4/4 trên COM thật;
  iface phải là tên biến đơn — đúng thiết kế).
