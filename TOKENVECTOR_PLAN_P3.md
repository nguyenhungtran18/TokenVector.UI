# TokenVector.UI — Plan P3: Repo Hygiene + Test Methodology + AccessKit Redirect

> Ngày lập: 2026-09-18. Đầu vào: `docs/COMPETITORS.md` (gap list),
> `docs/BENCH.md`, `docs/WASM_STATUS.md`, `docs/A11Y_NVDA.md`.
> Nguyên tắc giữ nguyên từ P2: chỉ claim khi có số đo/bằng chứng chạy được.

---

## P3-A: REPO HYGIENE SPRINT (0.5–1 ngày, rẻ nhất, làm trước)

| # | Việc | Xong khi |
|---|---|---|
| A1 | `CONTRIBUTING.md` (build/test/lint, quy ước compiler §0, cách thêm module + selftest) | file tồn tại, dẫn từ README |
| A2 | `.github/ISSUE_TEMPLATE/` (bug/feature) + PR template checklist (verify PASS, docs update) | tạo issue test đóng lại được |
| A3 | README: badges (verify status thủ công), screenshots (`build/canvas_shot.png`, Live window), niche lên đầu (Việt-first, PDF/SQL built-in, <1 MB) | đọc 60s hiểu repo để làm gì |
| A4 | Releases theo tag + CHANGELOG discipline (hiện CHANGELOG có nhưng không gắn release) | tag v2.9.0 + notes |
| A5 | `docs/API.md`: index tra cứu theo module (hàm chính + file + selftest entry), sinh bán-tự động bằng grep, không viết tay toàn bộ | tra cứu được mọi public API mà không cần grep source |

---

## P3-B: TEST METHODOLOGY UPGRADE (2–3 ngày)

| # | Việc | Xong khi |
|---|---|---|
| B1 | Benchmark driver 1 lệnh (`tools/bench_all.ps1`): chạy BenchText/BenchWidgets/CrudBench + pyqt đối chứng, ghi `docs/BENCH.md` table + baseline PyQt versioned (hiện 6.11.0) | 1 lệnh ra đủ 4 số, không copy tay |
| B2 | kittest-style test (copy egui): query widget qua cây a11y thay vì chỉ đếm pixel — `NativeButton <- tree node[role=button,label]` | ít nhất 5 case click/select/verify qua tree, chạy headless |
| B3 | Chuẩn pass/fail cho动画/perf flake: ngưỡng + retry + log percentile (hiện tại GetTickCount quantum 15.6 ms làm số nhảy) | bench lặp lại 3 lần cho cùng kết luận thắng/thua |

---

## P3-C: ACCESSKIT REDIRECT (chiến lược, thay thế hướng COM-vtable)

**Quyết định:** dừng hướng "viết COM vtable tay" cho Phase 9.2. Mục tiêu mới là
**bắn cây a11y ra AccessKit C bindings** (như Slint/egui/Bevy đã làm).

| # | Việc | Blocker | Xong khi |
|---|---|---|---|
| C1 | Spike gọi AccessKit C từ .tkv: `accesskit_node_*` qua pinvoke | `.so/.dll` pinvoke + marshal struct (đang blocked, track upstream) | 1 node xuất hiện trong Inspect.exe (Windows) |
| C2 | Trong lúc chờ C1: giữ host-driven file-watch hiện tại (`uia_dump_file`, outbox) + C# host mẫu đọc JSON dựng provider | Không (làm được ngay) | `tools/uia_host/` mẫu chạy + NVDA đọc được 1 button thật |
| C3 | Áp kittest-style (B2) lên bridge ngay khi C1/C2 xong | C1 hoặc C2 | test a11y chạy trong verify.sh |

---

## P3-D: WATCHLIST (không action, track upstream, review mỗi tháng)

| Item | Blocker | Dấu hiệu mở lại |
|---|---|---|
| WASI AOT native | .NET 9 xóa workload; net8 không engage | tkvc emit WASM trực tiếp, hoặc .NET có WASI-AOT ổn định |
| Dialog/IME native, TTF embed, `.so` pinvoke | marshal out-buffer / byte array | tkvc changelog có struct marshal |
| AT-SPI/JNI, X11/Cocoa/device thật | VM/device | có máy test |
| Indic/Thai shaping, font fallback sâu | research + tables | sau 11.1 |

---

## THỨ TỰ LÀM

1. P3-A (nửa ngày, xong là repo nhìn "sống" ngay).
2. P3-B1 + B3 (1 ngày, khóa số benchmark khỏi tranh cãi).
3. P3-C2 (2–3 ngày, bằng chứng a11y đầu tiên đọc được thật).
4. P3-B2 (sau C2).
5. P3-D: review monthly, không đốt giờ.

## ĐỊNH NGHĨA XONG P3

- [ ] Repo có CONTRIBUTING/templates/badges/screenshots/API index/releases.
- [ ] `tools/bench_all.ps1` 1 lệnh ra đủ số BENCH.
- [ ] NVDA đọc được ≥ 1 widget TkvUI thật (qua C2), có log làm bằng chứng.
- [ ] Không mục nào trong P3-D bị đụng vào nếu blocker chưa mở.
