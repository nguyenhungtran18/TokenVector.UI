# Changelog

Mọi thay đổi đáng chú ý của TokenVector.UI (TkvUI). Version lấy từ `tkvui_version()` trong `TokenVector.UI.tkv`.

## 2.2.2 — P2.3 half-resolution blur (2026-09-17)

- `TkvUI.Effects` thêm `half_res_blur()`: downsample 2× (trung bình khối 2×2, khử alias) → `box_blur_pass` radius/2 trên buffer nhỏ → upsample nearest-neighbor. Yêu cầu buffer phụ chỉ w×h/4.
- Benchmark trong `effects_selftest` (5 vòng 800×200 r=8, half-res tính cả copy vào): **full=1000ms vs half=391ms → ~2.5×** (dưới mức lý thuyết 4× vì downsample/upsample vẫn duyệt full-res một lượt mỗi phía).
- Chất lượng: trên vùng màu đều giữ nguyên giá trị (check PASS); radius/2 giữ độ mờ tương đương.
- `effects_selftest`: 26 → **29/29**. Full verify: TKVUI_VERIFY_OK.

## 2.2.1 — P2.2 blur benchmark (2026-09-17)

- `TkvUI.Effects`: benchmark `box_blur_pass` (10 vòng 800×200 r=4) trong `effects_selftest` với bản tham chiếu `box_blur_pass_ref` + check pixel-exact giữa 2 bản.
- Kết quả trung thực: sliding-window đã tồn tại từ trước nên tối ưu hoist row-index chỉ đạt **~1.0x** — blur đã là O(1)/pixel. Muốn nhanh hơn nữa cần `>>`/`&` cho decode ARGB (compiler chưa hỗ trợ, đã probe) hoặc half-resolution blur.
- Benchmark phát hiện bug copy buffer: `append` vào buffer đã có capacity ghi sai offset (data nằm sau zeros) → phải gán theo index.
- `effects_selftest`: 24 → 26/26. Full verify: TKVUI_VERIFY_OK.

## 2.2.0 — P2.1 Glyph Atlas (2026-09-17)

### Thêm
- **Glyph atlas** (`TkvUI.Text.tkv`): pre-bake toàn bộ 95 glyph ASCII (32..126) vào 1 buffer duy nhất
  (`text_atlas_record` + `text_atlas_baked_buffer`, layout 16 cột × 6 hàng, 96×42 px @ scale 1).
- `text_atlas_draw_string()` — vẽ text bằng **blit từ atlas** thay vì decode `glyph_pattern` per-pixel;
  hỗ trợ align/tracking như `draw_string`, blend theo mask kênh r của atlas pixel.
- `char_code()` — mã ASCII của ký tự in được (32..126) bằng binary search trong charset 95 ký tự
  đã sort (compiler chưa có `ord()`; so sánh chuỗi `<`/`>` là so sánh codepoint). Ngoại bảng → -1.
- Selftest text mở rộng 29 → **46 check** (char_code ×6, atlas ×9, benchmark ×2), gồm check atlas vẽ ra
  **đúng vị trí pixel từng pixel** so với `draw_string` cổ điển.
- **Benchmark tích hợp trong selftest**: đo `GetTickCount` (pinvoke kernel32) khi vẽ 400 vòng × 54 ký tự —
  classic ~63ms vs atlas ~15ms → **speedup ~4.2×**; kiểm tra cả 2 đường cho cùng số pixel.

### Sửa
- **Bug render cổ tích của `draw_string`**: `else: on = 0` ở cuối chuỗi decode bit nằm **sai cấp thụt**
  (thuộc `if tmp >= 1` thay vì `if mask >= p`) → mọi glyph có mask ≠ 17 chỉ vẽ đúng phần cột 0/4,
  text 'one two three four' mất ~2/3 pixel. Bỏ nhánh else sai + đóng `tmp = tmp - 1` cho cột 4.
  Trước fix selftest vẫn PASS vì các check chỉ đếm >= — minh chứng vì sao phải so snapshot pixel.
- `draw_string` giờ kiểm `char_code(ch) >= 0` trước khi vẽ (ký tự ngoại bảng bỏ qua thay vì tra
  pattern box-fallback — behavior box fallback giữ cho `glyph_pattern` gọi trực tiếp).

