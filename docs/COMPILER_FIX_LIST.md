# Danh sách cần sửa ở compiler (tkvc) + giải pháp đề xuất

> File riêng, ngắn gọn, đưa thẳng cho người sửa tkvc. Chi tiết đầy đủ +
> acceptance test chạy được: `docs/UPSTREAM_REQUIREMENTS.md` (R1–R12).
> Trạng thái probe ngày 2026-09-23 trên tkvc build 22:14.

## A. Hỏi xác nhận (không cần sửa code, cần 1 câu trả lời)

### Q-1. Ngữ nghĩa `len()` — chủ ý hay regression?
- Hiện tượng: build 22:14 đổi `len()` từ bytes UTF-8 sang chars/units.
  Bằng chứng: test `vi_seq_len_at("Việt", 0, 6)` (n=6 = số bytes) crash
  `IndexOutOfRange`; `shape_script_of("ệ")` rẽ nhánh sai.
- Repo đã migrate toàn bộ text family sang char-semantics (đúng đắn hơn,
  khớp `.NET String.Length`), verify 50/0/2 xanh lại.
- Cần maintainer xác nhận: **giữ chars (xong, không làm gì thêm)** hay
  **revert về bytes (báo ngay để repo revert migration theo)**.

## B. Thêm nhỏ (1 buổi mỗi cái)

### F-1. Builtin `ord()` — ✅ ĐÃ MỞ (tkvc 23/09 13:21), đã tiêu thụ
- Mở đúng như đề xuất (`Char.ConvertToUtf32`, đối xứng `chr()`); probe
  65/234/7879 đúng hết (lưu ý: `ệ` U+1EC7 = 7879, không phải 7887).
- Đã áp dụng: `fb_is_emoji`/`fb_is_color_font` chuyển `char_code` → `ord()`,
  ranges chết từ trước nay sống thật (✚ U+271A → đúng 4 emoji thay vì 3
  missing; test expectation sửa theo cho trung thực). Fallback 37/37.
- Còn lại: `bidi_is_surrogate` GIỮ nguyên kẹp biên (không dùng `ord()` được
  vì `ConvertToUtf32` ném với lone surrogate — đúng chỗ cần detect chúng).

## C. Sửa thật (chặn tính năng lớn, đã chứng minh không có đường vòng)

### F-2. Struct marshal qua pinvoke (R1)
- Chặn: OpenH264 `Initialize`/`DecodeFrame2`, HarfBuzz full, text-measure chuẩn.
- Đã thử: `__tkv_struct__` bị bỏ qua im lặng; `extern_method` trả `IntPtr`
  → `MissingMethodException`; shim C# kẹt ở F-3.
- Giải pháp: khai báo struct + truyền `Struct*` (in/out) như §R1 trong
  `UPSTREAM_REQUIREMENTS.md` (acceptance: `GetCursorPos`/`GetSystemTime`).

### F-3. Assembly identity đúng cho extern (R3) — VẪN ĐÓNG (re-probe 23/09)
- **Bằng chứng chạy thật (lần 2, tkvc mới)**: build DLL test bằng `csc.exe`,
  khai báo `__tkv_extern_assembly__`, gọi lúc chạy nổ Y NGUYÊN:
  `FileLoadException: 'R3Test, Version=4.0.0.0, Culture=neutral,
  PublicKeyToken=b77a5c561934e089'` — compiler vẫn đóng dấu identity
  Framework lên assembly tư nhân.
- Chặn: mọi shim C# (OpenH264 ~20 dòng, AccessKit).
- Giải pháp: cho khai báo full identity (name+version+culture+token) như §R3.

### F-4. COM vtable / implement interface (R8)
- Chặn: UIA provider thật, D3D11/GPU pipeline. HWND mirror chỉ là đường vòng.
- Giải pháp: như §R8 (dài hạn, P2).

## D. Đã mở — không cần làm gì thêm (ghi nhận để khỏi hỏi lại)

R2 native buffers (đúng spec đề xuất) · R4/D6 (insert trong loop đúng) ·
R5 bitwise · R6 i64 literal · R9 `chr()` · R10 `--target library` +
`--subsystem` (đã smoke) · R12 `reserve()` (chạy OK) · R7 build chấp nhận
`.so` (runtime chưa kiểm vì thiếu Linux) · R11 chưa kiểm.
