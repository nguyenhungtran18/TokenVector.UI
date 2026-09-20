## Checklist (bắt buộc tick hết trước khi merge)

- [ ] `bash tools/verify.sh` → `TKVUI_VERIFY_OK` (dán 3 dòng cuối log vào PR)
- [ ] Rule #0 pure-.tkv: không file non-`.tkv` mới ở root/`examples/` (trừ `.md`/`.json`/`.nuspec`); không unguarded native call
- [ ] Module mới đã đăng ký đủ 3 chỗ: `tkvui.pkg.json` + `TokenVector.UI.tkv` + `tools/verify.sh`
- [ ] Docs cập nhật nếu đổi số/hành vi: `docs/BENCH.md`, `docs/*_STATUS.md`, `docs/API.md`, `CHANGELOG.md`
- [ ] Không để lại process sống (server/NVDA), không commit `build/`/`dist/`/`*.log`

## Mô tả thay đổi

<!-- Gì + vì sao + bằng chứng chạy được (log/screenshot/số đo). -->
