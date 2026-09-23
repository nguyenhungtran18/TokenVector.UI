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

### F-1. Builtin `ord()` — đối xứng với `chr()` vừa ship
- Vì sao cần: không có cách nào lấy codepoint từ `str` (string compare
  không biểu diễn được biên surrogate D800/DC00; `chr()` ném với input
  surrogate; bảng literal chỉ cover ký tự đã biết).
- Workaround hiện tại (đã chứng minh 4/4 + dùng thật trong
  `bidi_is_surrogate`/`bidi_seq_step`): kẹp surrogate bằng 2 biên hợp lệ
  `chr(0xD7FF)`/`chr(0xE000)` — chỉ đủ để **group astral pair**, không đủ
  cho `ord()` tổng quát (VD: Hangul Jamo Extended-B D7B0–D7FF lọt vùng kẹp).
- Giải pháp: `ord(u) -> i32` qua `Char.ConvertToUtf32(string, 0)` (giống hệt
  cách `chr()` dùng `ConvertFromUtf32`).
- Acceptance: `ord("A")==65`, `ord("ê")==234`, `ord("ệ")==7887`.

## C. Sửa thật (chặn tính năng lớn, đã chứng minh không có đường vòng)

### F-2. Struct marshal qua pinvoke (R1)
- Chặn: OpenH264 `Initialize`/`DecodeFrame2`, HarfBuzz full, text-measure chuẩn.
- Đã thử: `__tkv_struct__` bị bỏ qua im lặng; `extern_method` trả `IntPtr`
  → `MissingMethodException`; shim C# kẹt ở F-3.
- Giải pháp: khai báo struct + truyền `Struct*` (in/out) như §R1 trong
  `UPSTREAM_REQUIREMENTS.md` (acceptance: `GetCursorPos`/`GetSystemTime`).

### F-3. Assembly identity đúng cho extern (R3) — CÓ PROOF MỚI
- **Bằng chứng chạy thật 2026-09-23**: build DLL test bằng `csc.exe`,
  khai báo `__tkv_extern_assembly__`, gọi lúc chạy nổ đúng:
  `FileLoadException: 'R3Test, Version=4.0.0.0, Culture=neutral,
  PublicKeyToken=b77a5c561934e089'` — compiler đóng dấu identity Framework
  lên assembly tư nhân.
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
