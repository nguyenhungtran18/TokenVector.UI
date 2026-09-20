# TokenVector.UI — Plan Bổ Sung (Phase 6–12): Những Gì Còn Thua PyQt6

> **Nguyên tắc:** chỉ tuyên bố thắng khi có số đo đối đầu trên cùng máy.
> File này liệt kê đúng các gap đã thừa nhận ở review "đánh bại PyQt6 mọi mặt?",
> mỗi phase có deliverable + phép đo + blocker.

---

## PHASE 6: BENCHMARK DOI DAU -- DONE (ti so 2-2, dung nguong GO)

**Ket qua do that** (PyQt 6.11.0, cung may, chi tiet `docs/BENCH.md`):

| # | TkvUI | PyQt6 | Ket qua |
|---|---|---|---|
| 6.1 Memory | **27.6 MB** (cua so animate) | 38.5 MB (cua so trong) | DONE-thang, dat < 30 |
| 6.2 Text 400x54 | **21.8 ms/block** | **14.2 ms/block** | DONE-thua ~35%, truot < 20 |
| 6.3 Widget x1000 | **< 0.0002 ms/w** | 0.0123 ms/w | DONE-thang (ca 2 qua) |
| 6.4 CRUD dev time | ~1.5 phut, thieu persistence + GUI | ~0.5 phut, SQLite file + dialog that | DONE-thua tinh than |

Deliverable thuc te: `examples/TkvUI.BenchText.tkv`, `TkvUI.BenchWidgets.tkv`,
`TkvUI.CrudDemo.tkv` (+ `CRUD_TKVUI_OK` trong verify) + `tools/bench/*_pyqt.py`.

**GO/NO-GO:** 2-2 -> dung nguong, khong claim thang.

---

## PHASE 7: WASM THẬT (Tuần 3–4)

**Vấn đề hiện tại:** AOT publish ra bytes giống hệt interpreter; bundle chỉ chạy console WASI, chưa render ra browser.

| # | Việc | Blocker | Workaround/Mục tiêu |
|---|---|---|---|
| 7.1 | Dieu tra AOT fallback -- CLOSED: .NET 9 xoa workload; khong duong AOT nao | (da thu .NET 9.0.318) | docs/WASM_STATUS.md |
| 7.2 | So sanh runtime -- DONE: interp PASS wasmtime (DATA_OK); AOT fail = "WASM = interpreter" | -- | docs/WASM_STATUS.md |
| 7.3 | Browser canvas -- DONE: render that qua Chrome headless (screenshot + frame) | (rAF song) | `TkvUI.BrowserDemo` + `BROWSER_OK` |

**Deliverable:** `docs/WASM_STATUS.md` -- DONE (interp DONE / AOT CLOSED / browser-canvas DONE)

---

## PHASE 8: NATIVE INTEGRATION (Tuần 5–7)

**Vấn đề hiện tại:** widget tự vẽ "giống" Win32 nhưng không phải control thật.

| # | Việc | Blocker (đã biết) | Hướng đi |
|---|---|---|---|
| 8.1 | File/Color/Font dialog native -- BLOCKED (marshal out-buffer, upstream) | -- | cho `TkvUI.NativeDlg.tkv` |
| 8.2 | IME day du -- BLOCKED (cung blocker 8.1) | -- | cho pump `WM_IME_*` |
| 8.3 | Per-monitor DPI -- DONE (Platform 64/64: GetDpiForWindow + fallback + watch; run_live OK) | pinvoke don gian | `OsTheme.set_scale`, AnimDemo 9/9 |
| 8.4 | OS animations -- DONE (Theme 59/59: OsAnim+ease+hover/open; 60 frames 375ms) | Tween/Spring co san | `ANIM_OK` |
| 8.5 | RTL -- DONE detect+mirror (LCID + os_mirror_x; 64/64, 59/59) | LocaleName blocked | mirror full Flex: follow-up |

**Deliverable:** DPI/RTL/animation DONE co test; `TkvUI.NativeDlg.tkv` doi unblock marshal.

---

## PHASE 9: ACCESSIBILITY THẬT (Tuần 8–10)

**Vấn đề hiện tại:** JSON dump + stub, chưa từng qua NVDA/VoiceOver.

