# TkvUI Development Plan: Turn Weaknesses → Strengths

> Goal: Make every "Don't Choose" criterion become a "Choose" reason.

---

## Trạng thái hiện tại (đối chiếu kế hoạch ↔ code, cập nhật 2026-09-16, v2.1.0)

| Hạng mục trong plan | Trạng thái | Ở đâu |
|---|---|---|
| Phase 1 — HarfBuzz shaping, font atlas, fallback chain, bidi/RTL, IME | **Chưa làm** — đang là font bitmap 5x7 (95 glyph) + wrap theo từ; ký tự ngoài bảng 32..126 vẽ box fallback | `TkvUI.Text.tkv` |
| Phase 2 — GPU backend (D3D11/Metal/Vulkan, shader pipeline) | **Chưa làm** — software rasterizer đã ổn định và có selftest | `TkvUI.Graphics.tkv` |
| Phase 3 — Accessibility tree (UIA/AT-SPI/NSAccessibility/AccessibilityNodeInfo) | **Chưa làm** | — |
| Phase 4 — Tooling & DX (VS Code ext, hot reload, inspector, tkvpkg, doc gen) | **Một phần** — đã có `tools/verify.sh` + `main()` selftest suite; extension/hot reload/inspector/pkg/doc gen chưa | `tools/verify.sh`, `TokenVector.UI.tkv` |
| Phase 5 — Platform hardening (Android/iOS thật, Wayland, multi-window) | **Một phần** — khung `AndroidPlatform`/`IOSPlatform` + example headless, gate theo `detect_platform()`; pixel lên thiết bị cần host shim; Wayland/multi-window chưa | `TkvUI.Platform.tkv`, `examples/TkvUI.*Demo.tkv` |
| Phase 6 — TkvUI.Web / Video / 3D / constraint solver | **Chưa làm** | — |
| Xuyên suốt — test tự động | **Đã bổ sung (P1.1)** — mỗi module có `*_selftest`, suite umbrella chạy tất cả, `tools/verify.sh` 12 case (`TKVUI_VERIFY_OK`) | `TokenVector.UI.tkv`, `tools/verify.sh` |

Đọc `docs/TkvUI.Roadmap.md §0` (ràng buộc compiler) trước khi viết `.tkv`; roadmap là nguồn sự thật cho v2, file này giữ vai trò kế hoạch v3.

---

## Phase 1: Text & Internationalization (4–6 weeks)

| Target | Tasks | Deliverable |
|--------|-------|-------------|
| **HarfBuzz shaping** | Pinvoke `hb_buffer_add_utf8`, `hb_shape`, `hb_buffer_get_glyph_infos`; add `TextShaper` class | `TextShaper.shape(text, font, features)` → `list[GlyphInfo]` |
| **Font atlas** | `stb_truetype` pinvoke → bake glyphs to `PixelSurface` atlas; LRU eviction | `FontAtlas.get_glyph(rune, size)` → `Rect2D + advance` |
| **Fallback chain** | FontConfig-like resolver: primary → Noto Sans → Noto Emoji → system | `FontFamily.resolve(rune)` → `FontFace` |
| **Bidi/RTL** | Pinvoke `fribidi_log2vis` or port Unicode Bidi Algorithm (UAX #9) | `TextShaper.set_direction(RTL/LTR/auto)` |
| **IME** | Platform hook: Win32 `ImmGetCompositionString`, Android `InputConnection`, iOS `UITextInput` | `TextFieldWidget.ime_composition` event |

**Milestone**: `draw_string("你好 🌍 שלום", rtl=true)` renders correctly.

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
| **Multi-window** | `SurfacePool` per window, `RenderLoop` per window, shared `GpuBackend` | `Platform.create_multiple()` |

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

**Resource estimate**: 1–2 core devs (compiler + runtime), 1 platform specialist per OS, 1 tooling dev. Total ~12–18 months to parity with Avalonia/Uno on core criteria.