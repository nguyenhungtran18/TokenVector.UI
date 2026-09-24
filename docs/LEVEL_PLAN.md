# Kế hoạch san bằng — TokenVector.UI vs Đối thủ

> Cập nhật: 2026-09-24. Nguồn: `docs/COMPETITORS.md` (verify 55/0/2), `COMPILER_FIX_LIST.md`, `COMPILER_GAPS.md`.
> Mục tiêu: biến từng "thua" thành "thắng được" hoặc "hòa có điều kiện" — có acceptance test đo thật.

---

## 0. Bảng điểm thua → mục tiêu san bằng

| # | Điểm thua (hiện tại) | Đối thủ | Mục tiêu | Effort | Blocker |
|---|---|---|---|---|---|
| L1 | Widget breadth 43 → **88** (Wave A done) vs ~1000 | Qt | **~80–100** (top-40 Qt gap đóng) | L | không |
| L2 | Shaping **chưa wire draw-path** (HB core打通 23/09) | Qt full HarfBuzz | complex-script render đúng qua atlas | M | leaf module design |
| L3 | Cold-start **~1.0 s** (AV+JIT) | PyQt ~0.2 s | **<0.3 s** warm / <0.5 s cold sạch | M–L | **R10 NGEN/AOT (upstream)** |
| L4 | GPU **stub** (device ops 11 stub) | Qt RHI / egui wgpu | compute-blit/blur thật trước, render sau | L–XL | host GPU + R1/R2 đã mở |
| L5 | OS look **self-drawn 28** | Qt native style | theme Win11/11 match DPI+accent (partial) | M | không |
| L6 | Media **Baseline-only**, không playback HW | QtMultimedia full | Main/High via FFmpeg LGPL + audio clock | L | FFmpeg pinvoke (R1/R2 ok) |
| L7 | A11y **HWND mirror v1**, NVDA chưa đọc widget | Qt native UIA | NVDA đọc label/value/role (COM shim C#) | M | **C# COM shim** (đường đã chọn) |
| L8 | Cross-plat **X11/Cocoa stub** | Qt/Slint/egui | Linux X11 thật (headless CI trước) | L | **R7 `.so` (upstream)** |
| L9 | CI **static-only** (ci.yml) | Slint GUI e2e / egui kittest | matrix Win+Ubuntu build+run suite | M | tkvc machine-local → cache artifact |
| L10 | Ecosystem **0 star / 0 issue** | 24k–76k stars | docs/demo/nuget.org + 1 external user | S–M | public repo |

**Không theo đuổi (đã chốt / âm ROI):** pixel `list[i32]` migration (F3 hoãn), MultiIndex, full Qt widget parity 1:1, GPU 4K@120fps ngay (làm compute trước).

---

## L1. Widget breadth — 43 → ~100

**Hiện tại (2026-09-24):** catalog **93 constructors** (Widgets 42 + Native 41 + Media 10). Wave A **DONE**: 10 widget mới + `WIDGETS_BREADTH_OK` (88 ≥ 80) + `widget_selftest` 167/167. Wave B **DONE**: Dock float/tab + MDI tile_h + Ribbon + PropertyGrid + TreeView multi-sel + ContextMenu + Qt Tree/Dock port 31/31 `QTDOCK_OK`. Còn: Thai/Deva box fallback, ASCII bench đo lại.

### Wave A — Top-10 Qt gap (app CRUD thật thiếu) ✅ DONE 2026-09-24
| Widget | Reuse | Effort | Acceptance |
|---|---|---|---|
| `CalendarWidget` | Date arithmetic + grid render | S | `CAL_OK` chọn ngày/tháng, paint cells ✅ |
| `DateTimeEdit` | LineEdit + Calendar popup | S | parse/format vi-VN + popup ✅ |
| `ToolBox` | Tab-like stack | S | switch page, hit-test ✅ |
| `StackedWidget` | đã có concept Layout | S | index switch + selftest ✅ |
| `ScrollBar` (dedicated) | Scroll của List/Table | S | range/page/step, drag thumb ✅ |
| `Dial` | Rate/Slider rotate | S | angle↔value, paint arc ✅ |
| `CommandLinkButton` | Button + description glyph | S | render + click ✅ |
| `KeySequenceEdit` | Input + chord parse | M | capture Ctrl+S…, selftest ✅ |
| `LCDNumber` | digit 7-seg bake | S | set value, render segments ✅ |
| `Tour/Balloon tip` | Tooltip đã có | S | anchor→bubble, auto-dismiss ✅ |

### Wave B — Structural (mở app phức tạp) ✅ DONE 2026-09-24
| Item | Effort | Note |
|---|---|---|
| **Docking layout thật** (DockPanel split/float/tab) | M | `set_floating`/`hit_dock_tab`/`select_dock_tab`/`dock_tab_rect` + `make_native_dock_float` ✅ |
| **MDI area** (child windows cascade/tile) | M | `tile_horizontal` 2-child layout ✅ |
| **Ribbon / CommandBar** | M | `NativeRibbon` group tabs + large/small hit ✅ |
| **PropertyGrid** (2-col edit + category) | M | `NativePropertyGrid` collapse + begin/commit edit ✅ |
| **TreeView expand/collapse + multi-sel** | M | `NativeTreeView` sels_click plain/ctrl/shift + anchor + render_multi ✅ |
| **Wizard multi-page** | S | đã Wizard — verify linear/back/cancel ✅ (Wave A) |
| **Systray + context menu** | S | `NativeContextMenu` items+separators+activate ✅ |

### Wave C — Polish (đếm số + parity claim)
- Splitter horizontal/vertical, Accordion, Timeline, Breadcrumb, Rating đã có → test depth.
- **Acceptance chung:** `WIDGETS_BREADTH_OK` ≥ 80 distinct constructors +每个 render non-blank + hit-test; port thêm 1 Qt example mới (Tree view + Dock) 90%+ ✅ **`QTDOCK_OK` 31/31**.
- Còn: Thai/Deva box fallback (L2), ASCII bench 9.4ms đo lại.

**Không làm:** match 1000 class Qt — claim “đủ CRUD/form/desktop admin”, không claim breadth parity.

---

## L2. Wire HarfBuzz → draw path (thua shaping complex-script)

**Blocker đã identified:** `TkvUI.Text` ↔ `TkvUI.Bidi` vòng import; HB trả gid lạ chưa bake atlas.

### Design (3 bước)
1. **Leaf `TkvUI.HarfBuzz.tkv`** (không import Text/Bidi/Widgets — chỉ Viet + pinvoke + R2)
   - `hb_shape_to_clusters(text, font_blob, dir) -> list[rec {gid, ax, ay, ox, oy, cluster}]`
   - cache blob handle theo font path; free đúng nơi.
2. **Atlas lazy-bake:** `Text` import leaf HarfBuzz; khi draw gặp gid chưa có slot → raster TTF glyf@cmap→gid (parser已有) → `atlas_bake_gid(gid)`; fallback i18n baked nếu font thiếu.
3. **Draw path:** `draw_string_shaped()`:
   - ASCII fast path giữ nguyên (đo 9.4ms không regress).
   - script≠Latn → HB shape → visual order (Bidi đã có, import 1 chiều qua leaf) → blit advances per-cluster.
   - Thiếu dll → exact fallback cũ (baked forms) — skip-sạch 157/157.

### Acceptance
- `HBWIRE_OK`: Arabic “سلام” + Thai + Devanagari render pixel > 0, cluster count match HB selftest; **ASCII bench ≤ 9.4ms × 1.1** (không regress).
- Bidi 194/194 + Shaping 91/91 giữ xanh.
- NVDA/text copy: cluster string round-trip (optional).

**Effort:** ~2–3 ngày. **Không cần upstream.**

---

## L3. Cold-start 1.0 s → <0.3 s

**Root cause đo:** AV scan exe mới + CLR JIT (~19MB atlas+JIT heap) — warm 3 lần vẫn ~1.0s → lever là **NGEN/R2R**, không phải AV-cache.

### Plan
| Bước | Action | Owner |
|---|---|---|
| 1 | **R10.2 NGEN/AOT** — đẩy `UPSTREAM_REQUIREMENTS` (đã có mục): `tkvc --target exe` emit `.ni` hoăć docs `ngen.exe install app.exe` post-build | upstream tkvc |
| 2 | Repo-side: `tools/nGEN.ps1` opt-in (admin) — đo cold/warm trước/sau, ghi `BENCH.md` | local |
| 3 | Giảm working set: `reserve()` đã mở (R12) → áp atlas/scratch **R12 apply** (chưa dùng rộng) — cắt ~7MB doubling → RAM idle 11→~8–9MB | local |
| 4 | Lazy-load module: split umbrella — demo app chỉ import Text+Widgets (không Media/SQLite/H264) → startup giảm | local |

**Acceptance:** cold-spawn median 5 lần **< 500 ms** máy sạch / **< 300 ms** warm; ghi số mới vào COMPETITORS §8 (không claim nếu chưa đo lại).

---

## L4. GPU thật — stub → compute path

**Hiện tại:** abstraction + factory + probe `vkGetInstanceProcAddr` + **device ops stub 11/11**.

### Giai đoạn (không nhảy render pipeline)
1. **GpuCompute-1:** `create_buffer` + `dispatch(blur_kernel)` qua Vulkan compute — **R1 struct + R2 out-handle đã mở** → `vkCreateInstance`/`vkAllocateCommandBuffers` đọc handle thật.
2. **Blit/blur offload:** `Effects.half_res_blur` optional backend `gpu_blur` — bench vs CPU (mục tiêu ≥ 2× @1080p).
3. **Present path:** texture → `VkSurface` Win32 (đã có HWND) — 1 triangle clear màu.
4. **Text SDF trên GPU** (sau L2 wire HB) — optional.

**Acceptance:** `GPU_REAL_OK`: instance+device+buffer+dispatch+readback checksum khớp CPU blur trong tol; bench ghi `BENCH.md`.
**Blocker:** driver GPU thật trên máy dev (probe d3d11/vulkan đã thấy entry) — không cần upstream.

---

## L5. OS look native — theme match

| Task | Effort | Note |
|---|---|---|
| Detect accent color Windows (registry `DWM`/`AppsUseLightTheme`) | S | R6 registry đã mở |
| Dark/Light mode follow OS + refresh khi đổi (WM_SETTINGCHANGE) | M | Platform message pump已有 |
| 3-state hover/press/focus theo Visual Style metrics (`GetThemePartSize`) | M | pinvoke uxtheme |
| DPI-aware bitmap snapback (125/150%) | M | DPI token已有 → wire render |
| **Không** chase full msstyles engine — 28 widget sufficient | — | claim “modern flat + accent”, không claim “native Explorer” |

**Acceptance:** `THEME_OS_OK` — screenshot compare accent RGB == OS; dark toggle re-render; DPI 150% non-blurry text (measure).

---

## L6. Media breadth — Baseline → Main/High + playback

**Giữ OpenH264 Baseline** (đã 8/8 + RT 11/12). Thêm đường FFmpeg **LGPL shared** (không static GPL).

| Bước | Action | Effort |
|---|---|---|
| 1 | `tools/fetch_ffmpeg.ps1` — avcodec/avformat/avutil DLL LGPL builds (gyan.dev/shared hoặc BtbN) | S |
| 2 | Shim C# **mỏng** (mẫu H.264 shim已有): `FFmpegShim.DecodeFile(path) -> frames RGB + pts` — marshal AVFrame→R2 buffer | M |
| 3 | `.tkv` `TkvUI.H264Ex` (optional module): probe dll → decode MP4 Main sample bake | M |
| 4 | **Audio clock:** WASAPI/`waveOut` pinvoke — video PTS master | M |
| 5 | Player widget hợp nhất ClipPlayer + audio — seek smooth | M |

**Acceptance:** `FFMPEG_OK` 1 file Main-profile 1s decode > 0 frame RGB; verify SKIP khi thiếu dll. **Không claim** realtime 4K — claim “phổ profile mở, playback mượt @720p software”.

**License:** chỉ tải LGPL build; ghi `OPENH264.md` §FFmpeg.

---

## L7. A11y — mirror → NVDA đọc được

**Đã có:** tree model 38/38, HWND mirror 33/33, KitTest 16/16, `UiaClientsAreListening=1`.
**Thiếu:** NVDA 0 utterance widget (JSON chưa vào UIA tree thật).

### Đường chính: **C# COM shim** (đã chọn trong COMPILER_GAPS A4 — tkv không CCW)
```
TkvUI.A11yBridge (JSON tree) 
  → named-pipe/file outbox 
  → UiaHost.exe (C#): implements IRawElementProviderSimple/Value/Invoke 
  → UIAutomationCore 
  → NVDA
```
1. **UiaHost skeleton** (C# 40 dòng): factory lấy HWND mirror → wrap provider → `UiaHost` scan tree JSON 10Hz.
2. Wire events: invoke/toggle/value ← host → `.tkv` outbox (reverse channel).
3. `nvda_probe.ps1` mở: expect title+button+label utterances ≥ positive control WinForms.

**Acceptance:** `NVDA_OK` — Live demo: button “Play” đọc được role/label; KitTest giữ 16/16; headless CI = SKIP host (đúng pattern H.264).

**Effort:** ~3–4 ngày (shim C# + protocol). Không cần upstream (R1/R2/R3 đủ cho pipes/buffers).

---

## L8. Cross-platform Linux (R7)

| Bước | Prereq | Action |
|---|---|---|
| 1 | upstream **R7 `.so` linter** (đã ghi) | probe `libX11.so` pinvoke |
| 2 | X11: `XOpenWindow`/`XPutImage` map từ `PixelSurface`已有 abstraction | headless `Xvfb` CI |
| 3 | AT-SPI D-Bus (thay file-bridge) — AccessKit C binding (đường COMPETITORS §3) | sau X11 |
| 4 | Wayland — **hoãn** (không claim) | — |

**Acceptance:** `X11_OK` — Xvfb下 create window + present non-blurb + destroy; suite SKIP优雅 khi không có display.

---

## L9. CI matrix — static → build+run

**Hiện tại:** `ci.yml` chỉ purity/JSON/shell/python/docs link (tkvc machine-local).

| Bước | Action |
|---|---|
| 1 | Cache `tkvc.exe` + `ilasm` como artifact (commit dist binary **hoặc** release asset) — hoặc self-hosted runner Windows |
| 2 | Job `windows-full`: checkout → fetch HB/OpenH264 dll → `tools/verify.sh` → upload junit/log |
| 3 | Job `ubuntu-xvfb`: build `.so` (khi R7) + subset suite headless |
| 4 | Badge README: verify + CI green |

**Acceptance:** PR red khi verify fail; badge xanh 7 ngày.

---

## L10. Ecosystem (không tự claim thắng — tạo điều kiện)

| Task | Effort |
|---|---|
| Public GitHub + topics (`tkv`, `gui`, `vietnamese`) | S |
| nuget.org push `TokenVector.UI` + README badges download | S |
| 3 GIF: CRUD, RTL Arabic, Dock/Theme — README §Screenshots | S |
| `docs/TUTORIAL_CRUD.md` → video/asciinema | M |
| Respond 1 issue đầu tiên từ ngoài (nếu có) | — |

---

## Thứ tự đánh (ROI × phụ thuộc)

```
Tuần 1  ── L2 Wire HarfBuzz (text face, không blocker)
        ── L1 Wave A (10 widget S-effort) song song
        ── L3.3 R12 reserve apply (RAM immediate)

Tuần 2  ── L7 UiaHost C# shim → NVDA_OK (mở enterprise story)
        ── L1 Wave B Dock+Tree (app complexity)
        ── L9 CI windows-full (bảo vệ regression)

Tuần 3  ── L5 Theme OS match + accent
        ── L6 FFmpeg fetch + shim decode Main
        ── L4 GPU compute blur (nếu driver ok)

Tuần 4  ── L8 X11 headless (cần R7 upstream song song)
        ── L3 NGEN (khi upstream R10.2) + đo lại COMPETITORS
        ── L1 Wave C + port Qt Tree/Dock example
        ── L10 public + nuget + GIF
```

**Gate mỗi tuần:** `tools/verify.sh` vẫn **51+ / 0 FAIL**; thêm case mới vào verify.sh cùng acceptance; cập nhật `COMPETITORS.md` §2/§8 **chỉ khi đo thật**.

---

## Acceptance tổng (Definition of Done san bằng)

| L | DoD đo được |
|---|---|
| L1 | ≥80 widget constructors + `WIDGETS_BREADTH_OK`; Qt Tree/Dock port ≥90% |
| L2 | `HBWIRE_OK` complex render; ASCII bench không regress >10% |
| L3 | cold-start median <500ms sạch / <300ms warm; ghi số mới |
| L4 | `GPU_REAL_OK` blur checksum + ≥2× CPU |
| L5 | `THEME_OS_OK` accent+dark+DPI |
| L6 | `FFMPEG_OK` Main-profile frames; SKIP sạch |
| L7 | `NVDA_OK` button+label utterance; KitTest 16/16 |
| L8 | `X11_OK` Xvfb present; suite SKIP khi thiếu display |
| L9 | CI full green 7 ngày; PR gate |
| L10 | public repo + nuget + 3 GIF live |

---

## Ghi chú chiến lược (trung thực)

- **Thắng niche giữ nguyên:** binary size, memory, text ASCII, SQL/PDF built-in, clipboard Win32, Vietnamese-first, H.264 Baseline nhỏ.
- **San bằng优先:** L2 text complex (mặt tiền) → L7 a11y (mở user) → L1 widgets (độ phủ) → L3 startup (perception).
- **Không claim** “đánh bại Qt mọi mặt” — claim “desktop CRUD/admin/Vietnamese app: nhỏ hơn, nhanh hơn, built-in persistence/print, shaping đủ dùng”.
- **Upstream song song:** R7 `.so`, R10 NGEN, R1 struct lồng — gửi `COMPILER_FIX_LIST` khi cần, không block local plan.
