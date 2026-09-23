# OpenH264 cho TokenVector.UI — tải về, khỏi xây (verified 2026-09-22)

Kết quả đã verify bằng chạy thật trên máy này:
- Tải `openh264-2.6.0-win64.dll` (452KB → 978KB), header `MZ`, đủ 3 exports.
- `LoadLibrary` OK; `WelsCreateDecoder` trả rc=0 + con trỏ decoder hợp lệ;
  `WelsDestroyDecoder` OK (verify bằng Python ctypes).
- Tái lập 1 lệnh: `powershell -ExecutionPolicy Bypass -File tools/fetch_openh264.ps1`
  (hoặc `bash tools/fetch_openh264.sh`). DLL nằm ở `build/` (bị `.gitignore`
  chặn — KHÔNG commit binary, đúng mẫu OpenH264Lib.NET).

## 1. Vì sao là OpenH264 mà không phải x264/ffmpeg/Chrome

| Nguồn | License | Kết luận |
|---|---|---|
| **Cisco OpenH264 binary** (`ciscobinary.openh264.org`) | BSD-2 + Cisco trả MPEG-LA royalties **cho chính binary của họ** (điều kiện: tải từ Cisco, xem `BINARY_LICENSE.txt`) | ✅ DÙNG — tải về, khỏi xây |
| Build OpenH264 từ source | BSD-2 nhưng **tự chịu** patent fees | ⚠️ Tránh — mất lá chắn Cisco |
| x264 / x264net wrapper | **GPL-2.0** | ❌ CẤM — nhiễm GPL vào repo MIT |
| FFmpeg DLLs | LGPL/GPL tùy build | ⚠️ Để sau (cần cho Main/High profile, xem §4) |
| Bóc codec từ Chrome | Vi phạm ToS + patent + kỹ thuật không tách được | ❌ Đã loại ở phân tích trước |

Tham khảo đúng mẫu tích hợp: `secile/OpenH264Lib.NET` (MIT) — native DLL +
bridge mỏng + consumer .NET; sample của họ tải đúng `openh264-*-win32.dll`
từ Cisco như script trên.

## 2. API surface — TRẠNG THÁI 2026-09-23: DECODE + ROUND-TRIP ✅

1. `WelsCreateDecoder` — pinvoke i64 ✅ (chứng minh từ 22/09).
2. `Initialize(SDecodingParam*)` — struct marshal → **vòng qua C# shim**
   (`tools/h264/OpenH264Shim.cs`, R1 không cần cho đường này).
3. `DecodeFrame2(...)` + `SBufferInfo` out — cũng nằm trong shim; `.tkv`
   chỉ gọi static methods i32/i64 + R2 buffers (R2) — identity assembly
   đầy đủ inline (R3 đã mở).
4. **Đã verify chạy thật:**
   - `ShimTest`: decode `gop.264` Baseline 960×540 → 6 frame RGB.
   - `RoundTrip` (`tools/h264/RoundTrip.cs`): encoder OpenH264 → Annex B
     → shim decode → 11/12 frame 64×64 gray đúng cả level (RC=0).
     Bẫy đã gặp: `SFrameBSInfo` có **nhiều layer** — frame IDR để slice ở
     `sLayerInfo[1]`, chỉ đọc layer[0] thì mất IDR → decoder `rc=18`
     (`dsNoParamSets|dsRefLost`) cho mọi frame P.
   - `TkvUI.H264.tkv` selftest: stream 230B bake trong source → 8/8
     (`H264_OK`), thiếu dll → `H264_OK H264_SKIPPED` (verify SKIP, 0 FAIL).

Giới hạn còn lại: **chỉ Constrained Baseline** (§3), không muxer/audio.

## 3. Giới hạn phải nói rõ

- **Chỉ Constrained Baseline (đến Level 5.2).** MP4 Main/High profile
  (đa số YouTube/phone quay) OpenH264 **từ chối decode** — nhóm đó vẫn cần
  FFmpeg (LGPL build) về sau. Baseline đủ cho WebRTC + file tự encode.
- Không có demux/container: vẫn cần MP4 demux thuần `.tkv` (P1 đã lên
  kế hoạch) để lấy Annex-B stream cho vào `DecodeFrame2`.
- Không có audio: AAC vẫn theo đường MDCT (tiền lệ `dsp_mdct.tkv`).

## 4. Next steps (theo thứ tự)

1. ✅ Tải + verify DLL (2026-09-22).
2. ✅ Upstream mở primitive (a) R1 struct + (b) R3 identity — đã đóng.
3. ✅ Shim C# + `TkvUI.H264.tkv` selftest decode bake sẵn — 8/8 (23/09).
   Round-trip encode→decode verify riêng (`tools/h264/RoundTrip.cs`, 11/12).
4. MP4 demux thuần `.tkv` (song song, không chặn).
5. Encode từ `.tkv` (encoder vtable đã tay thử trong RoundTrip — có thể
   gói shim thêm static Encode* khi cần).
6. FFmpeg LGPL cho Main/High — sau cùng.