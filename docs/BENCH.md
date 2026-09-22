# Phase 6 — Benchmark đối đầu TokenVector.UI vs PyQt6 (CHUẨN HOÁ 2026-09-19)

> Máy: Windows (x64), PyQt 6.11.0 / Qt 6.11.0,
> tkvc `D:\TokenVector\3.code\dist\tkvc.exe`, .NET Framework 4.x.
> Nguồn bench: `examples/TkvUI.BenchText.tkv`, `examples/TkvUI.BenchWidgets.tkv`,
> `examples/TkvUI.CrudBench.tkv`, `tools/bench/*_pyqt.py`,
> `tools/bench/crud_pyqt_bench_mem.py`, `tools/bench/bench_mem.py`.
> Driver 1 lệnh: `tools/bench_all.ps1` (Windows) / `tools/bench_all.sh` (WSL).
>
> Quy ước chuẩn hoá: **cùng workload, cùng reps, report per-op chuẩn hoá**.
> Timer TKV = GetTickCount (quantum ~16 ms — số 0/16/31/47 là biên lượng tử,
> không phải 0 thật); timer PyQt = `perf_counter` (µs). Chênh timer được ghi
> rõ từng bảng. Số cũ (2026-09-18) giữ ở cuối file để đối chiếu.

## 6.2 Text render — 400 dòng × 54 ký tự = 21.6K chars/block, 5 blocks = 108K

Cả hai bên cùng workload, cùng reps=5. TKV 47 ms ổn định 3/3 lần chạy.

| Bên | Cách đo | 108K chars (5 blocks) | **1 block (21.6K)** | vs PyQt6 |
|---|---|---|---|---|
| **TkvUI atlas** | `text_atlas_draw_string`, GetTickCount | **47 ms** (ổn định, đo lại 2026-09-20) | **9.4 ms** | **0.69x — nhanh hơn ~30%** ✅ |
| PyQt6 | QPainter.drawText lên QImage 340×3200, `perf_counter` | ~68 ms | 13.7 ms | 1.0x (baseline) |
| TkvUI classic | `draw_string` | ~391 ms | ~78 ms | 5.7x chậm hơn |

Runs PyQt 2026-09-20: 14.7/13.4/13.5/13.7/13.0 ms (baseline nhanh hơn lần đo 2026-09-19 là 15.6 ms — máy/môi trường; TKV atlas giữ 47 ms ổn định).
Selftest bench (400 laps × 54 chars cùng vị trí, surface 200×24): classic
78–94 ms, atlas 0–16 ms (chạm ngưỡng timer) — speedup nội bộ **~5–6x**.

**Verdict: THẮNG.** Từ 21.8 ms (2026-09-18) → 9.4 ms nhờ glyph atlas +
ink-pixel list + single-pass char lookup. Đạt target < 10 ms/block.

## 6.3 Widgets — 1000 Button, 10 cột

Cả hai bên: construct 1000 nút ×100 reps; paint/render 1000 nút offscreen
(QImage 820×2600 vs PixelSurface 820×2600) ×5 reps (TKV render ×20, chuẩn
hoá per-render).

| Bên | Construct / 1000 | Paint-Render / 1000 |
|---|---|---|
| **TkvUI** (`make_native_button` + `render`) | **< 0.16 ms** (0–16 ms/100 reps — dưới ngưỡng GetTickCount) | **~30 ms** (593–594 ms/20 reps, ổn định) |
| PyQt6 (QPushButton + `w.render(img)`) | 12.6–12.9 ms (100 reps, ổn định) | ~43–46 ms (steady ~41 ms; lần đầu ~63 ms warmup) |

**Verdict: THẮNG (cả hai vế).** Render từ ~86 ms → ~30 ms (**~2.9x**) nhờ
`fill_round_rect_packed` (band-split, hoist int-cast, inline opaque write,
pixel-exact 352px giữ nguyên) + stroke carve dùng chung. Không đụng text
path: đo trước thấy label 1 char chỉ ~2% pixels/nút — bỏ qua đúng chỗ.

## 6.4 CRUD — 1000 rows staff(id,name,age,city), 10 reps, fresh table/rep

Chuẩn hoá lưu trữ: **cả hai in-memory** (TKV lists vs PyQt `:memory:`) —
loại bỏ artifact fsync/journal của lần đo cũ. Report trung bình/rep.

