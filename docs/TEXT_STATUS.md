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

## 11.2 Complex Script Shaping (Indic/Thai/Arabic full) — 🔴 CHƯA LÀM

**Hiện trạng:**
- Bidi UAX#9 + visual reorder: DONE (`TkvUI.Bidi.tkv`, 112/112 PASS)
- HarfBuzz FFI stub: có (`TkvUI.Bidi.tkv` — `hb_*` pinvoke)
- **Shaping engine chưa có**: Indic (Devanagari/Bengali/etc), Thai, Arabic full contextual forms

**Blocker:** Cần shaping engine (HarfBuzz đầy đủ hoặc tự viết shaping tables)

**Workaround hiện tại:** Arabic/Hebrew dùng glyph baked sẵn (`i18n_baked`), không shaping runtime.

**Mục tiêu:** `text_atlas_draw_i18n` hỗ trợ shaping đúng cho Indic/Thai/Arabic full.

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