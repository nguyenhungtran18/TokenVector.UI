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

## 2. API surface cần cho decode (tối thiểu, theo `codec_api.h`)

1. `int WelsCreateDecoder(ISVCDecoder** ppDecoder)` — con trỏ-nhận-con-trỏ.
   ✅ **Gọi được ngay** (đã chứng minh rc=0 bằng ctypes): pinvoke `.tkv`
   với `i64` ra/vào đã chứng minh ở `TkvUI.Platform`/`TkvUI.Font`.
2. `int Initialize(const SDecodingParam* pParam)` — truyền **struct**.
   🔴 Chặn (tkvc không marshal struct — xem `docs/COMPILER_GAPS.md`).
3. `DECODING_STATE DecodeFrame2(const u8* pSrc, int len, u8** ppDst,
   SBufferInfo* pDstInfo)` — struct vào + **mảng 3 con trỏ YUV ra** +
   struct trạng thái ra (width/height/stride/bufferStatus).
   🔴 Chặn (out-struct + out-handle — cùng họ gap với GPU device/X11).
4. `int GetOption(...)`, `void WelsDestroyDecoder(...)` — destroy ✅ gọi được.

Đường vòng đã chứng minh trong repo (C# shim build+call được) hiện cũng
chặn ở `tkvc` gán cứng identity Framework cho extern assembly
(`DEVELOPMENT_PLAN.md` §3) — cần upstream mở **đúng 2 primitive**:
**(a)** đọc/ghi struct native qua pinvoke, **(b)** reference đúng identity
assembly. Khi đó shim C# ~20 dòng (mẫu OpenH264Lib.NET) là đủ.

## 3. Giới hạn phải nói rõ

- **Chỉ Constrained Baseline (đến Level 5.2).** MP4 Main/High profile
  (đa số YouTube/phone quay) OpenH264 **từ chối decode** — nhóm đó vẫn cần
  FFmpeg (LGPL build) về sau. Baseline đủ cho WebRTC + file tự encode.
- Không có demux/container: vẫn cần MP4 demux thuần `.tkv` (P1 đã lên
  kế hoạch) để lấy Annex-B stream cho vào `DecodeFrame2`.
- Không có audio: AAC vẫn theo đường MDCT (tiền lệ `dsp_mdct.tkv`).

## 4. Next steps (theo thứ tự)

1. ✅ Tải + verify DLL (xong 2026-09-22).
2. Viết yêu cầu upstream 2 primitive (a)(b) kèm use-case này (đo được,
   có deadline rõ thay vì "cần marshal" chung chung).
3. Khi upstream mở: shim C# + `TkvUI.H264.tkv` (pinvoke 4 hàm trên +
   copy YUV ra `PixelSurface` + selftest decode 1 frame Baseline bake sẵn).
4. MP4 demux thuần `.tkv` song song (không chặn bởi compiler).
5. FFmpeg LGPL cho Main/High — sau cùng.