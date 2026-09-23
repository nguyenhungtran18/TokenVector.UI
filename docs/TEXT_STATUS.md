# TkvUI Text Shaping & Font Status — Phase 11

> Cập nhật: 2026-09-18. Xem `TOKENVECTOR_PLAN_P2.md` Phase 11.

---

## 11.1 Font Fallback Chain — ✅ DONE (26/26 PASS)

**File:** `TkvUI.FontFallback.tkv` (317 lines)

**Chain:** ASCII (Text 5x7) → Việt 134 glyph → i18n baked (Hebrew/Arabic/CJK) → Box fallback

**Features:**
- Monospace 6px/sequence (đồng nhất `measure_string`)
- `fb_classify()`: phân loại sequence → ASCII/Viet/i18n/missing
- `fb_resolve()`: gom run cùng font để render batch
- Backend: `draw_string` (ASCII), `vi_draw_bits` (Viet), `atlas_blit_glyph` (i18n), `vi_draw_bits` box fallback

**Test:** `FALLBACK_OK` 26/26 (oracle consistency, mixed string resolve, draw pixel > 0)

**Thiếu:** Emoji, color font, variable font, font linking OS-level

---

## 11.2 Complex Script Shaping (Indic/Thai/Arabic full) — 🟡 CORE ĐÃ打通, CÒN WIRE

**Hiện trạng:**
- Bidi UAX#9 + visual reorder: DONE (`TkvUI.Bidi.tkv`, **194/194 PASS**)
- **HarfBuzz 14.5 thật: ĐÃ打通 (2026-09-23)** — pinvoke `hb_*` + `hb_shape_full`/`hb_shape_text`, bake Arial exact (gid/adv/cluster khớp ctypes, Ả Rập RTL joining), `tools/fetch_harfbuzz.ps1` (MIT), skip-sạch 157/157 khi thiếu dll
- **Wire draw path: ĐÃ XONG (L2, 2026-09-23)** — leaf `TkvUI.HarfBuzz` phá vòng import Text↔Bidi; `text_atlas_draw_shaped` + `atlas_find_or_bake_gid` lazy-bake; `hbwire_selftest` **14/14 `HBWIRE_OK`** (Arabic pixel>0 + cluster match, Thai/Deva box pixel>0, ASCII fast-path giữ nguyên)

**Workaround cũ (khi thiếu dll):** Arabic/Hebrew dạng glyph baked sãn (`i18n_baked`), không shaping runtime — nay fallback qua `text_draw_fallback` khi `hb_lib_present()==0`.

**Mục tiêu:** `text_atlas_draw_shaped` hỗ trợ shaping đúng cho Indic/Thai/Arabic full khi có dll — **đã wire**; Arabic/Hebrew/Han có font embedded → shape thật; Thai/Deva chưa có embedded font → box fallback (cần thêm subset font để render glyph thật).

---

## 11.3 TTF Subset + Embed PDF — 🔴 BLOCKED (UPSTREAM)

**File:** `TkvUI.Printing.tkv` — `pdf_font_embed()` stub trả 0

**Blocker:** Cần byte array support trong tkvc (compiler gap: không có file I/O, không byte array literal, không marshal struct ra file).

**Workaround:** PDF dùng Base14 fonts (Helvetica/Times/Courier) — không embed TTF.

**Unblock cần:** tkvc hỗ trợ `byte[]` / `Span<byte>` + `System.IO.File.WriteAllBytes` pinvoke.

---

## 11.4 Fuzz Shaping — 🟡 PARTIAL DONE

**File:** `TkvUI.Fuzz.tkv` — `FUZZ_OK` (26/26 PASS)

**Đã có:**
- 500 ops fuzz: rect/text/line/widget random (offscreen, radius lớn, chuỗi rỗng, màu transparent)
- Model fuzz: append/remove/cell get ngẫu nhiên 60 ops
- Rasterizer: rect/text/line/widget adversarial (tọa độ âm, radius lớn, chuỗi rỗng, màu transparent)

**Còn thiếu:**
- Corpus fuzzing shaping-specific (Indic/Thai/Arabic sequences)
- Assert crash-free trên sequence invalid UTF-8, surrogate pairs, grapheme clusters
- Property-based test: `fb_resolve` round-trip, `fb_measure` invariant

---

## Tóm tắt Phase 11

| Task | Status | File | Test |
|---|---|---|---|
| 11.1 Font Fallback | ✅ DONE | `TkvUI.FontFallback.tkv` | `FALLBACK_OK` 26/26 |
| 11.2 Complex Script | 🔴 CHƯA LÀM | `TkvUI.Bidi.tkv` + `TkvUI.FontFallback.tkv` | — |
| 11.3 TTF Embed PDF | 🔴 BLOCKED (upstream) | `TkvUI.Printing.tkv` | — |
| 11.4 Fuzz Shaping | 🟡 PARTIAL | `TkvUI.Fuzz.tkv` | `FUZZ_OK` 26/26 |

**Tiếp theo:** 11.1 mở rộng (emoji, color font) → 11.4 fuzz shaping corpus mở rộng → 11.2 research shaping engine.