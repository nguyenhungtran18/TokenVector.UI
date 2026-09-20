# A11Y_NVDA — Bằng chứng screen reader đầu tiên (Phase 9.1)

> Ngày đo: 2026-09-18. Máy Windows x64, desktop tương tác (có user active),
> NVDA 2026.1.1 portable (`build/nvda/`, không cài vào hệ thống),
> log DEBUG (`IO - speech.speech.speak: Speaking [...]`).
> Script lặp lại: `tools/nvda_probe.ps1`. NVDA dùng để làm gì: xem giải thích
> trong session Phase 9.1 (trọng tài độc lập cho claim accessibility).

## 1. Setup validation (pass ổn định 3/3 lần)

| Check | Kết quả |
|---|---|
| NVDA init (`NVDA initialized` trong log) | ✅ |
| `UiaClientsAreListening() == 1` (pinvoke trực tiếp) | ✅ |
| `ab_uia_listening()` của bridge | ❌ trả 0 — probe `tkv_has_file("UIAutomationCore.dll")` quá chặt (DLL ở System32, không nằm cạnh exe). **Phải sửa ở Phase 9.2**: gọi thẳng + guard, thay vì probe file. |

## 2. Positive control: WinForms thật (_tls_)

| Item | Kết quả |
|---|---|
| Window title `'NvdaCtl'` được đọc | ✅ (manual 1/1, script 1/2) |
| Button `'SaveBtn', 'button'` được đọc | ✅ manual 2/2; script 0/2 (flaky, xem §4) |

## 3. Cửa sổ TkvUI Live custom-drawn (2/2 lần nhất quán)

| Item | Kết quả |
|---|---|
| NVDA đọc title/chrome của cửa sổ layered | ❌ 0 utterance |
| NVDA đọc widget (button/slider/list tự vẽ) | ❌ 0 utterance |
| Speech trong lúc chạy chỉ là activity của user/OS (Settings, taskbar) | quan sát được |

**Kết luận: widget tự vẽ hiện VÔ HÌNH với NVDA.** Đúng như thiết kế stub —
JSON dump của bridge chưa nối vào UIA tree thật. Đây là cơ sở để làm Phase 9.2
(UIA provider thật / host-driven), không phải để claim.

## 4. Flakiness đã biết (trung thực)

- `nvda_probe.ps1` lần 1: control title=False button=False; lần 2 (thêm
  settle + retry): title=True button=False. Manual cùng mechanics: pass.
- Nguyên nhân chính: máy có user đang active (log lẫn speech của IDE Gemini,
  Alt-Tab, taskbar) + NVDA mới start cần thời gian settle + focus nền
  (`Control.Focus()` không foreground) không deterministic.
- Script KHÔNG dùng SendKeys/cướp focus (tôn trọng user) — đánh đổi bằng
  flakiness này. Chạy trên máy CI chuyên dụng (không user) sẽ ổn định hơn.
- Quy tắc an toàn đã áp dụng: kill mọi instance NVDA cũ trước khi start,
  `try/finally` dọn dẹp, không để orphan process.

## 5. P3 — Win32 mirror (2026-09-19, headless-verified)

Vì tkv không thể implement COM interface (không CCW/vtable), đường đi thực
tế là **mirror**: mỗi node ab-tree → 1 HWND thật (`CreateWindowExA` class hệ
thống, pinvoke đã chứng minh ở `Platform.create`). Screen reader thấy
mirror qua provider Win32 mặc định — không cần code COM nào.

- API: `uia_mirror_class/style/build/destroy` (`TkvUI.Uia.tkv`), chỉ dùng
  pinvoke có sẵn; `show=0` headless-safe (CI), `show=1` cho probe tay.
- Verify headless: parent HWND != 0, đủ HWND con, destroy sạch
  (uia selftest `mirror.*`, 33/33 PASS).
- Giới hạn v1 (ghi nhận): class ANSI (label non-ASCII vỡ font), không
  subclass proc (không click/focus events), composite → STATIC container,
  cần InitCommonControls nên tránh SysTreeView32/SysListView32.

## 6. Quy trình probe tay (khi có desktop + NVDA)

1. Build exe demo gọi `uia_mirror_build(..., show=1)` từ cây ab thật
   (ví dụ Live window: title + 2–3 nút).
2. Chạy `tools/nvda_probe.ps1` — kỳ vọng: `live_widgets=True` (trước đây
   False ổn định, xem §3),IBAction: focus từng nút mirror, NVDA đọc tên.
3. So sánh trực tiếp với control WinForms (§2) trong cùng 1 log run.
