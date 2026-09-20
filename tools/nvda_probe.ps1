# tools/nvda_probe.ps1 — kiem chung NVDA doc duoc gi (Phase 9.1, chay tay).
#
# 1. Start NVDA portable (DEBUG log) + cho "NVDA initialized".
# 2. UiaClientsAreListening (pinvoke truc tiep, doi chieu voi ab_uia_listening).
# 3. Positive control: WinForms Button/TextBox tu dao focus -> parse log speech.
# 4. Cua so TkvUI Live custom-drawn -> parse log (ky vong: NVDA khong thay).
# 5. Stop NVDA. In checklist.
#
# Dung:  powershell -NoProfile -File tools/nvda_probe.ps1 [-NvdaExe build/nvda/portable/nvda.exe] [-LiveExe build/live_run2.exe]
# Yeu cau: desktop tuong tac + audio (NVDA van log duoc khi khong co loa).
# LUU Y: khong SendKeys/cuop focus (may co the co nguoi dung) — form tu dao focus.

param(
  [string]$NvdaExe = "build/nvda/portable/nvda.exe",
  [string]$LiveExe = "build/live_run2.exe"
)

$root = (Get-Location).Path
$logDir = Join-Path $root "build/nvda"
$log = Join-Path $logDir "probe.log"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
if (Test-Path $log) { Remove-Item $log -Force }
if (-not [IO.Path]::IsPathRooted($NvdaExe)) { $NvdaExe = Join-Path $root $NvdaExe }
if (-not [IO.Path]::IsPathRooted($LiveExe)) { $LiveExe = Join-Path $root $LiveExe }

if (-not (Test-Path $NvdaExe)) {
  "SKIP: khong thay NVDA ($NvdaExe). Tai installer + tao portable: xem docs/A11Y_NVDA.md"
  exit 3
}
if (-not (Test-Path $LiveExe)) {
  Write-Error "Khong thay Live exe ($LiveExe)"
  exit 2
}

Add-Type -Namespace TkvNvda -Name Uia -MemberDefinition '[System.Runtime.InteropServices.DllImport("UIAutomationCore.dll")] public static extern int UiaClientsAreListening();'

$results = @{}

Stop-Process -Name nvda -Force -ErrorAction SilentlyContinue
Start-Sleep 3

try {
  Start-Process -FilePath $NvdaExe -ArgumentList "-l", "10", "--log-file=$log" -WindowStyle Minimized
  $ready = $false
  for ($i = 0; $i -lt 90; $i++) {
    if ((Test-Path $log) -and (Select-String -Path $log -Pattern "NVDA initialized" -Quiet)) { $ready = $true; break }
    Start-Sleep 1
  }
  $results["nvda_init"] = $ready
  if (-not $ready) { Write-Error "NVDA khong init (timeout)"; exit 1 }

  # Cho NVDA lang xuong (log yen 5s) — NVDA moi start con khoi tao ngam
  $stable = 0
  $lastSize = -1
  for ($i = 0; $i -lt 60; $i++) {
    $sz = (Get-Item $log).Length
    if ($sz -eq $lastSize) { $stable++ } else { $stable = 0 }
    $lastSize = $sz
    if ($stable -ge 5) { break }
    Start-Sleep 1
  }

$results["uia_listening"] = ([TkvNvda.Uia]::UiaClientsAreListening() -eq 1)

$formPs = "$logDir/ctl_auto.ps1"
@'
Add-Type -AssemblyName System.Windows.Forms
$f = New-Object System.Windows.Forms.Form
$f.Text = "NvdaCtl"
$f.Width = 300
$f.Height = 200
$f.StartPosition = "CenterScreen"
$b = New-Object System.Windows.Forms.Button
$b.Text = "SaveBtn"
$b.Left = 20; $b.Top = 20; $b.Width = 100
$f.Controls.Add($b)
$t = New-Object System.Windows.Forms.TextBox
$t.Text = "NameBox"
$t.Left = 20; $t.Top = 60; $t.Width = 150
$f.Controls.Add($t)
$f.Show()
Start-Sleep 2
$b.Focus(); Start-Sleep 4
$t.Focus(); Start-Sleep 4
$b.Focus(); Start-Sleep 4
$f.Close()
'@ | Out-File $formPs -Encoding ascii

  $n0 = (Get-Content $log | Measure-Object -Line).Lines
  Start-Process -FilePath powershell.exe -ArgumentList "-NoProfile", "-File", $formPs -WindowStyle Minimized
  Start-Sleep 22
  $newLines = Get-Content $log | Select-Object -Skip $n0 | Out-String
  $results["ctl_title"] = ($newLines -match "'NvdaCtl'")
  $results["ctl_button"] = ($newLines -match "'SaveBtn', 'button'")
  if (-not $results["ctl_button"]) {
    # Retry 1 lan (máy có thể có user active gây nhiễu focus)
    Start-Sleep 5
    $n0b = (Get-Content $log | Measure-Object -Line).Lines
    Start-Process -FilePath powershell.exe -ArgumentList "-NoProfile", "-File", $formPs -WindowStyle Minimized
    Start-Sleep 22
    $newLines = Get-Content $log | Select-Object -Skip $n0b | Out-String
    $results["ctl_retry"] = $true
    if ($newLines -match "'NvdaCtl'") { $results["ctl_title"] = $true }
    if ($newLines -match "'SaveBtn', 'button'") { $results["ctl_button"] = $true }
  }

$n1 = (Get-Content $log | Measure-Object -Line).Lines
& $LiveExe | Out-Null
$newLines2 = Get-Content $log | Select-Object -Skip $n1 | Out-String
$speech2 = ($newLines2 | Select-String "Speaking" -AllMatches).Matches.Count
$results["live_speech_total"] = $speech2
$results["live_widgets"] = ($newLines2 -match "TKVUI|TkvUI|Live.*button|Go.*button")

  Stop-Process -Name nvda -Force -ErrorAction SilentlyContinue
} finally {
  Stop-Process -Name nvda -Force -ErrorAction SilentlyContinue
}

"=== NVDA probe checklist ==="
"nvda_init={0} uia_listening={1}" -f $results["nvda_init"], $results["uia_listening"]
"control: title={0} button={1}" -f $results["ctl_title"], $results["ctl_button"]
"live window: speech_lines={0} widgets_seen={1}" -f $results["live_speech_total"], $results["live_widgets"]
if ($results["nvda_init"] -and $results["uia_listening"] -and $results["ctl_button"]) {
  "NVDA_PROBE_OK"
} else {
  "NVDA_PROBE_FAIL"
  exit 1
}