### Hiệu năng
- Vẽ text qua atlas: mỗi glyph = 1 lần blit 6×7 px với mask pre-baked, bỏ hoàn toàn
  `glyph_pattern` + chuỗi if decode bit per-pixel trong vòng lặp hot.

## 2.1.0 — P1.1 hardening (2026-09-16)

## 2.1.0 — P1.1 hardening (2026-09-16)

### Thêm
- `core_selftest` (47 check), `graphics_selftest` (29), `text_selftest` (29), `effects_selftest` (24),
  `platform_selftest` (24) — trước đây 4 module này không có test nào.
- `TokenVector.UI.tkv`: `tkvui_selftest()` + `main()` — build umbrella **không cần `--entry`**, chạy toàn bộ
  suite và trả `TKVUI_OK` / `TKVUI_FAIL`.
- `tools/verify.sh` — build + chạy mọi selftest headless, exit != 0 khi FAIL, chấp nhận `*_SKIPPED`.
- `README.md`, `CHANGELOG.md`, `LICENSE` (MIT), `.gitignore` (bỏ `build/`, `.freebuff/`, `*.exe`, `*.il`).

### Sửa
- `detect_platform()` trả hằng số `1` → **probe runtime thật** (env + file probe qua `mscorlib`: Android,
  iOS, macOS, Wayland, X11, Windows), thêm `detect_platform_id()` và override `TKVUI_PLATFORM=1..6`.
- `examples/TkvUI.IOSDemo.tkv` crash `DllNotFoundException: libobjc.dll` trên Windows → backend iOS/Android
  **gate theo `detect_platform()`**, `create()` trả handle 0, demo trả `*_SKIPPED` thay vì crash.
- `IOSPlatform.present()` ghi pixel trực tiếp vào con trỏ `CGContext` (tạo với `data=NULL`) → **ghi đè vùng nhớ
  của CGContext**. Nay đường upload do host đảm nhiệm (`set_frame_buffer`), không ghi vào vùng nhớ lạ.
- `AndroidPlatform.present()` bỏ `VirtualAlloc`/`wsprintf` (API Windows, không tồn tại trên Android) khỏi
  đường Android; contract rõ ràng: `set_jni_env` + `set_frame_buffer` + `set_dst_bits` do host cấp.
- iOS/Android thêm `set_frame_buffer()`; `AndroidPlatform` thêm field `frame_buf`, `dst_bits`;
  `IOSPlatform` thêm `frame_buf`.
- `docs/TkvUI.Roadmap.md`: bỏ thông tin sai (`__tkv_extern_assembly__ = "System.Drawing"` không có trong umbrella),
  cập nhật trạng thái P8/P9 (đã có khung + example), thêm §8 platform detection + contract mobile.
- `DEVELOPMENT_PLAN.md`: thêm bảng đối chiếu "kế hoạch ↔ trạng thái hiện tại".

## 2.0.0 — v2 (P1–P7.6, DONE)

- P1: Foundation v2 (HSL, Theme token, Insets/CornerRadius, DPI, SurfacePool), `draw_arc` bằng Sin/Cos thật.
- P2: Text v2 (align Center/Right, tracking, wrap + ellipsis), Effects Dual Kawase 3-pass + `backdrop_blur`.
- P3: Win32 thật — `WS_EX_LAYERED` + `CreateDIBSection` + `UpdateLayeredWindow`, contract `present_diff`.
- P4: Portability — PEVerify + Mono bit-identical, `WinForms` vehicle cho cửa sổ đa nền tảng, backend parity.
- P5: Input router (`hit_test_tree` topmost-first, pointer capture, touch/gesture) — 41/41 PASS.
- P6: Layout Flex/Grid/Stack + DPI + validator — 50/50 PASS.
- P7: Widget catalog 15 + Spring/Tween + Invalidation/Scheduler/RenderLoop — 27/27 PASS; demo desktop + mobile.
- P7.5 `examples/TkvUI.Live.tkv` — vòng 60fps thật, 27/27 PASS; P7.6 `run_live` — input thật (WM pump), 600 vòng.

## 1.0.0 — v1 (baseline)

- Core (`ColorRgba`, `PixelSurface`, blend SrcOver), Graphics Bresenham, Text bitmap 5x7, Effects blur/shadow,
  Platform stub (Win32/X11/Cocoa), Events. Chưa có Input router, Layout, Widgets.
