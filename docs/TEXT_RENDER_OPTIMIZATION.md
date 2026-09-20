# Text Rendering Optimization Plan for TokenVector.UI

> **Goal**: Giảm text render từ 21.8ms → <10ms (cho 400×54 chars = 108,000 chars)
> **Current**: 21.8ms (21.8ms/block) | PyQt6: 14.2ms | Gap: +53%
> **Target**: ≤10ms (tức ≤10μs/block, ≤0.1μs/char)

---

## Root Cause Analysis

### Current Bottlenecks (TkvUI.Text.draw_string)

```tkv
def draw_string(...):
    while idx < n:
        ch = text[idx]
        code = char_code(ch)
        if code >= 0:           # ASCII fast path
            for row in range(7):      # 7 rows
                mask = glyph_pattern(ch, row)
                for col in range(5):  # 5 cols
                    # Bit test bằng chia/trừ thay vì bitwise
                    p = 16
                    if col == 1: p = 8
                    if col == 2: p = 4
                    if col == 3: p = 2
                    if col == 4: p = 1
                    on = 0
                    if mask >= p:     # Division loop thay vì bitwise
                        tmp = mask
                        if tmp >= 16:
                            if p == 16: on = 1
                            tmp = tmp - 16
                        if tmp >= 8:  # 4 levels of division
                            ...
                        if tmp >= 1:
                            ...
                        if on == 1:
                            for sy in range(sc):  # scale loops
                                for sx in range(sc):
                                    surface_blend_pixel()  # CALL PER PIXEL
```

**Problems:**
1. **No glyph cache** - Mỗi ký tự vẽ lại từ đầu
2. **Bitwise bằng division** - `mask >= p` + subtraction loops thay vì `mask & bit`
3. **Per-pixel blending** - `surface_blend_pixel()` gọi cho MỖI pixel (7×5×scale²)
4. **No glyph atlas** - Không cache glyph đã render
5. **Character-by-character** - Không batch glyphs

---

## Optimization Roadmap

### Phase 1: Quick Wins (1-2 days) - **Target: 21.8ms → 12ms**

| # | Optimization | Effort | Expected Gain |
|---|---|---|---|
| 1 | **Bitwise ops thay division loops** | 2h | 2-3x faster bit test |
| 2 | **Precompute glyph bitmasks** | 4h | Remove per-char pattern lookup |
| 3 | **Inline surface_blend_pixel** | 2h | Reduce call overhead |

**Expected**: 21.8ms → ~12ms (45% improvement)

---

### Phase 1: Glyph Bitmap Cache (1-2 weeks) - **Target: 12ms → 4ms**

```tkv
# Glyph cache structure
class GlyphCache:
    cache: "dict[str, GlyphBitmap]"  # key: (char, scale, color) -> GlyphBitmap
    atlas: "GlyphAtlas"              # Texture atlas for GPU/blit

class GlyphBitmap:
    width: "i32"
    height: "i32"
    pixels: "list[i64]"  # ARGB32 pixels
    advance: "i32"       # Advance width

# Glyph Atlas - pack multiple glyphs into texture atlas
class GlyphAtlas:
    width: "i32"
    height: "i32"
    pixels: "list[i64]"  # ARGB32
    regions: "dict[str, Rect]"  # char -> (x, y, w, h)
```

**Implementation Steps:**
1. `GlyphCache.get_or_render(char, scale, color) -> GlyphBitmap`
2. `GlyphAtlas.allocate(char, bitmap) -> Rect`
3. `draw_string` → `fb_resolve` → batch blit glyphs via `atlas_blit` (memcpy blocks)

**Expected**: 21.8ms → **4ms** (5-6x speedup)

---

### Phase 2: Text Shaping Cache (Week 3-4)

```tkv
class ShapedTextCache:
    cache: "dict[str, ShapedText]"  # key: (text, font, scale, tracking) -> ShapedText

class ShapedText:
    glyphs: "list[ShapedGlyph]"  # Pre-positioned glyphs
    width: "f64"
    height: "f64"
    clusters: "list[Cluster]"    # For cursor/selection

class ShapedGlyph:
    glyph_id: "i32"
    x: "f64"
    y: "f64"
    advance: "f64"
    cluster: "i32"  # cluster index for cursor
```

**Benefits:**
- Reuse shaped text for static UI labels
- Cursor/selection via cluster boundaries
- Eliminate per-frame shaping

---

### Phase 3: GPU/Blit Acceleration (Optional)

```tkv
# GPU path (future)
def draw_glyphs_gpu(atlas: "Texture", glyphs: "list[PositionedGlyph]"):
    # Single draw call for all glyphs
    gpu_draw_instanced(atlas.texture, glyphs)

# CPU fallback (current)
def draw_string_cpu(...):
    # Batch blit from glyph atlas
    for run in runs:
        atlas_blit_batch(atlas, glyphs_in_run)
```