| Op (1000 rows) | **TkvUI** (lists + rowid-index) | PyQt6 (`:memory:`) |
|---|---|---|
| INSERT | ~1–4 ms (0–47 ms/10 reps — quanh ngưỡng timer) | 8.5 ms (ổn định 8–9) |
| SELECT + SORT | **~1–4 ms** (mergesort + key precompute) | ~0–3 ms (rep1 29 ms warmup, rep2+ < 0.5 ms) |
| UPDATE | **~0–3 ms** (rowid O(1)) | 2.1 ms |
| DELETE | ~1–3 ms (rowid O(1) + compact; cùng thứ tự descending với PyQt) | **0.6 ms** |
| **TOTAL avg/rep** | **~8 ms** | ~14 ms |

**Verdict: THẮNG (~1.8x).** Optimize 2026-09-19 đảo ngược kết quả chuẩn hoá
cũ (thua ~11x):
- `mv_sort_build`: bubble O(n²) → mergesort ổn định + key precompute
  (parse int 1 lần/row): 125 ms → 1–4 ms (**~35x**).
- Rowid-index cho INTEGER PK đơn (`sql_pk_declare`, verify-on-use nên stale
  slot không bao giờ sai): UPDATE 14 ms → 0–3 ms; DELETE find O(1).
- Bench DELETE chuyển ascending → descending (khớp PyQt có sẵn): compact
  cuối-mảng O(1) thay vì shift O(n): 17–20 ms → 1–3 ms.
- PK declare là opt-in; bảng không declare giữ nguyên behavior cũ. Tx
  rollback invalidate index. Selftest SQLite 35/35 (13 check PK mới:
  declare/update/miss/delete/rebuild/dup-fallback/non-int-reject).

Tham khảo persistence (không chuẩn hoá, giữ để đối chiếu): PyQt file-backed
cũ INSERT 164 / SELECT 31 / UPDATE 153 / DELETE 158 / TOTAL 505 ms.

### 6.4c Persistence file-backed (P1, mới 2026-09-19)

Format TKVSQL1 (text, length-prefixed, dual-slot + generation — xem
`docs/SQL_PERSISTENCE.md`). Bench `bench_persist`: staff 1000 rows,
save ×5 + load ×5 (`build/staff_persist.db.a/b`, 29 KB/slot).

| Op (1000 rows, file) | **TkvUI** | PyQt6 (file, CRUD full — workload khác) |
|---|---|---|
| SAVE (snapshot toàn DB) | ~72–78 ms/lần | — (nằm trong TOTAL 505 ms) |
| LOAD (parse + rebuild index) | ~0–3 ms/lần | — |
| Crash-safety | dual-slot: corrupt 1 slot bất kỳ vẫn load OK (16/16 check persist PASS, gồm gen đơn điệu, fallback 2 chiều, both-bad→8, no-file→2) | journal SQLite |

**Verdict: ĐẠT (tính năng).** Lần đầu TKV có persistence file thật với
crash-safety kiểm chứng được (51/51 SQLITE_OK). Save ~75 ms/29 KB còn chậm
(O(n²) string concat khi serialize ~12K chunks — ghi nhận tối ưu sau bằng
chunk-join/StringBuilder extern). So tốc độ với PyQt file CRUD (505 ms)
không cùng workload nên chỉ ghi nhận cạnh nhau, không claim thắng.

## 6.1 Memory — cùng workload text 108K chars, peak RSS tiến trình

Đo bằng `tools/bench/bench_mem.py` (psutil, poll 5 ms). Workload giống hệt
nhau (bench text 108K chars), khác biệt duy nhất là runtime + layout pixel.

| Bên | Peak RSS | Ghi chú |
|---|---|---|
| TkvUI (`bench_text.exe`) | **~46 MB** (45.7–47.1, 3 lần) | pixel `list[i64]` = 8 B/px (gấp đôi QImage) + CLR |
| PyQt6 (`bench_text_pyqt.py`) | **~15.6 MB** (ổn định) | QImage 4 B/px + CPython nền ~11 MB |

**Verdict: THUA (~3x).** Nghiên cứu breakdown 2026-09-19 (chi tiết ở Phụ lục
M1) kết luận pixel `i32` chỉ cứu ~11% với rủi ro refactor toàn repo →
**HOÃN**; giữ verdict thua trung thực.

Số idle cũ (giữ để đối chiếu, workload lệch): TKV live animated 27.6 MB vs
PyQt window trống 38.5 MB.

### Phụ lục M1: MEM breakdown (reflection CLR + batch RSS, đã đo)

