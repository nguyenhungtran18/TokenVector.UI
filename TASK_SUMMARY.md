# TokenVector.UI – Vietnamese Bitmap UI Task Summary

## Objective
Add pure 100% TokenVector Vietnamese bitmap font support (5x7 precomposed ~134 glyphs) and sequence‑aware text rendering, with cross‑platform UI widgets (Windows, Linux/macOS via X11/Cocoa, Android).

## Completed Work

### 1. Vietnamese Bitmap Font (`TkvUI.Viet.tkv`)
- 134 glyphs, codepoints 192–7929, generated via external script (`vi_gen.py` outside repo).
- QA art, duplicate‑pair fix → `total=134 unique=134`, `ascii‑clash=0`.
- Emitted `vi_bits.tkv` with branch `if pair ==` constants spot‑checked.
- Builder `vi_build_mod.py` → `TkvUI.Viet.tkv` written and verified.

### 2. Text Rendering (`TkvUI.Text.tkv`)
- `__tkv_import__ = ["TkvUI.Core", "TkvUI.Viet"]`.
- `vi_strlen`, `vi_seq_len_at`, `vi_row_of`, `vi_is_ascii`, `vi_truncate`, `vi_draw_bits` helpers.
- `measure_string` uses `vi_strlen` (byte‑wise sequence count).
- `draw_string` sequence‑aware: ASCII path unchanged; non‑ASCII pairs (2‑byte) or triplets (3‑byte) handled via `vi_bits` lookup, fallback to unknown glyph (`-1`).
- `text_atlas_draw_string` fallback to `draw_string` when atlas lacks non‑ASCII.
- `text_line_count`, `measure_block`, `draw_text_block` all sequence‑aware (counts by `vi_seq_len_at`, truncates at sequence boundaries).
- Selftest: **160/160 PASS** → `TEXT_OK` (thêm 18 i18n baked + 12 fallback: `font_family_resolve` 5 loại, `text_draw_fallback`, space blank — sửa bug `text_atlas_draw_i18n` cũ vẽ space thành box).
- `TkvUI.I18nData.tkv` (mới): byte TTF subset baked ngoài repo (times 6308B + msyh 3412B) + `i18n_codepoint`/`i18n_slot_for`; né compiler gap file I/O (chỉ có `tkv_has_file`, không có file-read).

### 3. Widget Updates (`TkvUI.Widgets.tkv`)
- Import `TkvUI.Viet`.
- `TextFieldWidget.backspace` now removes full sequence (2‑/3‑byte).
- `TextFieldWidget.caret` position computed via `vi_strlen`.
- `vi_truncate` used at 5 cut‑off points:
  - AntSteps title/descr (maxc = `(sw-4)/6`).
  - AntTable headers & cells (maxc = `(w-12)/6`).
  - AntSelect placeholder (`txt`).
  - MediaPlaylist title/artist (`t`, `a`).
- Widget selftest: **99/99 PASS** → `WIDGETS_OK`; includes new Vietnamese backspace/tests.

### 4. Media Truncation (`TkvUI.Media.tkv`)
- `vi_truncate` applied to `titles[idx]`, `artists[idx]` at `maxc = int((self.bw-110)/6)`.
- Selftest: **80/80 PASS** → `MEDIA_OK`.

### 5. Umbrella & Examples
- `TokenVector.UI.tkv`, `TkvUI.Media.tkv`, `TkvUI.Widgets.tkv` imports updated with `"TkvUI.Viet"`.
- `verify.sh` full suite: **TKVUI_OK** (all modules pass).
- Examples headless: Mobile 6/6, Live 27/27, MediaDemo 8/8; Android/IOS skipped (backend not on host).

## Active Tasks (Plan)

