# Cần sửa ở compiler (tkvc) — CHỈ MỤC CHƯA XONG (viết lại 23/09 tối)

> File riêng cho maintainer. Đã đối chiếu từng mục bằng probe chạy thật
> trên exe 17:05 — mục nào mở rồi chuyển xuống §D, không hỏi lại.
> Spec đầy đủ + acceptance test: `docs/UPSTREAM_REQUIREMENTS.md` (R1–R12).

## A. Đã có câu trả lời (không cần sửa gì thêm)

### Q-1. Ngữ nghĩa `len()` — ✅ CHỦ Ý, GIỮ CHARS
- Maintainer xác nhận giữ chars. Migration của repo đứng yên, mục này đóng.

## B. Còn lại (sau vòng verify 23/09 tối)

### F-2. Struct marshal qua pinvoke (R1) — ✅ MỞ, VERIFY ĐỘC LẬP
- Syntax thật (mò bằng probe + message lỗi, khác đề xuất ban đầu ở chỗ
  constructor): `__tkv_struct__ = [{"name": "Point",
  "fields": [["x", "i32"], ["y", "i32"]]}]` + `p = new_Point()` +
  pinvoke param `"Point*"` + đọc/ghi `p.x`. Bẫy đã gặp: khai list string
  thì lờ im lặng; `Point(0,0)` không tồn tại; truyền `list` báo sai kiểu
  (message tiếng Việt chỉ rõ cần biến kiểu struct).
- Verify: `GetCursorPos` rc=1 + tọa độ thật (x=897 y=513 lúc đo).
- Giới hạn còn lại (theo maintainer, chưa tự kiểm): field chỉ scalar
  blittable — struct lồng/fixed-array chưa có. `SBufferInfo.pData[3]` của
  OpenH264 rơi vào giới hạn này → đường **shim C# vẫn là chính** cho H.264
  (marshal phức tạp nằm trong C#, `.tkv` chỉ trao kiểu cơ bản + R2).

### F-4 còn lại. Expose COM / struct params (R8-phần-2, thu hẹp dần)
- Vtable CALLS đã mở + verify độc lập (AddRef d=1) — xong.
- Theo maintainer: expose COM đã mở (F4c cũ, `com_call0(p, 3)` → 7,
  `this` nguyên vẹn) — repo CHƯA TỰ VERIFY, để ticket probe tiếp theo.
- Còn thiếu sau đó: method có struct params (nay R1 đã mở cho scalar —
  kiểm tiếp khi cần) → UIA provider đủ sẽ triển khai khi 2 điểm trên xanh.

### F-3 còn lại. Form full-identity inline — ✅ SỬA XONG, VERIFY 50
- Tuple đã chạy từ trước (PROBER3A_OK); nay full-inline cũng parse đúng
  (tên, token, version) và chạy ra 50. Cả 3 form xanh.

### R11. Diagnostics — THEO MAINTAINER ĐÃ CÓ (chưa tự kiểm)
- Biến undeclared → lỗi compile kèm số dòng; >240 locals → chặn rõ ràng.
- Repo giữ `tools/check_locals.py` chạy tay cho chắc; sẽ bỏ khi nào tự
  verify thấy message mới.

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
- R3-tuple `[(name, None, None)]` (PROBER3A_OK) + full-identity inline
  (parse tên/token/version, verify 50); bare form ra Framework identity
  là by-design.
- R1 struct: `__tkv_struct__` dict + `new_Name()` + param `"Name*"` +
  field access (verify `GetCursorPos` rc=1 + tọa độ thật); giới hạn còn
  lại: field scalar blittable (lồng/fixed-array chưa có).
- Vtable dispatch `(iface_var, slot, ...args)` (VTCOM 4/4 trên COM thật;
  iface phải là tên biến đơn — đúng thiết kế).