| # | Việc | Blocker | Hướng đi |
|---|---|---|---|
| 9.1 | Test NVDA that -- DONE (`docs/A11Y_NVDA.md`): control doc duoc, TkvUI vo hinh | (NVDA portable + log parse) | bang pass/fail theo role |
| 9.2 | UIA COM provider -- BLOCKED (COM vtable; can shim C# + fix upstream) | -- | huong host-driven file-watch |
| 9.3 | AT-SPI Linux -- BLOCKED (.so pinvoke) | -- | Orca tren VM khi xong |
| 9.4 | JNI TalkBack / ObjC -- BLOCKED (shim + device that) | -- | contract san, cho device |

**Deliverable:** `docs/A11Y_NVDA.md` DONE (NVDA); bang full 4 nen doi 9.2-9.4 unblock.

---

## PHASE 10: PLATFORM THẬT (Tuần 11–14)

| # | Việc | Hiện trạng | Mục tiêu test |
|---|---|---|---|
| 10.1 | X11 backend thật | Stub | Cửa sổ ARGB + `_NET_WM_WINDOW_TYPE_DOCK` trên Ubuntu VM, screenshot diff | CHUA LAM (can VM/device)
| 10.2 | Cocoa backend thật | Stub (WinForms vehicle) | Build trên Mac thật, cửa sổ `NSPanel`, không crash | CHUA LAM (can VM/device)
| 10.3 | Android on-device | Contract chưa verify | `pack_apk.sh` (cần maui workload) → `adb install` → screenshot + touch log | CHUA LAM (can VM/device)
| 10.4 | iOS on-device | Script gate Darwin | Build trên Mac + Xcode → TestFlight/device, VoiceOver smoke test | CHUA LAM (can VM/device)

**Deliverable:** mỗi platform một `docs/PLATFORM_<os>.md` "đã chạy thật + ảnh chụp", thay cho dòng "stub" trong pkg.json.

---

## PHASE 11: TEXT SHAPING & FONT (Tuần 15–16)

| # | Việc | Hiện trạng |
|---|---|---|
| 11.1 | Font fallback -- CHUA LAM | Atlas don font | cho `TkvUI.FontFallback.tkv` |
| 11.2 | Complex script (Indic/Thai) -- CHUA LAM | Bidi co, shaping chua | -- |
| 11.3 | TTF subset+embed PDF -- BLOCKED (can byte array) | stub san | -- |
| 11.4 | Fuzz shaping -- DONE mot phan (`TkvUI.Fuzz.tkv` rasterizer+model 500 ops, FUZZ_OK) | -- | fuzz shaping-specific: follow-up |

**Deliverable:** 11.4 partial DONE; 11.1/11.2/11.3 + `docs/TEXT_STATUS.md` CHUA LAM.

---

## PHASE 12: TOOLING & QUALITY (Tuần 17–18)

| # | Việc | Hiện trạng |
|---|---|---|
| 12.1 | Designer GUI tuong tac -- DONE (+450 dong: handlers, headless 19/19, windowed OK) | -- | dung chinh Native widgets |
| 12.2 | Docs nguoi dung -- DONE (`docs/TUTORIAL_CRUD.md` 15 phut) | -- | -- |
| 12.3 | CI matrix -- CHUA LAM | chay tay | workflow + ghi unverified |
| 12.4 | Fuzz rasterizer/model -- DONE (trong verify, FUZZ_OK) | -- | `tools/fuzz.sh` rieng: chua lam |

**Deliverable:** DesignerApp + tutorial + fuzz DONE; CI workflow CHUA LAM.

---

## THỨ TỰ ƯU TIÊN (nếu thiếu người)

1. **Phase 6** (rẻ nhất, giá trị claim cao nhất — 2 tuần, 1 người). DONE.
2. **Phase 8.3 + 8.4** (DPI + animation: pinvoke đơn giản, làm được ngay). DONE.
3. **Phase 7.3** (browser canvas — quyết định WASM có dùng được thật không). DONE.
4. **Phase 9.1** (NVDA test — rẻ, chỉ cần cài NVDA + checklist). DONE.
5. Còn lại theo blocker upstream (COM vtable, `.so` pinvoke, byte array, .NET 9) — track riêng, không block release.

## ĐỊNH NGHĨA "XONG" CHO CẢ PLAN BỔ SUNG

- [x] Bang success criteria 10/10 dong CO SO DO (xem P1).
- [~] `docs/*_STATUS.md`: WASM DONE, A11y partial (NVDA only), Platform/Text CHUA.
- [x] `verify.sh` TKVUI_VERIFY_OK (30 PASS / 0 FAIL).
- [x] Khong tuyen bo dong chua co bang chung (thua/gap ghi ro).