| Thành phần bench_text.exe (peak ~46 MB) | Ước lượng | Cách xác minh |
|---|---|---|
| Runtime floor (CLR + mscorlib, exe 5 KB) | ~9.5–10.8 MB | `test_minimal.exe` peak 9552 KB |
| IL size | ~0 (exe 430 KB → peak 9.7 MB) | `testimports.exe` |
| Main surface `buf` 1.088M×i64 | ~16 MB backing (8.7 MB dùng + doubling waste ~7 MB) | probe append 1M: +8.2 MB (slope 8 B/elem); `list[i64]`→`List<Int64>` unboxed, quét opcode `box` trong IL 9 hàm hot = 0 |
| Atlas + glyph tables + strings + JIT heap | ~19 MB (chưa tách được — cần CLR profiler/NGEN, máy không có) | `text_test.exe` (không buffer lớn) peak 36.6 MB vs `fallback_test.exe` (cùng import Text) 9.5 MB |

Kết luận cho plan:
- **Không** migration i32 toàn repo (cứu ~4.5 MB → ~41 MB, vẫn thua 2.6x).
- Muốn giảm thật cần **primitive `reserve(n)` từ compiler** (xoá ~7 MB
  doubling waste — đã thử `[0]*n`: compiler báo lỗi, không có cách làm từ
  phía user) **hoặc** NGEN deployment (nếu JIT heaps là phần lớn của 19 MB —
  chưa xác minh được, cần elevation/profiler).
- Quick-win `codes` scratch (2026-09-19, đã làm): `text_atlas_draw_string_ex`
  nhận scratch list từ caller, wrapper cũ giữ nguyên API. Bench tái dùng 1
  scratch qua 2000 calls (bớt ~10K mảng tạm gen0). Kết quả đo: time không đổi
  (46–47 ms), peak RSS không đổi (~45.9 MB) — churn không phải driver của peak.
  Giữ lại vì giảm GC pressure (tốt cho frame pacing), không break gì
  (Text 160/160 PASS).
- Lưu ý compiler phát hiện khi làm: **không alias param list** (`codes =
  scratch` bị suy kiểu thành i32 → `MissingMethodException` lúc chạy, trong
  khi compile vẫn qua). Dùng param trực tiếp. Đã ghi comment trong code.

## 6.5 Blur (nội bộ, không đối chứng PyQt) — 800×200

| So sánh | Kết quả |
|---|---|
| ref vs opt (r=4, 10 laps) | 2187 vs 2156 ms → **~1.0x** (pixel-exact, không speedup thật) |
| full vs half-res (r=8, 5 laps, gồm copy) | 1063 vs 500 ms → **2.1x** ✅ |

## Tổng kết chuẩn hoá (GO/NO-GO)

| # | Benchmark | Kết quả chuẩn hoá (sau optimize 2026-09-19) |
|---|---|---|
| 6.2 Text | ✅ **Thắng** (9.4 vs 15.6 ms, đạt < 10) |
| 6.3 Widgets | ✅ **Thắng** (construct <0.16 vs 12.6 ms; render ~30 vs ~43 ms) |
| 6.4 CRUD engine | ✅ **Thắng** (~8 vs ~14 ms/rep khi cùng in-memory) |
| 6.4c Persistence file | ✅ **Đạt** (TKVSQL1 dual-slot, save ~75 ms + load ~3 ms / 1000 rows, crash-safety 16/16) |
| 6.1 Memory (load) | ❌ Thua (~3x; floor ~10 MB + doubling ~7 MB + ~19 MB chưa tách được — xem Phụ lục M1; i32 hoãn) |
| 6.5 Blur | ➖ Nội bộ (half-res 2.1x; ref/opt hoà) |

**4 thắng – 1 thua – 1 đạt (persistence mới).** Chuỗi optimize: sort 35x (mergesort) → update 10x +
delete 7x (rowid-index) → render 2.9x (band-split raster) → P1 persistence từ
0 lên có (dual-slot crash-safe). Hạng mục còn lại:
MEM (cần kiến trúc pixel hoặc chấp nhận floor CLR).

## P3-B3 stability gate (chống flake GetTickCount quantum ~16ms)
`tools/bench_stats.py` (10/10 selftest: percentile/median/extract) + driver
`tools/bench_stable.sh` / `.ps1`: mỗi bench build 1 lần, chạy 3 lần, verdict
`BENCH_OK` khi median đạt ngưỡng VÀ spread trong dung sai. Ngưỡng từ bảng
trên + headroom: text atlas tổng <100ms (tol 32), widgets render <900ms
(tol 64), crud total <20ms/rep (tol 16).

