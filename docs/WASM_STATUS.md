# WASM Status — TokenVector.UI trên WebAssembly

> Ngày verify: 2026-09-18. Toolchain: .NET 8.0.425 + wasi-experimental 8.0.31
> + wasm-tools 8.0.31, wasmtime 48.0.2, Chrome headless.
> Script: `tools/pack_wasm.sh`. Entry mẫu: `TkvUI.Data:data_selftest`,
> `TkvUI.BrowserDemo:browser_frame/browser_info`.

## 1. WASI interpreter — ✅ CHẠY THẬT

- Pipeline: tkvc → IL → ilasm `/dll` → `dotnet build wasi-wasm` → AppBundle
  (~12.4 MB: `dotnet.wasm` 10.9 MB + `icudt.dat` 1.5 MB).
- `wasmtime run --dir . ./dotnet.wasm host` → **PASS wasmtime (DATA_OK)**.
- Caveat: selftest có ghi file (`ab_dump_tree` → `build/...`) crash trong
  sandbox WASI (chỉ map AppBundle). Dùng entry pure-compute để chứng minh.

## 2. WASI AOT native — ❌ KHÔNG KHẢ THI trên toolchain hiện tại (đã điều tra tới gốc)

- `AOT=1` (.NET 8.0.425 + wasi-experimental 8.0.31): publish thành công nhưng
  `dotnet.wasm` **hash giống hệt** interpreter (E0C25C66), dù đã truyền
  `-p:RunAOTCompilation=true` một cách tường minh.
- Thử .NET 9.0.318 (cài side-by-side để test): workload `wasi-experimental`
  **bị xóa khỏi .NET 9** (`error: not supported in .NET 9`); chỉ còn bản
  `wasi-experimental-net8` (target net8.0, cùng họ với bản đã fail).
- Kết luận: không có đường WASI-AOT nào hoạt động trên máy này (8 không
  engage, 9 không còn workload). Tạm dùng interpreter (mục 1) — ngang
  Pyodide, đúng fallback plan đã dự báo. Mở lại khi upstream (tkvc emit
  trực tiếp WASM hoặc .NET có WASI-AOT ổn định).

## 3. Browser canvas — ✅ CHẠY THẬT (Phase 7.3)

- `TARGET=browser`: Blazor WASM host + `TkvBridge.GetFrame(int)` (JSInvokable)
  gọi `TKVUI.BrowserDemo.browser_frame` → base64 RGBA 160×90 → JS
  `putImageData` → `<canvas>` → `requestAnimationFrame` loop. Frame counter
  mirror ra `<span id="tkvframe">` để kiểm tra headless.
- Publish Release ra `TKVUI.*.wasm` (per-assembly AOT của Blazor) +
  `dotnet.native.wasm` — pass mọi check của script.
- Chrome headless verify (2 lần độc lập):
  - Screenshot: canvas render đúng scene (title, nút Go, progress 63%,
    thanh trượt) — xem `build/canvas_shot.png`, `canvas_shot4.png`.
  - `--dump-dom`: `<span id="tkvframe">frame=7</span>` / `frame=8` /
    `frame=10` ở các run khác nhau → rAF loop sống, animation tiến triển.
- Hạ tầng (2 bẫy Windows đã xử lý dứt điểm):
  - `tools/serve_static.ps1` — serve/stop qua Start-Process + PID file
    (PowerShell Job chết theo session, không dùng được).
  - `tools/capture_utf8.ps1` — hứng stdout exe ra file UTF-8 (PowerShell `>`
    mặc định ghi UTF-16 có BOM: base64 76800 chars từng thành 153606 bytes).
  - Chrome screenshot đôi khi cần retry (lần đầu dính "Loading" do server
    chưa ấm — `serve_static.ps1` đã probe HTTP 200 trước khi trả về).
