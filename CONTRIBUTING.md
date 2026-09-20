# Contributing to TokenVector.UI

## Rule #0 — Pure TokenVector 100%

**Mọi file trong đường library (`TkvUI.*.tkv` ở root, `examples/*.tkv`,
`TokenVector.UI.tkv`) phải là .tkv thuần — zero dependency, không Skia/SDL/WPF,
không code C#/Python/JS nhúng vào thư viện.**

- Được phép: `__tkv_extern_method__` / `__tkv_extern_pinvoke__` khai báo API
  hệ điều hành có sẵn (mscorlib, user32, kernel32, gdi32...) — theo đúng mẫu
  `TkvUI.Platform.tkv`. Mọi call native **phải có guard** (probe file/DLL
  trước khi gọi; DllNotFound/EntryPointNotFound sẽ crash exe).
- Không được phép: file `.py`/`.cs`/`.js`/`.dll`/binary trong đường library.
  Code đối chứng (PyQt bench), script pack/verify/serve (`.sh`/`.ps1`),
  scaffold sinh ra lúc build (Blazor host, C# bridge) sống ở `tools/`,
  `build/`, `.github/` — là **dev tooling**, không bao giờ được import bởi `.tkv`.
- CI có job kiểm tra invariant này (xem `.github/workflows/ci.yml`):
  `*.tkv` ngoài `TkvUI.*.tkv`, `examples/*.tkv`, `TokenVector.UI.tkv` = fail;
  file non-`.tkv` mới ở root/`examples/` = fail (trừ `.md`, `.json`, `.nuspec`).

## Thêm module mới

1. Đọc `docs/TkvUI.Roadmap.md §0` (ràng buộc compiler) **trước khi viết**.
   Tóm tắt các bẫy hay gặp nhất:
   - Không `& | >> <<`, không `bool` (dùng `i32` 0/1).
   - Record **không chứa field `list`** — dữ liệu biến đổi do caller giữ.
   - Không nested attribute (`a.b.c`) — gán trung gian (`tmp = a.b`).
   - Không gọi method/đọc field trên **kết quả gọi hàm**.
   - `int(...)` chỉ chứa literal nguyên; `float(...)` tường minh khi cần.
   - Method record không được tên `update`/`insert`/`remove` (macro của compiler).
   - Hằng module không dùng ở vế phải gán local trong method (dùng literal số).
   - So sánh chuỗi chỉ `==`/`!=` — cấm `<`/`>` (crash codegen `KeyError: 'str'`).
   - Method đầu tiên của class phải là `self` (không `this`).
2. Tiền tố tên `Xxx_*/MakeXxx*` riêng cho module, kiểm tra trùng toàn repo
   trước khi merge (`Select-String '^def|^class'`).
3. Mỗi module có `*_selftest() -> "XYZ_OK"` chạy headless, assertions qua
   `text_check*` (không assert số thực/hiệu số vào hàm cần 0/1).
4. Đăng ký: `tkvui.pkg.json` (modules) + `TokenVector.UI.tkv` (import + suite)
   + `tools/verify.sh` (run_case). Chạy `bash tools/verify.sh` đến
   `TKVUI_VERIFY_OK` trước khi commit.

## Commit / PR

- Viết tiếng Việt không dấu hoặc có dấu đều được, giữ nguyên encoding UTF-8.
- Không commit `build/`, `dist/`, file `.log`, process còn sống (server/NVDA).
- PR template checklist: verify PASS, docs cập nhật (BENCH/STATUS nếu đổi số),
  không vi phạm Rule #0.