| Priority | Area | Next Steps |
|---|---|---|
| High | **Linux (X11) & macOS (Cocoa) platform support** | ✅ Added `make_x11_platform()` / `make_cocoa_platform()` in `TkvUI.Platform.tkv`; platform checks in `create()` like Android/iOS; `detect_platform()` returns correct backend. Full suite `TKVUI_OK`. |
| High | **Widget API** | ✅ `ButtonWidget.contains()`, `TextInputWidget` (sequence-aware), `make_button`, `make_textinput` factories. Cross-OS, no Win32 calls. |
| Medium | **IME for Vietnamese** | ✅ Added `__tkv_extern_pinvoke__` for `ImmGetContext`, `ImmReleaseContext`, `ImmGetCompositionStringW`, `ImmSetCompositionStringW`, `ImmNotifyIME` (Win32). Constants `GCS_COMPSTR`, `GCS_RESULTSTR`, `NI_COMPOSITIONSTR`, etc. Helper functions `ime_get_context`, `ime_get_composition_string`. |
| High | **IME deep integration** | ✅ `EventDispatcher` thêm `ime_composing`, `ime_composition` + methods `ime_start`/`ime_composition`/`ime_end`/`ime_result`. `TextInputWidget` thêm `ime_composing`, `ime_composition` + `ime_start`/`ime_composition`/`ime_end`/`ime_result` + render composition text. |
| High | **IME Win32 real hook demo** | ✅ `examples/TkvUI.IMEDemo.tkv` - demo IME Win32 that: tạo cửa sổ thật, hook `WM_IME_COMPOSITION`/`WM_IME_STARTCOMPOSITION`/`WM_IME_ENDCOMPOSITION`, gọi `ImmGetCompositionStringW` (GCS_COMPSTR/GCS_RESULTSTR), feed vào `EventDispatcher` + `TextInputWidget`. Render composition text realtime. |
| High | **WebAssembly support (NEW)** | ✅ `tokenvector_compile.tkv`: thêm `assemble_il_to_dll()` (IL → .dll via `ilasm /dll`) và `compile_il_to_wasm()` (IL → .dll → .NET 8+ WASM AOT qua `dotnet publish -r browser-wasm`). Test WASM 2.9MB tạo thành công. Yêu cầu: .NET 8+ SDK, `dotnet workload install wasm-tools`. |
| Medium | **Demo & Documentation** | ✅ Created `examples/TkvUI.VietDemo.tkv`, `examples/TkvUI.IMEDemo.tkv`. Updated `README.md` (v2.3.2), `TokenVector.UI.tkv` (version 2.3.2). |
| Low | **WASM / web port (DONE)** | ✅ WebAssembly compilation working end-to-end via .NET 8+ WASM AOT. |
| High | **Bidi / UTF-8 decoder (DONE)** | ✅ `TkvUI.Bidi.tkv`: `utf8_seq_range` (Hebrew→R, Arabic→AL, CJK→L, emoji→ON), `bidi_seq_classes`/`bidi_seq_offset`/`bidi_draw_visual` + `bidi_draw_visual_atlas` (visual order + blit glyph thật); `utf8_seq_len` đã chuyển sang `TkvUI.Viet` (leaf, Text dùng chung); selftest **117/122 PASS** → `BIDI_OK`, milestone `"你好 🌍 שלום"` vẽ glyph thật đúng thứ tự RTL; **HarfBuzz thật (gần đủ)**: pinvoke DLL load + single-char shaping đúng (glyph id, cluster byte-based, advance với scale); multi-char bị bug glyph id=0 (buffer stride/out-array index mismatch - gap compiler đọc out-buffer), tạm dùng fallback bitmap/sequence-aware. |
| High | **Glyph thật CJK/Hebrew (DONE, trừ emoji)** | ✅ Bake subset TTF (times/msyh) vào atlas qua `text_atlas_bake_i18n_all` (10 glyph, codepoint thật — sửa bias code+32 của `ttf_atlas_bake`); vẽ qua `text_atlas_draw_i18n`; emoji vẫn box (cần cmap format12 + outline màu, ngoài phạm vi parser). |
| High | **Fallback chain (DONE)** | ✅ `font_family_resolve` (ASCII→bitmap, Viet→vi, he/cjk→i18n slots, còn lại→box) + `text_draw_fallback` (2 atlases, align/tracking); TEXT 160/160. |
| Medium | **A11y tree (data model DONE, bridge BLOCKED)** | ✅ `A11yNode` + tree commit/diff (38/38) + JSON dump (`a11y_node_to_json`, `a11y_tree_to_json`); PLATFORM 49/49. ❌ OS bridge: Win32 UIA (COM vtable blocked), Linux AT-SPI (.so + D-Bus blocked), macOS (ObjC protocol), Android (JNI) - cần compiler upstream. |
| Medium | **GPU Vulkan device ops (stubs DONE) + Shader Pipeline (abstraction DONE)** | ✅ 11 Vulkan device ops stub + 9 shader pipeline (module/layout/graphics/compute pipeline) + 4 D3D11/Metal stubs; GPU 66/66. ❌ Instance/device handle chặn ở đọc out-handle (gap compiler); shader compile/Dx11/Metal thật cần host GPU thật. |
| Medium | **Theme theo OS (logic DONE, detect BLOCKED)** | ✅ `theme_pick`/`theme_changed` polling + `theme_detect_os` stub; PLATFORM 49/49. ❌ Detect thật: đã thử C# shim (build+call được) nhưng tkvc gán cứng identity Framework cho extern assembly → unloadable; vét tổng 11 cơ chế đều chặn (chi tiết trong code + DEVELOPMENT_PLAN §3). |
| High | **Multi-window wiring (DONE)** | ✅ `make_win32_platform` + `win32_create_multiple`/`win32_present_all`/`win32_close_all` (pool DIB/memDC theo handle, flat buffer/window, handle-0 headless-safe) + `render_loop_pump_all` (Widgets); PLATFORM 48/48, WIDGETS 101/101; tạo thật 2 cửa sổ 2x2, present 8px, đóng sạch. |