---

## Implementation Priority

| Sprint | Focus | Deliverable | Target |
|---|---|---|---|
| **Sprint 1** (Week 1-2) | Bitmap glyph cache + atlas | `GlyphCache`, `GlyphAtlas`, `fb_draw_string` rewrite | 21.8ms → 4ms |
| **Sprint 2** | Precomputed glyph bitmaps | Pre-bake ASCII + Việt + i18n glyphs at common scales | 4ms → 2ms |
| **Sprint 3** | ShapedText cache | `ShapedTextCache` cho static text | Static text ~0ms |
| **Sprint 4** | Batch blit / Atlas blit | `atlas_blit_batch` thay `surface_blend_pixel` loop | 21ms → **<1ms** |

---

## Implementation Checklist

### Sprint 1: Glyph Cache (Week 1)
- [ ] `GlyphCache` class với LRU eviction
- [ ] `GlyphAtlas` - pack glyphs into power-of-2 texture
- [ ] `fb_draw_string` → resolve runs → `atlas_blit_glyph` batch
- [ ] Benchmark: `bench_text_block` target <5ms

### Sprint 2: Pre-baked Glyphs
- [ ] Pre-bake ASCII (95), Việt (134), Latin-1 Supplement
- [ ] Pre-bake i18n baked (Hebrew/Arabic/CJK) từ `TkvUI.I18nData`
- [ ] Scale variants: 1x, 1.5x, 2x, 3x

### Sprint 3: Shaping Cache
- [ ] `ShapedTextCache` với key `(text, font, scale, tracking)`
- [ ] LRU eviction (max 1000 entries)
- [ ] Cluster boundaries cho cursor/selection

### Sprint 4: Batch Blit
- [ ] `atlas_blit_batch(atlas, glyphs[])` - memcpy blocks
- [ ] `draw_string` → resolve → batch blit
- [ ] Benchmark target: **<1ms** for 400×54 chars

---

## Quick Wins (Do First - 1 Day)

```tkv
# 1. Bitwise thay division loop (TkvUI.Text.tkv ~line 1800)
# TRƯỚC:
if mask >= p:
    tmp = mask
    if tmp >= 16: ...
    if tmp >= 8: ...
# SAU:
on = int(mask & p != 0)

# 2. Precompute bit masks
BIT_MASKS = [1, 2, 4, 8, 16]
on = 1 if (mask & BIT_MASKS[col]) != 0 else 0

# 3. Precompute glyph bitmasks
GLYPH_MASKS[char][row] = uint32  # 5-bit per row
# Thay vì glyph_pattern(ch, row) call mỗi lần
```

**Estimated gain**: 21.8ms → **8ms** (2.7x) với 2-3 ngày effort.

---

## Benchmark Targets

| Metric | Current | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 |
|---|---|---|---|---|---|
| **400×54 chars** | 21.8ms | 8ms | 4ms | 2ms | **<1ms** |
| **Per char** | 0.20 μs | 0.07 μs | 0.04 μs | 0.02 μs | **<0.01 μs** |
| **vs PyQt6** | 21.8ms | 8ms | 4ms | 2ms | **<1ms** (thắng PyQt) |

---

## Files to Modify

| File | Changes |
|---|---|
| `TkvUI.Text.tkv` | `draw_string` rewrite, bitwise ops |
| `TkvUI.Text.tkv` | `glyph_pattern` → precomputed table |
| `TkvUI.FontFallback.tkv` | Add `GlyphCache`, `GlyphAtlas` |
| `TkvUI.Text.tkv` | `draw_string` → cache + atlas blit |
| `TkvUI.Graphics.tkv` | `atlas_blit_batch` for batch blit |

---

## Test Plan

```bash
# Baseline
$ bash tools/bench_all.sh

# Sprint 1 target
$ ./build/bench_text.exe
# Target: <5ms for 400×54 chars

# Sprint 2
$ ./build/bench_text.exe  # With pre-baked glyphs

# Sprint 4
$ ./build/bench_text.exe
# Target: <1ms for 400×54 chars
```

---

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| Font fallback complexity | Keep fallback chain: ASCII→Viet→i18n→Box |
| Memory usage | LRU cache max 500 glyphs, atlas 1024×1024 |
| Color font (CBDT/COLR) | Defer to Phase 2, fallback to outline |
| RTL/Bidi | Cluster boundaries preserved in `ShapedText` |
| Emoji | Defer to Phase 2 (color font support) |

---

## Definition of Done

- [ ] `bench_text_block` < 5ms (400×54 chars)
- [ ] `bench_text_block` < 1ms (with pre-baked glyphs)
- [ ] `bench_text_block` < 1ms for static cached text
- [ ] No visual regression vs current output
- [ ] Memory < 50MB for glyph cache
- [ ] RTL/Bidi/Complex script still works