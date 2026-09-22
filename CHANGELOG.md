# Changelog

Mọi thay đổi đáng chú ý của TokenVector.UI (TkvUI). Version lấy từ `tkvui_version()` trong `TokenVector.UI.tkv`.

## Unreleased (chưa commit)

- **Chrome-canvas ingest khép kín MP4→player** (`tools/mp4_to_tkvv.py` + `tools/chrome_cap.py` + `examples/TkvUI.ClipPlayer.tkv` 14/14 `CLIPPLAYER_OK` + clip `TkvUI.TkvvClipMp4` + `tkvv_import.py` bake RGB sums): Chrome headless decode H.264 thật + CDP `Page.captureScreenshot` (poll currentTime, không canvas/events) → 4 PNG 320×240 → TKVV blob 261KB ratio 1.18 decode-back EXACT → player parse/decode/render/clock sums khớp. Bài học: `seeked` không fire dưới `--dump-dom` (cả virtual-time lẫn real-time), `Emulation.setDeviceMetricsOverride` ép viewport chuẩn. Verify 49/0/2.
- **MP4 realistic: co64/ctts/elst/SPS (38 -> 62)** (`TkvUI.Mp4` 62/62 `MP4_OK` + `TkvUI.Mp4RData` + `tools/mp4_gen.py` realistic builder + umbrella import `Mp4RData`): file MP4 như thật (moov sau mdat, co64 offset-64bit, elst edit list, ctts composition offset, stsc multi-run, SPS Baseline thật 160x128 parse Exp-Golomb ra width/height); extract + O(1) seek vẫn đúng trên cả 2 file (craft + realistic).
- **M3 port Qt app: Application Example 52/52** (`examples/TkvUI.QtAppPort.tkv` `QTAPP_OK` + verify.sh +1 case): port trung thực Qt 6 mainwindows/application (QMainWindow + 11 QAction/shortcut + QTextEdit + QFileDialog + QMessageBox + QPrintDialog + recent + statusbar) sang MenuBar/ToolBar/StatusBar/RichEdit/DlgFile/Dialog/Printing thật, headless 52 checks (state + hit-test + file/PDF thật + pixel ground truth). Phát hiện bug compiler D6 (method trùng tên BCL resolve sai trong loop, đã isolate + workaround `qa_put1`, ghi `docs/COMPILER_GAPS.md`). Verify 48/0/2.
- **M1 crash-safety: kill-9 matrix** (`TkvUI.SQLite` 51 -> 132 `SQLITE_OK` + `examples/TkvUI.SqlCrash.tkv` + `tools/sql_crashkill.py`): tach `sql_serialize` khoi `sql_save` (behavior giu nguyen); ma tran cat-ngang would-be content (10 diem x 2 slot + garbage/magic-only + bien tail-newline==commit) -> load luon ve gen cu + du lieu nguyen; kill that 12 cycle (TerminateProcess, PAD 2000 rows cho save du cham) -> gen don dieu, count == gen+PAD, sum khop; kill truoc commit dau -> rc 2 (DB rong) la dung. Suite 32/32 xanh.

