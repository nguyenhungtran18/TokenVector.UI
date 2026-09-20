# TkvUI Development Plan: Turn Weaknesses → Strengths

> Goal: Make every "Don't Choose" criterion become a "Choose" reason.

---

## Trạng thái hiện tại (đối chiếu kế hoạch ↔ code, cập nhật 2026-09-18, v2.3.2 — số liệu verify bằng build+run thật)

| Hạng mục trong plan | Trạng thái | Ở đâu |
|---|---|---|
| Phase 1 — HarfBuzz shaping, font atlas, fallback chain, bidi/RTL, IME | **Cơ bản xong** — UAX#9 port (Bidi 112) + UTF-8 split + fallback chain `font_family_resolve` + baked glyph thật Hebrew/Arabic/CJK (Text 160) + IME Win32 (dispatcher/TextInput/demo); còn: HarfBuzz thật (cần lib DLL, hiện guard), emoji màu (cần cmap12), LRU/DPI | `TkvUI.Text/Bidi/Viet/I18nData/Widgets.tkv` |
| Phase 2 — GPU backend (D3D11/Metal/Vulkan, shader pipeline) | **Một phần** — abstraction + factory + pick + probe 44/44 (gồm resolve entry thật `vkGetInstanceProcAddr(NULL)`); **device ops 11/11 stub** + **shader pipeline abstraction 9/9** (module/layout/graphics/compute pipeline) + **D3D11/Metal stub 4/4**; GPU 66/66; tạo instance/device còn chặn ở đọc out-handle (gap compiler, cùng họ với registry); shader compile/Dx11/Metal thật cần host GPU thật. | `TkvUI.Gpu.tkv` |
| Phase 3 — Accessibility tree (UIA/AT-SPI/NSAccessibility/AccessibilityNodeInfo) | **Một phần** — data model + commit/diff 38/38; chưa bridge OS, chưa `a11y_node` integration trong Widgets | `TkvUI.A11y.tkv` |
| Phase 4 — Tooling & DX (VS Code ext, hot reload, inspector, tkvpkg, doc gen) | **Một phần** — `tools/verify.sh` 15 case + suite umbrella; extension/hot reload/inspector/pkg/docgen chưa | `tools/verify.sh`, `TokenVector.UI.tkv` |
| Phase 5 — Platform hardening (Android/iOS thật, Wayland, multi-window) | **Một phần** — Win32 thật (DIB mmap present + multi-window wiring), X11/Cocoa stub, Android/iOS scaffolding headless (SKIP đúng); pixel thật/Wayland chưa | `TkvUI.Platform.tkv`, `examples/TkvUI.*Demo.tkv` |
| Phase 6 — TkvUI.Web / Video / 3D / constraint solver | **Chưa làm** (layout `constraint` hiện chỉ clamp min/max) | — |
| Xuyên suốt — test tự động | **782 checks** qua suite (+11 font manual): core 47, graphics 29, text 160, effects 32, input 41, layout 50, widgets 101, media 80, bidi 112, platform 48, gpu 44, a11y 38; `tools/verify.sh` 15 case | `TokenVector.UI.tkv`, `tools/verify.sh` |

Đọc `docs/TkvUI.Roadmap.md §0` (ràng buộc compiler) trước khi viết `.tkv`; roadmap là nguồn sự thật cho v2, file này giữ vai trò kế hoạch v3.

---

## Phase 1: Text & Internationalization (4–6 weeks)

