# tools/capture_utf8.ps1 — chay exe, ghi stdout ra file UTF-8 (khong BOM).
#
# Ly do ton tai: PowerShell `>` / Out-File mac dinh ghi UTF-16 (co BOM) tren
# Windows PowerShell 5.1 — file base64 76800 chars da tung thanh 153606 bytes
# (Phase 7.3). Moi pipeline text-intercept (base64, JSON, PDF) PHAI qua day.
#
# Dung:  powershell -NoProfile -File tools/capture_utf8.ps1 -Exe build/x.exe -ExeArgs @("7") -Out build/x.out

param(
  [Parameter(Mandatory=$true)][string]$Exe,
  [string[]]$ExeArgs = @(),
  [Parameter(Mandatory=$true)][string]$Out
)

$text = & $Exe @ExeArgs 2>&1 | Out-String
$code = $LASTEXITCODE
[IO.File]::WriteAllText($Out, $text)
$n = (Get-Item $Out).Length
"captured $Out (${n} bytes) exit=$code"
if ($code -ne 0) { exit $code }
