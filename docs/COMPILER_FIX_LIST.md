# Cần sửa ở compiler (tkvc) — CHỈ MỤC CHƯA XONG (viết lại 23/09 tối)

> File riêng cho maintainer. Đã đối chiếu từng mục bằng probe chạy thật
> trên exe 17:05 — mục nào mở rồi chuyển xuống §D, không hỏi lại.
> Spec đầy đủ + acceptance test: `docs/UPSTREAM_REQUIREMENTS.md` (R1–R12).

## A. Cần 1 câu trả lời (không sửa code)

### Q-1. Ngữ nghĩa `len()` — chủ ý hay regression?
- Build 22:14 đổi `len()` từ bytes UTF-8 sang chars/units (bằng chứng:
  test `vi_seq_len_at("Việt", 0, 6)` crash; đã migrate toàn bộ text family
  sang char-semantics, verify 50/0/2 xanh lại).
- Hỏi: **giữ chars (xong)** hay **revert về bytes (báo để repo revert theo)**.

## B. Cần sửa thật (đã chứng minh không có đường vòng)

### F-2. Struct marshal qua pinvoke (R1) — CHƯA CÓ GÌ MỚI
- `__tkv_struct__` vẫn bị bỏ qua im lặng; `extern_method` trả `IntPtr` vẫn
  `MissingMethodException`. Không file feature mới nào trong dist.
- Chặn còn lại: OpenH264 **trực tiếp** (`Initialize`/`DecodeFrame2`),
  HarfBuzz full, `GetTextExtentPoint32A`, struct X11/Vulkan, method COM
  có struct params.
- Tạm bypass được: shim C# (R3-tuple + R2 đã mở) — đang đi đường này cho
  H.264, nhưng direct-integration vẫn cần R1.
- Giải pháp + acceptance (`GetCursorPos`/`GetSystemTime`): §R1 trong
  `UPSTREAM_REQUIREMENTS.md`, giữ nguyên.

### F-4 còn lại. Implement COM interface trong `.tkv` (R8-phần-2)
- Vtable CALLS đã mở + verify độc lập (AddRef d=1, xem §D) — phần này xong.
- Còn thiếu: (a) method có struct params (chờ R1); (b) implement một COM
  interface bằng class `.tkv` để COM gọi NGƯỢC vào (cần cho UIA provider
  đầy đủ — hiện chỉ gọi RA ngoài được, chưa expose được).
- Giải pháp đề xuất: hoặc emit CCW/vtable cho record có đánh dấu
  (VD: `__tkv_com_class__`), hoặc document chính thức "chỉ gọi ra" để repo
  chốt kiến trúc host-shim implement phía C#.

### F-3 còn lại. Form full-identity inline emit IL sai cú pháp (nhẹ)
- Tuple đã là form chính thức và chạy (PROBER3A_OK) — mục này ưu tiên thấp,
  ghi để khỏi quên: với method `assembly` = full identity string, IL emit
  ra `.assembly extern R3Test, Version=...` không quote → lỗi assemble.
- Giải pháp: hoặc parse identity ra version/token đúng, hoặc báo lỗi rõ
  "dùng tuple thay vì inline" lúc build thay vì emit IL hỏng.

### R11. Diagnostics an toàn (chưa kiểm, có thể vẫn thiếu)
- Biến chưa khai báo phải lỗi compile (hiện nghi vẫn silent); function vượt
  ~256 locals phải báo rõ (hiện crash ngẫu nhiên, repo tự check bằng
  `tools/check_locals.py`).
- Giải pháp + acceptance (2 file repro): §R11.

## C. Chờ môi trường, không phải compiler (ghi nhận)

- **R7 runtime Linux**: build đã chấp nhận `.so`; chưa kiểm runtime vì thiếu
  máy Linux. Cần CI/runner Linux hoặc xác nhận từ maintainer.
- **R3 trên máy khác**: tuple đã xanh ở đây; nếu maintainer cần matrix
  (x86/x64, .NET Framework/Core) thì báo để chạy thêm.

## D. ĐÃ MỞ — archive, đừng hỏi lại

- R2 native buffers = `alloc/free/read/write_u8/i32/i64`, `read_ansi`
  (đúng spec đề xuất; Clipboard + registry + GUID-bytes dùng thật).
- R4/D6 insert trong loop đúng (gỡ workaround `qa_put1`, qtapp 52/52).
- R5 bitwise `& | >> <<` (MJPEG hot paths, pixels bit-identical).
- R6 i64 literal (HKEY >2³¹ chạy thật, fd 18/18).
- R9 `chr()` · F-1 `ord()` (ConvertToUtf32/FromUtf32; lưu ý đã biết:
  `ord()` ném với lone surrogate nên `bidi_is_surrogate` vẫn phải kẹp biên
  `chr(0xD7FF)`/`chr(0xE000)` — đừng "sửa hộ" chỗ này).
- R10 `--target library` + `--subsystem` (đã smoke: DLL 29KB ra đúng).
- R12 `reserve()` (build + chạy OK, chưa áp dụng rộng).
- R3-tuple `[(name, None, None)]` (PROBER3A_OK); bare form ra Framework
  identity là by-design.
- Vtable dispatch `(iface_var, slot, ...args)` (VTCOM 4/4 trên COM thật;
  iface phải là tên biến đơn — đúng thiết kế).