Chạy 2026-09-22 (`BENCH_STABLE_OK`): text 63/46/47 → med 47 (rep đầu nhảy
quantum nhưng median vẫn PASS — đúng giá trị của gate), widgets
579/579/563 → med 579, crud 6/7/8 → med 7.

## Verdict HD video (MJPEG thuần .tkv, 2026-09-22)

| Case | Số đo thật | Kết luận |
|---|---|---|
| 160×120 baseline | 5 reps = 47ms → **~106fps** | Thừa realtime cho preview/thumbnail |
| 1280×720 (bake 8 chunk 44.5KB) | 453ms → **~2fps**, đúng pixel (first/last ±2, sum ±1 avg) | Đúng nhưng không realtime |
| Profile 160×120 | Huffman ~9% (~1ms), IDCT float ~60% (~7ms), còn lại ~30% | IDCT là nút cổ chai |

Ngoại suy tuyến tính: 320×240 ~25fps, 640×480 ~6fps. Kể cả optimize hết
(AAN + reuse + lookahead ≈ 2.5×) cũng chỉ ~5fps@720p. Realtime HD cần
bitwise (`>>`/`&` thay `//`/`%`, nhanh 10–50× cho bit-reader) và/hoặc SIMD
từ compiler — gap số 1 cho codec, đã ghi trong `docs/COMPILER_GAPS.md`.
Đường TKVV custom (không Huffman/IDCT) mới là ứng viên realtime — để tiếp.

## Verdict HD realtime (TKVV fast path, 2026-09-22)

Presized buffers + RGB trực tiếp (0 append): đo 200-400 reps —
I-decode 0.70ms, P-decode 0.20ms, render 0.55ms @320×240 (76.8k px),
tuyến tính đã kiểm (32×24 cho cùng ~9ns/px). Ngoại suy tuyến tính:

| Khung hình | I-frame | P-frame + render (typical) | Kết luận |
|---|---|---|---|
| 320×240 | ~0.7ms | ~0.75ms | đo trực tiếp |
| 1280×720 (×12) | ~8.4ms | ~9ms | **~100fps, realtime dư headroom 4×** |
| 1920×1080 (×27) | ~19ms | ~20ms | ~50fps chiếu theo tuyến tính |

Content đo: `tools/tkvv_hd_gen.py` (320×240 ball+square, I 76.8KB + P ~7KB,
200-400 reps, GetTickCount). Chạy lại: `tkvc.exe build
examples/TkvUI.TkvvBench.tkv --entry tkvvbench_run --out build/tkvvbench.exe`
(asset `TkvUI.TkvvHD.tkv`, ngoài verify.sh để suite gọn nhẹ).

## P2 Typography (chức năng — Text 227/227, Bidi 150/150)

- Composite glyf + kern/CPAL/COLR-v0 parse + CBDT-bitmap blit + per-slot
  advances (hmtx) trong draw i18n (hết fixed-6px); COLR draw từng layer
  (tint palette, SrcOver).
- Sửa 2 bug nền: rasterizer mirror upward-edges; parser emit X/Y-block
  trong khi consumer đọc interleaved.
- Quy tắc compiler mới (trả giá bằng 1 buổi debug): method **< 240 locals**
  (ldloc.s 1-byte; 272 locals → slot aliasing → crash lạ) — guard
  `tools/check_locals.py`; int×float viết `float(x) * y` tường minh;
  không alias param list; args BaseGlyphRecord là 8 bytes (u32+u16+u16).

## Phụ lục: số cũ 2026-09-18 (trước chuẩn hoá, workload lệch)

| Hạng mục | Số cũ | Vấn đề chuẩn hoá đã fix |
|---|---|---|
| Text | TKV 21.8 vs PyQt 14.2 ms/block (thua 35%) | Đã optimize → 9.4 ms, thắng lại |
| Widgets construct | TKV "0 ms/100K" vs PyQt 12.3 ms/1000 | Reps PyQt 20→100; thêm paint/render cả hai; render optimize → thắng |
| CRUD throughput | TKV 177 vs PyQt 425 ms (thắng 2.4x) | Artifact file-vs-memory; chuẩn hoá :memory: từng thua ~11x → optimize (mergesort + rowid) → thắng lại ~8 vs ~14 ms |
| Memory idle | TKV 27.6 vs PyQt 38.5 MB (thắng) | Workload lệch (animate vs trống); đo lại cùng workload → thua ~3x |
