# Yêu cầu sửa tkvc (upstream) — đầy đủ, có acceptance test chạy được

> Người nhận: người sửa compiler tkvc. Mỗi yêu cầu dưới đây có: vấn đề chính
> xác, cú pháp đề xuất, **acceptance test dạng code chạy được trên máy
> Windows này**, và mặt trận nào được mở. Nền: `docs/COMPILER_GAPS.md`
> (mã gap A1…F2), case OpenH264 (`docs/OPENH264.md`), kết quả đối chiếu
> đối thủ 2026-09-22 (`docs/COMPETITORS.md` §2b).
>
> Quy tắc nghiệm thu chung: sau mỗi fix, `tools/verify.sh` vẫn
> `TKVUI_VERIFY_OK` (hiện 51/0/2) + acceptance test của chính yêu cầu đó PASS.

---

## 0. Bảng tổng quan (ưu tiên theo ROI)

| # | Yêu cầu | Gap cũ | Mở mặt trận | Mức |
|---|---|---|---|---|
| R1 | Struct marshal qua pinvoke (vào + ra) | A2-một phần | H.264 decode (đã mở bằng shim C#), text-measure chuẩn — **HarfBuzz glyph arrays KHÔNG còn chờ** (đọc tay stride20 qua R2,打通 2026-09-23) | **P0** |
| R2 | Out-buffer/mảng: `alloc` + đọc/ghi + extern nhận mảng | A2 + C9 | Clipboard OS, Vulkan enumerate, registry đọc — **HarfBuzz arrays đã dùng** (mem_read/write_u8) | **P0** |
| R3 | `extern_method` reference đúng assembly identity | A2 (đoạn identity) | C# shim (OpenH264/AccessKit): build+call được như đã chứng minh | **P0** |
| R4 | Bug D6: method trùng tên BCL resolve sai trong loop | D6 (mới) | Mọi app code (đang phải workaround `qa_put1`) | **P0 (bug, rẻ)** |
| R5 | Bitwise `&`, `\|`, `>>`, `<<` | B1 | Codec nhanh ~10× (MJPEG-HD realtime), blur/blend 1.5–2× | **P1** |
| R6 | i64 literal/typeflow + `int()` 64-bit | A1 + B3 | Handle Vulkan/registry >2³¹ | **P1** |
| R7 | Linter chấp nhận `.so`/`.dylib` | A3 | X11/Wayland, AT-SPI D-Bus, pixel Linux/macOS thật | **P1** |
| R8 | COM vtable / implement interface | A4 | UIA provider thật, D3D11 device, GPU pipeline | P2 (có đường vòng host-driven) |
| R9 | `chr(code)` builtin | B2 | Bỏ lookup-table `if`-chain trong SQLite/shaping | P2 (rẻ, tiện) |
| R10 | Packaging/AOT: `--target library`, subsystem, NGEN/AOT | E1/E2/F2 | Deploy DLL, app không console, startup NGEN, WASM AOT | P2 |
| R11 | Diagnostics: undeclared-var error + locals-limit message | D3/D4 | An toàn toàn repo (bắt bug âm thầm) | P2 |
| R12 | `reserve(lst, n)` preallocate | F1 | Giảm ~7 MB peak (pixel buffer doubling waste) | P2 |

Không yêu cầu (workaround đã ổn định, đừng đụng): toàn bộ nhóm C còn lại
(C1–C8, C10–C12: if multi-line, ternary block, `pass`, raw-string, hex
literal, string-const/module-global, tên pinvoke, entry scalar, attribute
biến trung gian, pinvoke gán biến) và D1/D2/D5 (đã có quy tắc thực nghiệm).

---

## R1. Struct marshal qua pinvoke (P0)

**Vấn đề:** không truyền struct vào / nhận struct ra qua pinvoke. Chặn:
`OpenH264.Initialize(SDecodingParam*)`, `DecodeFrame2(..., SBufferInfo*)`
+ 3 con trỏ YUV (`docs/OPENH264.md`), `GetTextExtentPoint32A` (SIZE),
XImage/XEvent. (HarfBuzz `hb_glyph_info_t` đã không còn — đọc stride20 tay qua R2.)

**Cú pháp đề xuất (tối thiểu, đủ dùng):**
```python
__tkv_struct__ = [
    {"name": "Point", "fields": [["x", "i32"], ["y", "i32"]]},
    {"name": "SystemTime", "fields": [["wYear", "i16"], ["wMonth", "i16"], ["wDayOfWeek", "i16"], ["wDay", "i16"], ["wHour", "i16"], ["wMinute", "i16"], ["wSecond", "i16"], ["wMilliseconds", "i16"]]},
]
__tkv_extern_pinvoke__ = [
    {"name": "cur_pos", "dll": "user32.dll", "symbol": "GetCursorPos", "params": ["Point*"], "returns": "i32"},
    {"name": "sys_time", "dll": "kernel32.dll", "symbol": "GetSystemTime", "params": ["SystemTime*"], "returns": "void"},
]
```
Ngữ nghĩa: `Point*` = out-struct (cấp phát + truyền con trỏ, đọc fields sau
call); struct truyền-vào tương tự (ghi fields trước call). Layout
sequential, pack mặc định Win32.

**Acceptance test** (file `.tkv` chạy trên mọi máy Windows, không cần setup;
tên constructor `new_Point`/`new_SystemTime` minh họa — upstream chọn tên
chính thức, miễn đọc/ghi fields được sau call):
```python
def struct_probe() -> "str":
    acc = [int(0), int(0)]
    p = new_Point(0, 0)          # hoặc constructor tương đương
    rc = cur_pos(p)
    check_i(acc, "pos.rc", rc, 1)
    check(acc, "pos.ints", is_int(p.x))
    s = new_SystemTime()
    sys_time(s)
    check(acc, "time.year.sane", 2020 < s.wYear)
    check(acc, "time.msec.range", 0 <= s.wMilliseconds)
    check(acc, "time.msec.range2", s.wMilliseconds < 1000)
    ...
    return "STRUCT_OK" if acc[0] == acc[1] else "STRUCT_FAIL"
```
PASS khi: `GetCursorPos` trả 1 + fields đọc được số nguyên; `GetSystemTime`
trả năm/ngày/giờ hợp lệ (2 lần chạy khác nhau ở millisecond là điểm cộng,
không bắt buộc).

---

## R2. Out-buffer / mảng (P0)

**Vấn đề:** không cấp phát + đọc bộ nhớ native (A2), param extern không nhận
mảng (C9: chỉ `bool/f32/f64/i32/i64/object/str/...`). Chặn: clipboard
(`GlobalLock` + copy), `vkEnumeratePhysicalDevices`, `RegQueryValueExA`,
HarfBuzz glyph arrays, `GetWindowTextA`.

**Cú pháp đề xuất:**
```python
buf = alloc_bytes(512)                 # handle buffer (i64/opaque)
n = win_text(h, buf, 512)              # pinvoke existing, buf là out-buffer
s = read_ansi(buf, 0, n)               # -> "str"
write_u8(buf, 0, 65)
v = read_u8(buf, 0)                    # == 65
free_bytes(buf)
```
Và `__tkv_extern_method__` chấp nhận param `list[i32]`/`list[i64]` (marshal
như mảng) + `assembly` identity đúng (xem R3).

**Acceptance test:**
```python
h = desktop_hwnd()                     # GetDesktopWindow, returns i64
buf = alloc_bytes(512)
n = win_text(h, buf, 512)              # GetWindowTextA
t = read_ansi(buf, 0, n)
check(acc, "title.nonempty", len(t))
check(acc, "title.str", 0 < len(t))
write_u8(buf, 0, 65)
check_i(acc, "rw.u8", read_u8(buf, 0), 65)
free_bytes(buf)
```
PASS khi đọc được title cửa sổ desktop (non-empty) + vòng write/read đúng.

---

## R3. Assembly identity đúng cho extern (P0)

**Vấn đề:** `extern_method` gán cứng identity Framework
(4.0.0.0/b77a…) → managed DLL riêng (C# shim) `FileLoadException`. Đã chứng
minh: C# shim build+call được, chỉ chết ở reference. Đây là primitive (b)
trong `docs/OPENH264.md` — mở cái này + R1 là OpenH264 chạy (shim ~20 dòng
theo mẫu OpenH264Lib.NET đã có).

**Cú pháp đề xuất:** cho `assembly` nhận full identity:
```python
{"name": "h264_init", "assembly": "OpenH264Shim, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null",
 "class": "OpenH264Shim.Decoder", "method": "Init", "params": ["str"], "returns": "i32"}
```
**Acceptance test:** build 1 `.tkv` reference 1 managed test-DLL bất kỳ
(provision bởi người sửa compiler cũng được) → IL emit chứa đúng identity
(kiểm bằng `monodis`/`ikdasm` hoặc `ildasm` grep chuỗi identity) + call chạy
không `FileLoadException`.

---

## R4. Bug D6: resolve sai trong loop (P0, rẻ nhất)

**Vấn đề (đã isolate dứt điểm 2026-09-22):** method trùng tên BCL
(`insert` → `List<T>.Insert`) gọi TRONG thân `while` (receiver+arg là param)
emit IL `callvirt ... NativeRichEdit::Insert(int32, !0)` →
`MissingMethodException` lúc chạy. Cùng call ở straight-line emit đúng
`'insert'(List<string>, string)`. Chi tiết + ma trận isolate:
`docs/COMPILER_GAPS.md` §D6.

**Acceptance test:** file repro tối giản (đã có mẫu đầy đủ lúc isolate):
```python
def put_loop(edit: "NativeRichEdit", lines: "list[str]", text: "str") -> "i32":
    i = int(0)
    while i < len(text):
        ch = text[i:i + 1]
        if ch == "\n":
            edit.newline(lines)
        else:
            edit.insert(lines, ch)   # truoc fix: emit Insert(int32, !0)
        i = i + 1
    return len(lines)
```
PASS khi: IL chứa `'insert'(List<string>, string)` (grep `.il`) + chạy ra
kết quả đúng. Không cần tính năng mới — chỉ cần dispatch đúng như
straight-line.

---

## R5. Bitwise (P1)

**Vấn đề:** `&`, `|`, `>>`, `<<` không compile (B1). Hậu quả đo được:
MJPEG-HD 453 ms (~2 fps, kể cả optimize hết cũng chỉ ~5 fps) — realtime cần
bitwise/SIMD, không đường vòng; blur/blend mất thêm 1.5–2×.

**Acceptance test:**
```python
check_i(acc, "and", 255 & 15, 15)
check_i(acc, "or", 240 | 15, 255)
check_i(acc, "shl", 1 << 8, 256)
check_i(acc, "shr", 256 >> 4, 16)
check_i(acc, "mask", (179 & 240) + (179 & 15), 179)
```

---

## R6. i64 literal/typeflow + parse 64-bit (P1)

**Vấn đề:** literal ≥2³¹ nổ ở fold hằng/runtime `TkvInt.ToI64`;
`int("2147483648")` ném `ParseInt32` (A1/B3). Chặn: handle Vulkan/registry,
mọi pinvoke param >2³¹.

**Acceptance test:**
```python
big = 2147483648
check(acc, "lit.u64", big)
check_i(acc, "add.u64", 1073741824 + 1073741824, 0)  # == 2^31, so sánh qua str nếu cần
check_s(acc, "str.u64", str(big), "2147483648")
check_s(acc, "parse.u64", str(int("2147483648")), "2147483648")
check(acc, "hex", 0x80000002)  # literal hex được chấp nhận (giá trị tùy implement đúng bit pattern)
```

---

## R7. Linter chấp nhận `.so`/`.dylib` (P1)

**Vấn đề:** linter bắt buộc `.dll`, từ chối `libvulkan.so`/`libatspi.so`/
`.dylib` kể cả khi chỉ build (A3). Chặn toàn bộ Linux/macOS thật.

**Acceptance test:** build-only (headless-safe, không chạy):
```python
__tkv_extern_pinvoke__ = [
    {"name": "x11_open", "dll": "libX11.so", "symbol": "XOpenDisplay", "params": ["str"], "returns": "i64"},
]
```
PASS khi `tkvc build` thành công (không cần chạy — máy Windows không có `.so`).

---

## R8. COM vtable / implement interface (P2)

**Vấn đề:** không implement `IRawElementProviderSimple` (UIA),
không gọi method qua vtable COM (`ID3D11Device*`), không ObjC msgSend/JNI
(A4). Đường vòng chính thức hiện tại là host-driven (HWND mirror + shim),
vẫn đủ dùng — nên đây là P2.

**Acceptance test (khi làm):** class `.tkv` implement 1 COM interface test
(trả `S_OK` + out-params đúng) + gọi 1 method qua vtable của interface có
sẵn (vd `IUnknown::QueryInterface`).

---

## R9. `chr(code)` (P2, rẻ)

Xóa lookup-table `if`-chain (`char_code_from_i64` trong `TkvUI.SQLite.tkv`).
Acceptance: `check_s(acc, "chr", chr(65), "A")`,
`check_s(acc, "chr.vi", chr(234), "ê")` (ê U+00EA để kiểm non-ASCII).

---

## R10. Packaging/AOT (P2)

- `--target library`: `tkvc build src.tkv --target library --out x.dll` ra
  managed DLL import được (thay vì exe đổi tên như `tools/pack_nupkg` đang làm).
- `--subsystem windows`: exe không kèm console.
- NGEN/AOT: tài liệu/hỗ trợ build NGEN (`ngen.exe` chạy được trên output) hoặc
  hướng AOT — mục tiêu cold-start về <0.3 s (hiện ~1.0 s do AV+JIT, xem
  `docs/COMPETITORS.md` §2).
Acceptance: từng flag chạy thành công + artifact đúng loại (check header/
  `corflags` / chạy không console).

---

## R11. Diagnostics an toàn (P2)

- Biến chưa khai báo → **lỗi compile** (hiện-desc: D3 — silent, gây bug âm
  thầm; `qa_put1`-style code rất cần).
- Function vượt ~256 locals → **message rõ ràng** lúc build (hiện crash ngẫu
  nhiên; workaround là `tools/check_locals.py` chạy tay sau mỗi build).
Acceptance: 2 file repro (1 biến lạ, 1 hàm 300 locals) → compiler báo lỗi
bằng chữ, exit code ≠ 0.

---

## R12. `reserve(lst, n)` (P2)

Giảm doubling waste ~7 MB cho pixel buffer (F1; slope đo 8 B/elem).
Acceptance: API tồn tại + `len`/`append` hành vi cũ; peak RSS đo tay
(`tools/bench/bench_mem.py`) giảm sau khi dùng cho surface lớn.

---

## Thứ tự đề xuất + ma trận unblock

Làm theo: **R4 → R1 → R2 → R3** (P0: mở H.264 decode, clipboard, HarfBuzz-struct,
text-measure chuẩn, xóa workaround `qa_put1`) → **R5 → R6 → R7** (P1: codec
realtime, handle lớn, Linux) → **R8 → R9 → R10 → R11 → R12** (P2).

| Mở | M1 persist | M2 shaping | M3 widgets | M4 media/GPU | M5 a11y/print |
|---|---|---|---|---|---|
| R1 struct | — | HarfBuzz full | — | **H.264 decode** | — |
| R2 out-buf | WAL verify mạnh | HarfBuzz arrays | — | Vulkan enum, XImage | Registry font, AT-SPI đọc |
| R3 identity | — | — | — | **Shim OpenH264 chạy** | Shim AccessKit/COM |
| R4 bug D6 | Bớt crash bẩn | Bớt crash bẩn | Bỏ `qa_put1` | — | — |
| R5 bitwise | CRC32 nhanh | blend 1.5–2× | — | **MJPEG-HD realtime** | — |
| R6 i64 | — | — | — | Vulkan handles | HKEY_* |
| R7 .so | — | — | — | X11/Wayland | AT-SPI D-Bus |
| R8 COM | — | — | — | D3D11/GPU pipeline | **UIA provider thật** |
| R10 pkg | — | — | — | WASM AOT, startup NGEN | Spooler không console |
