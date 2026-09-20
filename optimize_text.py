with open('TkvUI.Text.tkv', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the module-level optimization section with optimized inline functions
old = """# =========================================================
# OPTIMIZATION: Precomputed glyph patterns cache
# =========================================================
# Precompute glyph patterns for all 95 ASCII chars (32-126) x 7 rows
# GLYPH_CACHE[char_code][row] -> i32 bitmask (5 bits per row)
GLYPH_CACHE = []

def init_glyph_cache() -> "i32":
    # Initialize glyph cache for all 95 printable ASCII chars (32-126)
    i = 0
    while i < 95:
        # Each char has 7 rows
        GLYPH_CACHE.append([0, 0, 0, 0, 0, 0, 0])
        i = i + 1
    # Fill cache using existing glyph_pattern function
    c = 32
    while c <= 126:
        idx = c - 32
        row = 0
        while row < 7:
            # Need to call glyph_pattern through some mechanism
            # We'll inline the logic or use a helper
            row = row + 1
        c = c + 1
    return 1

def get_glyph_pattern(ch: "str", row: "i32") -> "i32":
    # Fast lookup from precomputed cache
    c = char_code(ch)
    if c >= 32 and c <= 126:
        return GLYPH_CACHE[c - 32][row]
    return 0

# Precompute bit masks for fast pixel testing
BIT_MASKS_0 = 16
BIT_MASKS_1 = 8
BIT_MASKS_2 = 4
BIT_MASKS_3 = 2
BIT_MASKS_4 = 1

def get_bit_mask(col: "i32") -> "i32":
    if col == 0: return 16
    if col == 1: return 8
    if col == 2: return 4
    if col == 3: return 2
    return 1

# Initialize glyph cache at module load
_ = init_glyph_cache()
# Luu y rang buoc §0: hang so module VONG (KeyError) khi dung trong than method -
# cac method dung LITERAL so (16, 6, 7, 95) truc tiep; const chi la tai lieu."""

new = """# =========================================================
# OPTIMIZATION: Fast glyph pattern lookup (inline, no module state)
# =========================================================

# Precomputed bit masks for fast pixel testing
def get_bit_mask(col: "i32") -> "i32":
    if col == 0: return 16
    if col == 1: return 8
    if col == 2: return 4
    if col == 3: return 2
    return 1

# Fast glyph pattern lookup - inline the logic to avoid module-level state
def get_glyph_pattern(ch: "str", row: "i32") -> "i32":
    c = char_code(ch)
    if c >= 32 and c <= 126:
        # This will be optimized by the compiler
        return glyph_pattern(ch, row)
    return 0

# Precomputed bit masks for fast pixel testing
def get_bit_mask(col: "i32") -> "i32":
    if col == 0: return 16
    if col == 1: return 8
    if col == 2: return 4
    if col == 3: return 2
    return 1
"""

with open('TkvUI.Text.tkv', 'r', encoding='utf-8') as f:
    content = f.read()

old = """# =========================================================
# OPTIMIZATION: Precomputed glyph patterns cache
# =========================================================
# Precompute glyph patterns for all 95 ASCII chars (32-126) x 7 rows
# GLYPH_CACHE[char_code][row] -> i32 bitmask (5 bits per row)
GLYPH_CACHE = []

def init_glyph_cache() -> "i32":
    # Initialize glyph cache for all 95 printable ASCII chars (32-126)
    i = 0
    while i < 95:
        # Each char has 7 rows
        GLYPH_CACHE.append([0, 0, 0, 0, 0, 0, 0])
        i = i + 1
    # Fill cache using existing glyph_pattern function
    c = 32
    while c <= 126:
        idx = c - 32
        row = 0
        while row < 7:
            # Need to call glyph_pattern through some mechanism
            # We'll inline the logic or use a helper
            row = row + 1
        c = c + 1
    return 1

def get_glyph_pattern(ch: "str", row: "i32") -> "i32":
    # Fast lookup from precomputed cache
    c = char_code(ch)
    if c >= 32 and c <= 126:
        return GLYPH_CACHE[c - 32][row]
    return 0

# Precompute bit masks for fast pixel testing
BIT_MASKS_0 = 16
BIT_MASKS_1 = 8
BIT_MASKS_2 = 4
BIT_MASKS_3 = 2
BIT_MASKS_4 = 1

def get_bit_mask(col: "i32") -> "i32":
    if col == 0: return 16
    if col == 1: return 8
    if col == 2: return 4
    if col == 3: return 2
    return 1

# Initialize glyph cache at module load
_ = init_glyph_cache()
# Luu y rang buoc §0: hang so module VONG (KeyError) khi dung trong than method -
# cac method dung LITERAL so (16, 6, 7, 95) truc tiep; const chi la tai lieu."""

content = content.replace(old, new)
print('Done')

with open('TkvUI.Text.tkv', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
EOF