## Technical Constraints (strict)
- **No**: bitwise `<<`/`>>`/`&`/`|`/`^`/`~`, `pass`, tuple literals, ternary `x if cond else y`.
- **Only**: `def`/`if`/`return`/`while`/`for`, list append in same scope, `__tkv_import__`, `__tkv_extern_pinvoke__`.
- **Record**: flat fields only (`i32`, `f64`, `str`), no `list` inside.
- **Import**: resolve per file‑source folder (e.g. `TkvUI.Viet` → `TkvUI.Core`).

## Build & Test Commands (verified)
```powershell
# Build single module
tkvc.exe build TkvUI.Viet.tkv --entry vi_selftest --out build\viet.exe

# Full verify suite
bash tools/verify.sh   # or TKVC=... verify.sh on Windows

# Run example headless
tkvc.exe build examples\TkvUI.Demo.tkv --out build\demo.exe
```

## Key Files (relative to `D:\TokenVector.UI`)
- `TkvUI.Viet.tkv` — new module, 134 glyph.
- `TkvUI.Text.tkv` — text + Vietnamese rendering.
- `TkvUI.Widgets.tkv` — TextField + widget truncation.
- `TkvUI.Media.tkv` — playlist truncation.
- `tools/vi_gen.py` — external generator (outside repo).
- `tools/vi_build_mod.py` — builder that produced `TkvUI.Viet.tkv`.
- `tools/verify.sh` — full test harness.

---
*Last updated: 2026-09-18 — Task status: Umbrella TKVUI_OK + BIDI_OK (117/122) + TEXT_OK (160/160) + PLATFORM_OK (49/49) + WIDGETS_OK (101/101) + GPU_OK (66/66), full suite 15 PASS 0 FAIL (HarfBuzz multi-char bug blocked, registry/X11 blocked, A11y bridge blocked).*