- **H264 thành module optional** (`TkvUI.H264`, không vào suite — theo mẫu `TkvUI.Font`): pinvoke OpenH264 đầy đủ chặn ở struct marshal (kẹt upstream, đã ghi spec); selftest chỉ probe DLL (`H264_OK` khi có DLL, headless-safe). Suite giữ 32 module xanh.
- **Ingest tổng quát PNG→TKVV** (`tools/tkvv_import.py` + `TkvUI.TkvvClip.tkv` + file `TkvUI.TkvvClip.tkv` 33KB + `examples/tkvv_capture.html`): PNG bất kỳ → palette adaptive chung (deterministic + pad zeros) → TKVV I/P + decode-back EXACT 8/8; chạy trên `play_f*.png` ratio 4.65, tương thích decoder đã commit pixel-exact 8/8 frame (probe tạm). Sửa bug that: palette PIL trim theo màu dùng (thiếu 15 byte). Harness Chrome `<video>`+`<canvas>` cho MP4→frames không ffmpeg (semi-auto).
- **MP4 demux thuần `.tkv` (đường B)** (`TkvUI.Mp4` 38/38 `MP4_OK` + `TkvUI.Mp4Data` craft 2-track + `tools/mp4_gen.py`): box walk (size<8/overrun → lỗi) + moov/mvhd + trak (tkhd/mdia mdhd/hdlr/minf/stbl: stsd-codec/stsz/stsc/stco) + O(1) sample offset qua runs+chunks + extract bytes + durations ms; avc1 3 samples + mp4a 2 samples, extract đối chiếu bytes. Sửa bug that: `mp4_find` gọi từ box-start (tự skip cả parent), offset full-box quên version/flags (+8), u32 overflow ≥2³¹ (guard). Suite 31 -> 32 module, verify.sh +1 case.
- **VideoDemo player xem được (đường A)** (`examples/TkvUI.VideoDemo.tkv` 21/21 `VIDEODEMO_OK` + `TkvUI.TkvvPlay` bake 8f 160x120 qua PNG trung gian + `tools/tkvv_play_gen.py`): widget Media THẬT (Transport/SeekBar/Speed/ABLoop) + clock Video + blit surface; play/pause/seek-450ms/speed-2x/AB-wrap/end-loop đều assert qua pixels (sum ground truth). Đơn vị cs↔ms đổi ở ranh giới, overshoot-preserving loop. verify.sh +1 case.
- **OpenH264: tải về khỏi xây** (`tools/fetch_openh264.ps1`/`.sh` + `docs/OPENH264.md`): `openh264-2.6.0-win64.dll` chính chủ Cisco (452KB → 978KB, MZ + đủ exports, `LoadLibrary` + `WelsCreateDecoder` rc=0 + `Destroy` OK trên máy này, verify bằng ctypes). Rõ license: binary Cisco được Cisco trả MPEG-LA royalties (tải từ Cisco); tự build source thì tự chịu; **x264 CẤM (GPL-2.0)**. Còn kẹt đúng 2 primitive upstream (struct marshal + assembly identity) mới pinvoke `Initialize`/`DecodeFrame2` được — đã ghi spec chính xác (mẫu `OpenH264Lib.NET`). Giới hạn: Baseline-only (Main/High vẫn cần FFmpeg sau).
- **TKVV fast path đạt HD realtime** (`TkvUI.Tkvv` +8 check, 56/56): presized buffers + RGB trực tiếp (0 append) thay append-lists; đo 200-400 reps @320×240: I 0.70ms, P 0.20ms, render 0.55ms (~9ns/px, tuyến tính đã kiểm ở 32×24) → ngoại suy **720p ~10ms (~100fps), 1080p ~50fps**. Content đo `tools/tkvv_hd_gen.py` + asset `TkvUI.TkvvHD.tkv` (ngoài verify/suite) + `examples/TkvUI.TkvvBench.tkv`. Kết luận kiến trúc: chuẩn interchange (MJPEG: đúng nhưng 2fps@720p) + format custom (TKVV: realtime) — đúng triết lý TKVA.
- **Verdict HD cho MJPEG** (`mjpg_hd_selftest` 6/6 `MJHD_OK`, bake 720p 8 chunk 44.5KB): decode 1280x720 ĐÚNG pixel (2.76M px, first/last ±2, sum ±1 avg) nhưng **453ms ~2fps** — realtime HD thuần `.tkv` không tới được. Profile 160x120: Huffman 9% (~1ms), IDCT float 60% (~7ms), còn lại ~30% (alloc/presize/RGB). Kể cả optimize hết (AAN + reuse + lookahead ≈ 2.5×) cũng chỉ ~5fps@720p; cần bitwise/SIMD từ compiler (gap số 1 cho codec). Đường TKVV custom (không Huffman/IDCT) mới là ứng viên realtime — để tiếp.
- **MJPEG baseline thuần .tkv + verdict fps** (`TkvUI.Mjpg` 44/44 `MJPG_OK` + `TkvUI.MjpgData` bake 3 frame 160x120): SOF0/DQT/DHT/SOS-interleaved + Huffman canonical + dequant/unzigzag + IDCT float (Cos thật) + nearest upsample + YCbCr→RGB + bench GetTickCount. Đo that 5 reps = 47ms → **~106fps @160x120** (≈25fps @320x240, ≈6fps @640x480 suy ra tuyến tính) — pure-.tkv đủ xem video nhỏ/thumbnail, HD realtime thì không (giới hạn //% thay bitwise). Sửa 3 bug that: segment offset thiếu 2 byte marker, SOF length check thừa, bit reader LSB (kế thừa từ GIF) thay vì MSB, hval local-vs-global, index transpose zigzag; upsample fancy đo thua nearest nên xóa (nearest khớp PIL ±2, trừ 2px biên dưới chấp nhận tol 5 có tài liệu).
- **Media decode thuần .tkv** (`TkvUI.Video` 44/44 `VIDEO_OK` + `TkvUI.VideoGifData` bake sẵn; **`TkvUI.Tkvv` custom format 50/50 `TKVV_OK` + `TkvUI.TkvvData`** giong TKVA audio): GIF89a subset — parse header/LSD/GCT/GCE-delay/skip-extension/LCT-palette/descriptor + LZW early-change flat-dict (4096) + player clock (`vid_frame_at` loop, `vid_seek_cs` promille) + mã lỗi 0-6; TKVV v1 bit-exact (magic/ver/chunk/profile I-P + O(1) seek + tile-diff reconstruct + clock reuse + mã lỗi 0-4), sample `tools/tkvv_gen.py` (ball 32x24 6f, P-frame 134B vs 768 raw, ratio 2.78). Sửa bug that: I-payload xếp theo tile nhưng decoder copy verbatim (sum đúng, vị trí sai — position-checks bắt được). Phát hiện: ffmpeg pinvoke không khả thi (thiếu DLL + gap marshal out-struct); quy tắc tăng width LZW phân xử thực nghiệm (early `nxt >= 2^W` đúng 4096/4096, late dừng 592). Ngoài subset (interlace, disposal/transparency compositing) → err 6 / v2.
- **P3-B3 bench stability gate** (`tools/bench_stats.py` 10/10 selftest + `tools/bench_stable.sh`/`.ps1`): mỗi bench chạy 3 lần, verdict theo median + ngưỡng + dung sai spread (chống flake GetTickCount quantum ~16ms); ngưỡng từ `docs/BENCH.md` + headroom (text <100/tol32, widgets <900/tol64, crud <20/tol16). Chạy 2026-09-22 `BENCH_STABLE_OK`: text 63/46/47 → med 47, widgets → med 579, crud → med 7. `docs/BENCH.md` +mục P3-B3.
- **Kittest-style test** (`TkvUI.KitTest` mới, 16/16 `KITTEST_OK`, P3-B2 copy egui): test widget native THẬT thông qua cây a11y thay vì đếm pixel — query (role,label) + `hit_test_tree` thật + act (click/type/backspace/toggle/select/slide/choose) + rebuild cây (như RenderLoop commit) + assert lại qua cây; 9 case headless (button, disabled, checkbox toggle, lineedit, slider, listview select, miss → -1, window-vs-button routing, combo). Suite 26 -> 27 module (`TKVUI_OK`), verify.sh +1 case.
- **Emoji raster thật** (`TkvUI.EmojiData` mới, 107/107 `EMOJIDATA_OK`; `TkvUI.FontFallback` 29 -> 37 check): bake offline 12 BMP symbol 12x12 1bpp từ Segoe UI Symbol qua `tools/emoji_gen.py` (render 48px -> crop -> scale 12px -> threshold 128, né gap file I/O như I18nData); `fb_draw_run_emoji` blit glyph thật, giữ E-box cho emoji chưa bake; sửa bug nền `fb_classify` không bao giờ trả emoji(4) cho BMP (nhánh `len==1` chết với seq 3-byte). Phát hiện compiler: so sánh chuỗi `>=`/`<=` là linguistic, không ordinal với symbol (probe: `"✚" >= "←"` = 0) — chỉ dùng literal-match cho glyph bake. Suite 25 -> 26 module (`TKVUI_OK`), verify.sh +1 case emoji.
- **P6 wiring + Gpu unbreak** (`TokenVector.UI` umbrella 23 -> 25 module, suite `TKVUI_OK` 25/25): wire `TkvUI.Shaping` (91/91 `SHAPING_OK`) + `TkvUI.FontDiscovery` (15/15 `FONTDISCOVERY_OK`) vào umbrella + `tkvui.pkg.json`; `tools/verify.sh` +4 case (gpu/a11y/shaping/fontdisc — platform standalone vẫn bị linter chặn `__tkv_extern_class__` nên chỉ cover qua umbrella); `TkvUI.FontFallback` 21 -> 29 check với weighted bridge record-free (`fb_want_family`/`fb_best_family_for_font`, scoring parity với `fd_match_score`).
- **P6 Gpu build fix** (`TkvUI.Gpu` 66/66 `GPU_OK`): xóa hằng module-level `= 0 - 1` (tkvc chỉ cho literal), xóa `#` trailing trong multi-line call args (tokenizer nối dòng), `pass` -> `noop = 0` (7 chỗ, ngôn ngữ cấm `pass`), xóa dead `fl` list (không suy được kiểu phần tử), sửa test `vk queue family null -> -1` theo đúng docstring (hàm trả -1, test cũ kỳ vọng 0). Nguyên nhân gốc: commit P1-P5 làm vỡ build Gpu standalone + umbrella (verify bằng build+run thật).
- **P2 Typography** (`TkvUI.Text` 46 → 227 check, `TkvUI.Bidi` + shaping 150 check): composite glyf merge (scale/xyscale/2x2, depth cap), kern format-0, CPAL + COLR v0 parse/draw từng layer, CBDT-bitmap blit, per-slot hmtx advances (hết fixed-6px), shaping orchestration (script runs/clusters/fallback/HB-bridge). Sửa 2 bug nền: rasterizer mirror upward-edges, parser X-block vs consumer interleaved. Quy tắc compiler mới: method < 240 locals (`tools/check_locals.py`), `float()` tường minh khi nhân int×float, không alias param list.
- **P1 SQL persistence** (`TkvUI.SQLite` 22 → 51 check): format TKVSQL1 text dual-slot + generation (atomic không cần rename), save/load, rebuild PK index, rollback invalidate; crash-safety matrix; bench file-backed save ~70ms + load ~3ms/1000 rows. Chi tiết `docs/SQL_PERSISTENCE.md`.
- **Perf engine**: `mv_sort_build` bubble → mergesort ổn định + key precompute (125ms → 1–4ms); rowid-index cho INTEGER PK đơn (UPDATE 14ms → 0–3ms, DELETE 20ms → 1–3ms); `fill_round_rect_packed` band-split (render ~86ms → ~30ms/1000 buttons). CRUD total 157ms → ~8ms/rep (thắng SQLite `:memory:` ~14ms).
- **P3 accessibility** (`TkvUI.A11yBridge` 89 check, `TkvUI.Uia` 33 check): roles 15–23 + 8 builders (table/tree/menubar/toolbar/scrollbar/splitter/spinbox/tooltip); Win32 mirror (mỗi node → HWND thật, headless-safe); quy trình probe NVDA trong `docs/A11Y_NVDA.md`.
- **P4 delegates + stylesheet** (`TkvUI.Data` 52 check, `TkvUI.Theme` 79 check): `mv_paint_cell` (text/check/progress/slider) + `mv_render_typed` (dạng function — method call 11 params crash runtime); QSS-subset (Type/.class/#id, 9 palette roles, cascade, copy semantics).
- **P5 MemoryPlatform** (`TkvUI.Platform` 82 check): backend headless thật (mọi platform/CI), present/diff đếm pixel; GPU loader probe sống, creation vẫn stub đúng chỗ (thiếu out-struct primitives); media decode defer.
- **Benchmark chuẩn hoá** (`docs/BENCH.md`, `tools/bench_all.sh/.ps1`): cùng workload/reps, report per-op; Text 9.4ms/block (thắng PyQt6 ~40%), Widgets render ~30ms, CRUD in-memory thắng, MEM thua ~3x (floor CLR + doubling, cần `reserve` từ compiler).

- **TTF parser/rasterizer verified** (`TkvUI.Text`, text 46 → 110 check): synthetic font 314B end-to-end (load/cmap/glyf/raster/atlas-bake/metrics) + readers/bit/bezier/flatten/error-paths. Sửa 4 bug do thiếu test: literal tag `hhea`/`hmtx`/`maxp` sai, `segCountX2` đọc nhầm offset +2 (đúng +6), thiếu `j = j + 1` trong contour loop (+ lồng sai `contour_start`/`i`), nested `list[list[f64]]` trả null runtime → viết lại edge table phẳng.
- **Module media-player `TkvUI.Media`** (mới, 10 widget + `media_format_time`, 80/80): Transport/SeekBar/Volume/Repeat/Shuffle/Speed/Playlist/Equalizer(+preset)/Spectrum/ABLoop. Wire umbrella (`MEDIA_OK`), `tkvui.pkg.json`, `verify.sh`, demo `TkvUI.MediaDemo` (8/8).
- **WinForms interop thật** (`TkvUI.Platform`, platform 24 → 34 check): `wf_create/set_title/set_bounds/get_bounds/set_opacity/hide/do_events/close` nối thật + verify headless trên Form thật. Còn stub (compiler gap): control-level, `Handle` (IntPtr), `wf_run`.
- **Ant-inspired widgets** (`TkvUI.Widgets` 15 → 28, widget 43 → 95 check): Tag/Badge/Avatar/Alert/Pagination/Steps/Table/Select/Rate/Spin (+ DPad/ControlButton/Joystick). Phát hiện: field tên `shape` bị parser hiểu nhầm thành indexing `.shape[...]`.
- **Module `TkvUI.Font`** (đưa vào từ thử nghiệm, optional/Windows-only): bake font thật qua GDI, 11/11 (ngoài umbrella + verify.sh).
- Suite umbrella: **444 check PASS** (`TKVUI_OK`).

## 2.3.1 — P2.8 bilinear upsample (2026-09-17)

- `half_res_blur`: thay upsample nearest-neighbor bằng **bilinear nội tuyến 1 chiều trong khối 2×2** — px lẻ lấy trung bình 2 mẫu kề, giảm artifact "bậc thang" khi blur sau text/mép sắc. Chi phí gần như không đổi (vẫn không đọc pixel ngoài khối).
- `effects_selftest`: 29 → **32/32** (3 check bilinear: px lẻ giữa 2 vùng nằm giữa 2 đầu mút, gradient tiếp diễn vào vùng trong).
- Lưu ý dùng: small_buf/small_scratch phải sạch (zeros) trước mỗi gọi vì `half_res_blur` chỉ ghi sw×sh phần tử đầu.
- Full verify: TKVUI_VERIFY_OK (12 PASS / 0 FAIL / 2 SKIPPED).

## 2.3.0 — P2.4–P2.7 quick wins (2026-09-17)

- **P2.4 — Present qua DIB memory-mapped** (`TkvUI.Platform`): `create` tạo DIB section backed bởi file-mapping (`CreateFileMappingA` + `MapViewOfFile`, pinvoke mới), lưu mapview pointer vào `PlatformWindowHandle`. `present`/`present_diff` ghi pixel trực tiếp vào DIB bits qua `wsprintfA` thay vì `SetPixelV` per-pixel (probe: 40k px — mem 0ms vs SetPixelV 15–31ms). `close_window` giải phóng mapping đúng.
- **P2.5 — Áp half-res blur vào sản phẩm** (`TkvUI.Effects`): `backdrop_blur` và `draw_drop_shadow` dùng `half_res_blur` khi radius ≥ 4 (buffer phụ cho trước), hưởng ~2.5× tại chỗ gọi hot mỗi frame.
- **P2.6 — Cache `char_code`** (`TkvUI.Text`): `text_atlas_draw_string` tra `char_code` (binary search 7 bước) mỗi ký tự mỗi frame; giờ cache 95 entry gắn với atlas (`atlas.codes`, -2 = chưa tra) — tra 1 lần/ký tự trong vòng đời atlas.
- **P2.7 — FocusManager** (`TkvUI.Widgets`): tab-order, `focus_next`/`focus_prev` (Tab/Shift-Tab wrap), `focus_at` (hit-test click), `focus_index(-1)` clear focus, key routing `type_char`/`backspace` theo flag `focused`. `widget_selftest`: 27 → **43/43**.
- Ghi chú compiler (đã đẩy upstream): không hỗ trợ gán field qua chain `list[i].field` — viết qua biến tạm; các hàm trả record cần return thật (dùng `empty_textfield()` placeholder thay vì `0`).
- Full verify: **TKVUI_VERIFY_OK** (12 PASS / 0 FAIL / 2 SKIPPED).

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