| Target | Tasks | Deliverable |
|--------|-------|-------------|
| **HarfBuzz shaping** | Pinvoke `hb_buffer_add_utf8`, `hb_shape`, `hb_buffer_get_glyph_infos`; add `TextShaper` class | `TextShaper.shape(text, font, features)` → `list[GlyphInfo]` → **ĐANG BLOCKED (2026-09-18)**: DLL `libharfbuzz.dll` load được, pinvoke `hb_buffer_add_utf8`/`hb_shape`/`hb_buffer_get_glyph_infos` gọi được, single-char shaping đúng (glyph id, cluster byte-based, advance với scale). **NHƯNG** multi-char (`"אב"`, `"AA"`, `"AAA"`) bị bug: glyph id thứ 2+ trả 0 (nên khác 0), cluster/advance chỉ đúng khi set scale; nguyên nhân: buffer stride/out-array index mismatch trong FFI (cần đọc struct glyph_info/position - gap compiler đọc out-buffer). Cần upstream: primitive đọc struct hoặc fix FFI marshal. Tạm dùng fallback bitmap/sequence-aware đã làm. |
| **Font atlas** | `stb_truetype` pinvoke → bake glyphs to `PixelSurface` atlas; LRU eviction | `FontAtlas.get_glyph(rune, size)` → `Rect2D + advance` |
| **Fallback chain** | FontConfig-like resolver: primary → Noto Sans → Noto Emoji → system | `FontFamily.resolve(rune)` → `FontFace` |
| **Bidi/RTL** | Pinvoke `fribidi_log2vis` or port Unicode Bidi Algorithm (UAX #9) | `TextShaper.set_direction(RTL/LTR/auto)` |
| **IME** | Platform hook: Win32 `ImmGetCompositionString`, Android `InputConnection`, iOS `UITextInput` | `TextFieldWidget.ime_composition` event |

**Milestone**: `draw_string("你好 🌍 שלום", rtl=true)` renders correctly. → ✅ **ĐẠT 2026-09-18** qua `bidi_draw_visual_atlas` (visual order UAX#9 + blit glyph thật từ atlas baked; emoji còn box).

---

## Phase 2: GPU Backend (6–8 weeks)

| Target | Tasks | Deliverable |
|--------|-------|-------------|
| **Abstraction layer** | `IGpuBackend` interface: `create_texture`, `draw_quad`, `draw_textured_quad`, `blur`, `present` | `GpuBackend` record + factory |
| **DirectX 11 (Win32)** | `ID3D11Device`, `CreateTexture2D`, `DrawIndexed` via pinvoke `d3d11.dll` | `Dx11Backend` |
| **Metal (macOS/iOS)** | `MTKView`, `MTLRenderPipeline`, `MTLTexture` via ObjC pinvoke | `MetalBackend` |
| **Vulkan (Linux/Android)** | `vkCreateInstance`, `vkCmdDrawIndexed` via `libvulkan.so`/`vulkan-1.dll` | `VulkanBackend` |
| **Shader pipeline** | Built-in shaders: solid, textured, SDF text, blur (compute) | `ShaderLibrary` embedded bytecode |
| **Fallback** | Auto-detect: GPU available → `GpuBackend`, else → `SoftwareBackend` | `Platform.create_gpu_backend()` |

**Milestone**: `TkvUI.Live` runs 4K @ 120fps on GPU path, software path unchanged.

---

## Phase 3: Accessibility Tree (4 weeks)

| Target | Tasks | Deliverable |
|--------|-------|-------------|
| **A11y data model** | `A11yNode{role, label, value, states, actions, bounds, children}` + tree root | `UIElement.a11y_node()` virtual |
| **Win32 UIAutomation** | `IRawElementProviderSimple`, `IValueProvider`, `IInvokeProvider` via `UIAutomationCore.dll` | `Win32A11yProvider` |
| **Linux AT-SPI** | `org.a11y.atspi.Accessible` D-Bus interface via `libatspi` pinvoke | `LinuxA11yProvider` |
| **macOS/iOS** | `NSAccessibility` / `UIAccessibility` protocols via ObjC | `CocoaA11yProvider` |
| **Android** | `AccessibilityNodeInfo` via JNI | `AndroidA11yProvider` |
| **Integration** | `RenderLoop` commits a11y tree after layout; `InvalidationManager` marks dirty a11y nodes | `A11yManager.update_tree()` |

**Milestone**: Narrator / NVDA / VoiceOver / TalkBack reads widget labels, states, activates buttons.

---

## Phase 4: Tooling & DX (ongoing, parallel)

| Target | Tasks | Deliverable |
|--------|-------|-------------|
| **VS Code extension** | Syntax highlight `.tkv`, `tkvc` build task, F5 debug (map IL→source via `#line`), IntelliSense (LSP stub) | `tokenvector.tkv` marketplace |
| **Hot reload** | `tkvc --watch` → recompile module → `Assembly.Load` new version → swap `RenderLoop` frame callback | Sub-second UI iteration |
| **Widget inspector** | Overlay showing bounds, a11y tree, dirty rects, spring values (toggle `F12`) | `DebugOverlayWidget` |
| **Package manager** | `tkvpkg` CLI: `tkvpkg add TkvUI.Chart`, `tkvpkg publish` → local NuGet feed | Ecosystem bootstrap |
| **Doc generator** | `tkvdoc` extracts `///` comments → markdown + playground | `docs/` auto-generated |

---

## Phase 5: Platform Hardening (4 weeks)

| Target | Tasks | Deliverable |
|--------|-------|-------------|
| **Android real device** | JNI `SurfaceTexture` → `ANativeWindow`, `Choreographer` callback → `RenderLoop.tick`, touch → `GestureRecognizer` | `TkvUI.AndroidDemo` runs on Pixel |
| **iOS real device** | `UIView` + `CALayer` + `CADisplayLink` in Swift/ObjC host app, `tkvc` AOT → framework | `TkvUI.IOSDemo` runs on iPhone |
| **Wayland** | `wl_compositor`, `xdg_shell`, `zwp_linux_dmabuf` for zero-copy | `WaylandPlatform` |
| **Multi-window** | `SurfacePool` per window, `RenderLoop` per window, shared `GpuBackend` | `Platform.create_multiple()` → ✅ **DONE 2026-09-18** (Win32): `win32_create_multiple`/`present_all`/`close_all` + `render_loop_pump_all`; 2 cửa sổ thật, headless-safe ngoài Win32 |

---

## Phase 6: Advanced Features (v3 scope)

| Feature | Estimate | Note |
|---------|----------|------|
| **TkvUI.Web** (WebView bridge) | 3 weeks | `WebViewWidget(url)`, `EvalJS`, `OnMessage` |
| **TkvUI.Video** (FFmpeg) | 3 weeks | `VideoPlayer(path)`, HW decode → texture |
| **TkvUI.3D** (software + optional GPU) | 4 weeks | `Matrix4x4`, `RasterizeTriangle`, `DepthBuffer` |
| **Layout constraint solver** | 2 weeks | Cassowary-style `layout_constraint_solve()` |

---

## Summary Timeline

| Quarter | Focus | "Don't Choose" → "Choose" |
|---------|-------|---------------------------|
| Q1 | Text + GPU | Complex text ✅, GPU ✅ |
| Q2 | A11y + Tooling | Accessibility ✅, DX ✅ |
| Q3 | Platform hardening | Android/iOS real ✅, Multi-window ✅ |
| Q4 | v3 features | Web/Video/3D ✅ |

---

## Hướng nâng cấp tiếp theo (đánh giá 2026-09-17, sau v2.2.2)

Bối cảnh đã có: glyph atlas ~4.2×, half-res blur ~2.5× (chưa dùng trong product path),
selftest 299 check, packaging .tkvpkg/.nupkg đầy đủ.

### 1. Quick wins (1–3 ngày mỗi mục)

> **Trạng thái sau v2.3.1 (2026-09-18):** 5/5 mục đã xong — present memory-mapped (P2.4), áp half-res blur (P2.5), FocusManager (P2.7), cache char_code (P2.6), bilinear upsample (P2.8, kèm selftest trong Effects).
| Item | Chi tiết | Tác dụng |
|---|---|---|
| **BitBlt present** ⭐ | Thay per-pixel `SetPixelV` trong `presentDiff` bằng `gdi_bit_blt` (pinvoke đã có trong Platform, chưa dùng) | Điểm nóng lớn nhất còn lại: presentDiff từng đo ~430ms/frame (roadmap §7.6); blit cả DIB 1 lần có thể xuống vài ms |
| Áp half-res blur | `backdrop_blur` + `draw_drop_shadow` đổi sang `half_res_blur` khi radius ≥ 4 | Hàm đã có, chỉ rewire + sửa selftest — hưởng lợi tức thì |
| Bilinear upsample | Cho `half_res_blur` thay nearest-neighbor | Giảm artifacts bậc thang sau text/mép sắc, quan trọng khi half-res là đường mặc định |
| Focus manager | Tab/Shift-Tab, focus ring, caret nháy theo FrameScheduler | TextFieldWidget đã có `focused` nhưng chưa điều hướng bàn phím; tiền đề form thật |
| Cache `char_code` | Bảng 95 entry cache on first hit trong `text_atlas_draw_string` | Nhỏ nhưng rẻ (loại binary search 7 bước/ký tự/frame) |

### 2. Trung hạn (mở khóa phase mới)

| Item | Chi tiết | Mở khóa |
|---|---|---|
| **TTF rasterizer** ⭐ | Parse glyf quadratic (không hinting), bake vào atlas hiện có; DPI thật qua `GetDeviceCaps` (pinvoke đã có). **2026-09-18**: milestone scripts (Hebrew/Arabic/CJK) xong bằng đường bake-subset (`TkvUI.I18nData` + `text_atlas_bake_i18n_all`, không cần file-read); file I/O runtime vẫn gap | Tiếng Việt, đa cỡ chữ, đa DPI — giá trị sản phẩm cao nhất |
| Theme theo OS | Đọc registry dark/light (`RegGetValueA`), hot-switch runtime | UX hiện đại |
| Multi-window | Pool DIB/memDC theo `PlatformWindowHandle`, RenderLoop pump nhiều window | Khung SurfacePool/RenderLoop đã sẵn, chỉ còn wiring |

### 3. Bị chặn bởi compiler tkvc (đẩy upstream)

| Item | Cần gì | Mở khóa |
|---|---|---|
| Đọc registry/OS theme | Đã vét 11 cơ chế 2026-09-18, chốt BLOCKED: `extern_method` exact-match (không `object`), không primitive đọc out-buffer, linter chặn symbol ordinal, và **tkvc gán cứng identity Framework (4.0.0.0/b77a) cho mọi extern assembly** → DLL managed riêng không load được (FileLoadException) dù đúng cạnh exe; ECMA key không trích được để delay-sign; không primitive spawn/wait. Cần upstream: reference đúng identity thật (khi đó shim C# 20 dòng là đủ). Tạm dùng `theme_detect_os` stub + logic polling | Theme theo OS thật, hot-switch runtime |
| X11/Wayland thật | pinvoke `.so` (hiện bắt buộc `.dll`). Đã probe 2026-09-18: linter từ chối cứng (kể cả flag `--no-lint` — flag này không tồn tại); thêm 2 tường độc lập: không primitive cấp phát/đọc bộ nhớ native trên Linux (cần cho XImage/event struct) và không host X/Linux để test + không primitive socket cho đường wire-protocol. Giữ stub `X11Platform` (handle-gated, headless-safe) | Linux desktop, bỏ vehicle WinForms |
| Android/iOS pixel thật | `.so`/`.dylib` + `memcpy`/`Marshal.WriteByte` | Demo chạy trên thiết bị |
| Decode ARGB `>>`/`&` | Bit shift/mask operators | Blur + blend nhanh thêm ~1.5–2× (đã đo: `//`/`%` chi phối) |
| Zero-console | `.subsystem 0x0002` | GUI app không kèm console |
| DLL thuần | `--target library` | Nupkg sạch (DLL hiện là exe đổi tên) |

### 4. Dài hạn (Phase 3/4/6 — xem các phần trên)

- **A11y tree**: thêm `a11y_role`/`a11y_label` vào `UIElement` từ sớm để widget catalog không phải sửa hàng loạt sau; bridge OS để sau.
- **GPU backend abstraction** (`create_texture`/`draw_quad`/`present`, software fallback) — API đủ ổn định để tách layer.
- **TkvUI.Web / Video / Chart / 3D** — chưa bắt đầu.

### Thứ tự đề xuất (cập nhật 2026-09-18: 3 việc cũ xong cả — present mmap, TTF milestone, FocusManager)

3 việc tiếp theo làm được, xếp theo giá trị/công sức: **(1) Multi-window wiring** (`SurfacePool` + `RenderLoop` đã sẵn, headless-test được) → **(2) GPU shader pipeline thật** (`D3DCompile`/`vkCreateShaderModule`/`MTLLibrary` cần host GPU thật, bindings sẵn) → **(3) HarfBuzz shaping thật** (bindings+guard sẵn, cần lib DLL để test sống).

**Resource estimate**: 1–2 core devs (compiler + runtime), 1 platform specialist per OS, 1 tooling dev. Total ~12–18 months to parity with Avalonia/Uno on core criteria.