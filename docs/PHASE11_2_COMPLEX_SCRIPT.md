# Phase 11.2: Complex Script Shaping (Indic/Thai) - Research & Implementation Plan

> **Mục tiêu:** Hỗ trợ shaping đầy đủ cho các script phức tạp: Devanagari (Hindi/Marathi), Bengali, Tamil, Telugu, Thai, v.v.
> **Trạng thái hiện tại:** Cơ sở HarfBuzz bindings đã có, nhưng shaping engine đầy đủ chưa hoàn thiện.

---

## 1. Trạng thái hiện tại (Current State)

### ✅ Đã có sẵn (Ready)
- **HarfBuzz FFI bindings** (`TkvUI.Bidi.tkv` lines 10-35): `hb_shape`, `hb_buffer_*`, `hb_font_*`, `hb_face_*`, `hb_blob_*` 
- **Script detection** (`hb_script_for_text`): Detect Arabic, Hebrew, Devanagari, Bengali, Thai, etc.
- **Script constants**: HB_SCRIPT_DEVANAGARI=6, HB_SCRIPT_BENGALI=7, HB_SCRIPT_THAI=16, etc.
- **Font fallback chain**: ASCII → Viet 134 glyph → i18n baked (Hebrew/Arabic/CJK) → Box fallback
- **Bidi support** (UAX #9): RTL/RTL detection, visual reordering
- **Font fallback chain**: ASCII → Viet 134 glyph → i18n baked → Box fallback
- **Glyph drawing**: `atlas_blit_glyph` cho i18n baked fonts
- **HarfBuzz FFI**: `hb_shape`, `hb_buffer_*`, `hb_font_*`, `hb_face_*`, `hb_blob_*`

### ❌ Chưa có / Cần implement (Gaps)

| Component | Status | Mô tả |
|---|---|---|
| **GSUB/GPOS processing** | ❌ | HarfBuzz `hb_shape` được gọi nhưng GSUB/GPOS tables chưa được xử lý đúng cho complex scripts |
| **Indic conjunct formation** | ❌ | Devanagari/Bengali/Tamil conjuncts (half-forms, virama, reph, etc.) |
| **Thai reordering** | ❌ | Pre-base vowels (เ, แ, โ, ใ, ไ), tone marks (่, ้, ๊, ๋), tone marks positioning |
| **Cluster boundaries** | ❌ | Cluster boundaries cho cursor movement/selection |
| **GSUB/GPOS table processing** | ❌ | Chỉ gọi `hb_shape` mà không xử lý lookup tables |
| **Thai tone marks positioning** | ❌ | Tone marks (่, ้, ๊, ๋) positioning above consonants |
| **Thai vowel reordering** | ❌ | Pre-base vowels (เ, แ, โ, ใ, ไ) reordering visual |
| **Indic conjunct formation** | ❌ | Virama (्), half-forms, reph, rakar, vattu, etc. |
| **Cluster boundaries** | ❌ | Grapheme cluster boundaries cho cursor/selection |
| **GSUB/GPOS table parsing** | ❌ | Chưa parse GSUB/GPOS tables từ font |

---

## 2. Kiến trúc đề xuất (Proposed Architecture)

### 2.1 Module Structure
```
TkvUI.TextShaping/
├── TkvUI.Shaping/
│   ├── ShapingEngine.tkv        # Main shaping engine
│   ├── HarfBuzzBridge.tkv       # HarfBuzz FFI wrapper
│   ├── IndicShaping.tkv         # Indic-specific logic
│   ├── ThaiShaping.tkv          # Thai-specific logic
│   ├── ClusterBoundary.tkv      # Grapheme cluster boundaries
│   ├── GSUBGPOS.tkv             # GSUB/GPOS table processing
│   ├── ShapingPlan.tkv          # Shaping plan cache
│   └── GlyphPositioning.tkv     # GPOS positioning
```

### 2.2 Data Structures

```tkv
# Shaped glyph info
class ShapedGlyph:
    glyph_id: "i32"
    cluster: "i32"           # Original character index
    x_advance: "i32"         # X advance (26.6 fixed point)
    y_advance: "i32"         # Y advance
    x_offset: "i32"          # X offset
    y_offset: "i32"          # Y offset
    cluster_start: "i32"     # Start char index
    cluster_end: "i32"       # End char index
    is_ligature: "i32"       # 1 if ligature

# Cluster info for cursor/selection
class TextCluster:
    start: "i32"             # Start char index
    end: "i32"               # End char index (exclusive)
    glyph_start: "i32"       # First glyph index
    glyph_count: "i32"       # Number of glyphs
    is_rtl: "i32"            # RTL run
    script: "i32"            # Script type
```

---

## 3. Implementation Plan (Phased)

### Phase 11.2.1: HarfBuzz Integration Foundation (Week 1-2)
**Mục tiêu:** Kết nối đầy đủ HarfBuzz shaping pipeline

| Task | Mô tả | Deliverable |
|---|---|---|
| 1.1 | `hb_shape_full` hoàn thiện | `hb_shape_full` trả về `HbGlyphInfo[]` + `HbGlyphPosition[]` đầy đủ |
| 1.2 | `hb_shape_plan` caching | Cache `HbShapePlan` theo (font, script, direction, language) |
| 1.3 | Font fallback integration | Tích hợp fallback chain vào shaping pipeline |
| 1.3 | Glyph info/position extraction | `hb_buffer_get_glyph_infos/positions` → `ShapedGlyph[]` |
| 1.4 | Cluster mapping | Map glyph→char cluster boundaries |

**Test:** `hb_shape_full("नमस्ते", devanagari_font) → glyphs + clusters correct`

---

### Phase 11.2.2: Indic Shaping Engine (Week 3-4)
**Mục tiêu:** Hỗ trợ Devanagari, Bengali, Tamil, Telugu, etc.

| Task | Mô tả | Deliverable |
|---|---|---|
| 2.1 | Indic script detection | `detect_indic_script(text) -> script_id` |
| 2.2 | Virama handling | Virama (्) processing, half-form generation |
| 2.3 | Reph/Rakar formation | Reph (र्), rakar, vattu formation |
| 2.4 | Half-form generation | Half-form lookup (GSUB lookup type 1/2) |
| 2.5 | Conjunct formation | Consonant conjuncts (kṣ, ज्ञ, त्र, श्र, etc.) |
| 2.5 | Matra positioning | Dependent vowel (matra) positioning |
| 2.6 | Reph/Rakar/Vattu | Reph (र्), Rakar (र्), Vattu ( đáy ) |
| 2.6 | Nukta handling | Nukta (़) positioning |

**Test cases:**
- `हिंदी` → हि + ं + दी (proper conjuncts)
- `தமிழ்` → த + மி + ழ் (Tamil shaping)
- `বাংলা` → ব + া + ং + ল + া (Bengali)

---

### Phase 11.2.3: Thai Shaping Engine (Week 5-6)
**Mục tiêu:** Hỗ trợ đầy đủ Thai script

| Task | Mô tả | Deliverable |
|---|---|---|
| 3.1 | Thai vowel reordering | Pre-base vowels (เ, แ, โ, ใ, ไ) → visual reorder |
| 3.2 | Tone marks positioning | Tone marks (่, ้, ๊, ๋) positioning above consonants |
| 3.3 | Thai tone marks stacking | Multiple tone marks stacking |
| 3.3 | Thai cluster boundaries | Cluster boundaries cho cursor/selection |
| 3.4 | Thai tone mark stacking | Multiple tone marks (่ ้ ๊ ๋) stacking |
| 3.5 | Thai tone mark stacking | Above/below vowel positioning |

**Test cases:**
- `สวัสดี` → ส + ว + ั + ส + ด + ี (proper reordering)
- `ไทย` → ท + ั + ย (proper vowel positioning)
- `โทรศัพท์` → โ + ต + ร + ะ + ส + ั + พ + ฎ (complex)

---

### Phase 11.2.4: GSUB/GPOS Processing (Week 7-8)
**Mục tiêu:** Full GSUB/GPOS table processing

| Task | Mô tả | Deliverable |
|---|---|---|
| 4.1 | GSUB lookup processing | Single/alternate/multiple/ligature/contextual substitution |
| 4.2 | GPOS positioning | Pair adjustment, cursive attachment, mark-to-base, mark-to-mark |
| 4.3 | Lookup processing | Single/multiple/alternate/ligature/contextual/chaining |
| 4.3 | Contextual substitution | Contextual chaining (GSUB type 5/6/7/8) |
| 4.4 | Mark-to-base/mark-to-mark | Anchor-based positioning (GPOS type 4/5) |
| 4.5 | Cursive attachment | Cursive attachment (GPOS type 3) |

---

## 4. Architecture Integration

### 3.1 Integration Points

```tkv
# TextShaping.tkv - Main entry point
def shape_text(text: "str", font: "Font", direction: "i32", script: "i32", language: "str") -> "ShapedText":
    """Main shaping entry point"""
    # 1. Script detection
    script = detect_script(text)
    
    # 2. Choose shaping engine
    if is_indic_script(script):
        return shape_indic(text, font, direction, language)
    elif script == HB_SCRIPT_THAI:
        return shape_thai(text, font, direction, language)
    else:
        return shape_generic(text, font, direction, script, language)

# Cluster boundary API
def get_cluster_boundaries(shaped: "ShapedText") -> "list[TextCluster]":
    """Return cluster boundaries for cursor/selection"""
```

### 3.2 Integration with Existing Pipeline

```
Current: draw_string() → FontFallback.draw_string() → atlas_blit_glyph()
          ↓
New:     shape_text() → ShapedText → FontFallback.draw_shaped() → atlas_blit_glyph()
```

---

## 4. Implementation Priority & Timeline

### Sprint 1 (Week 1-2): Foundation
- [ ] `hb_shape_full` complete implementation
- [ ] Font fallback integration
- [ ] Cluster mapping
- [ ] Basic test: `hb_shape_full("नमस्ते", devanagari_font)` → correct glyphs

### Sprint 2 (Week 3-4): Indic Shaping
- [ ] Indic script detection
- [ ] Virama/half-form processing
- [ ] Reph/Rakar formation
- [ ] Conjunct formation test: `हिंदी`, `தமிழ்`, `বাংলা`

### Sprint 3 (Week 5-6): Thai
- [ ] Thai vowel reordering
- [ ] Tone marks positioning
- [ ] Thai cluster boundaries

### Sprint 4 (Week 7-8): GSUB/GPOS
- [ ] GSUB lookup processing
- [ ] GPOS positioning
- [ ] Contextual substitution
- [ ] Mark-to-base/mark-to-mark positioning

---

## 5. Testing Strategy

### Test Cases (Minimum)

| Script | Test String | Expected |
|---|---|---|
| Devanagari | `नमस्ते` | न + म + स् + ते |
| Devanagari | `हिंदी` | हि + ं + दी |
| Bengali | `বাংলা` | ব + া + ং + ল + া |
| Tamil | `தமிழ்` | த + மி + ழ் |
| Telugu | `తెలుగు` | త + ె + లు + గు |
| Thai | `สวัสดี` | ส + ว + ั + ส + ด + ี |
| Thai | `ไทย` | ท + ั + ย |
| Arabic | `مرحبا` | م + ر + ح + ب + ا |

### Cluster Boundary Tests
```tkv
# Cursor movement tests
get_cluster_boundaries("नमस्ते") → [{0,2},{2,4},{4,5},{5,6}]  # नम, स्, ते
get_cluster_boundaries("สวัสดี") → [{0,2},{2,4},{4,6}]  # สว, ัส, ดี
```

---

## 4. Implementation Files Structure

```
TkvUI.Shaping/
├── ShapingEngine.tkv        # Main entry: shape_text()
├── HarfBuzzBridge.tkv       # hb_* wrappers + hb_shape_full
├── IndicShaping.tkv         # Indic-specific logic
├── ThaiShaping.tkv          # Thai-specific logic  
├── ClusterBoundary.tkv      # Cluster boundary detection
├── GSUBGPOS.tkv             # GSUB/GPOS table processing
├── ShapingPlan.tkv          # Shaping plan cache
├── GlyphPositioning.tkv     # GPOS positioning
└── ClusterBoundary.tkv      # Cluster boundary detection
```

---

## 4. Testing & Validation

### Unit Tests (per sprint)
```tkv
def test_indic_shaping() -> "i32":
    # Devanagari
    assert_equal(shape("नमस्ते", devanagari_font), expected_glyphs)
    assert_equal(shape("हिंदी", hindi_font), expected_glyphs)
    assert_equal(shape("तमिऴ்", tamil_font), expected_glyphs)
    
    # Thai
    assert_equal(shape("สวัสดี", thai_font), expected_glyphs)
    assert_equal(shape("ไทย", thai_font), expected_glyphs)
    
    # Cluster boundaries
    assert_cluster_boundaries("नमस्ते", [{0,2},{2,4},{4,5},{5,6}])
    assert_cluster_boundaries("สวัสดี", [{0,2},{2,4},{4,6}])
```

---

## 5. Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| HarfBuzz DLL not found | High | High | Graceful fallback to basic shaping |
| Font missing GSUB/GPOS | Medium | Medium | Fallback to basic positioning |
| Complex conjuncts missing | Medium | High | Fallback to virama + base glyphs |
| Thai reordering bugs | Medium | High | Extensive test cases |
| Performance on long text | Low | Medium | Caching shaping plans |

---

## 6. Success Criteria (Phase 11.2 Complete)

- [ ] `hb_shape_full` returns correct glyphs + positions for Indic/Thai
- [ ] Cluster boundaries correct for cursor movement
- [ ] Test cases pass: Devanagari, Bengali, Tamil, Thai
- [ ] Cluster boundaries correct for cursor movement
- [ ] Performance: < 10ms for 1000 chars shaping
- [ ] Fallback works when HarfBuzz unavailable

---

## 6. Next Steps

1. **Week 1**: Implement `hb_shape_full` + cluster mapping
2. **Week 2**: Test with Devanagari/Bengali/Tamil fonts
3. **Week 3**: Thai shaping (reordering + tone marks)
4. **Week 4**: GSUB/GPOS processing + cluster boundaries
5. **Integration**: Replace `draw_string` with `shape_text` in render pipeline

---

*Đã cập nhật: 2026-09-18 | Phiên bản 1.0*
*Phụ thuộc: TkvUI.Bidi.tkv (HarfBuzz FFI), TkvUI.Text (font fallback), TkvUI.I18nData (baked glyphs)*