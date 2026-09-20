# tools/serve_static.ps1 — static file server song doc lap session.
#
# Ly do ton tai: PowerShell Job chet theo session (Phase 7.3: http.server bien
# mat giua cac lenh) -> dung Start-Process + PID file de start/stop chu dong.
#
# Dung:
#   powershell -NoProfile -File tools/serve_static.ps1 -Dir build/x/wwwroot -Port 8934   # start
#   powershell -NoProfile -File tools/serve_static.ps1 -Port 8934 -Stop                   # stop

param(
  [string]$Dir = "build/wasm-canvas/publish/wwwroot",
  [int]$Port = 8934,
  [switch]$Stop
)

$pidFile = "build/serve_$Port.pid"

if ($Stop) {
  if (Test-Path $pidFile) {
    $srvPid = [int](Get-Content $pidFile)
    Stop-Process -Id $srvPid -Force -ErrorAction SilentlyContinue
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    "stopped server pid=$srvPid port=$Port"
  } else {
    "no pid file for port=$Port (nothing to stop)"
  }
  exit 0
}

$py = $null
foreach ($c in @("C:\Users\Admin\AppData\Local\Python\pythoncore-3.14-64\python.exe")) {
  if (Test-Path $c) { $py = $c }
}
if (-not $py) {
  $cmd = Get-Command python3.exe, python.exe -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($cmd) { $py = $cmd.Source }
}
if (-not $py) { Write-Error "Khong tim thay python"; exit 2 }
if (-not (Test-Path $Dir)) { Write-Error "Khong thay thu muc: $Dir"; exit 2 }

$p = Start-Process -FilePath $py -ArgumentList "-m", "http.server", "$Port" `
  -WorkingDirectory $Dir -WindowStyle Hidden -PassThru
"$($p.Id)" | Out-File $pidFile -Encoding ascii -NoNewline
Start-Sleep 2
try {
  $r = Invoke-WebRequest "http://localhost:$Port/" -UseBasicParsing -TimeoutSec 10
  "serving $Dir on port=$Port pid=$($p.Id) HTTP $($r.StatusCode)"
} catch {
  "server started pid=$($p.Id) but probe failed: $($_.Exception.Message)"
  exit 1
}
