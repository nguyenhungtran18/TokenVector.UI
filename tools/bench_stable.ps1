<#
.SYNOPSIS
    P3-B3: bench stability gate (Windows twin cua tools/bench_stable.sh).
    Chay: powershell -ExecutionPolicy Bypass -File tools/bench_stable.ps1
#>
param(
    [string]$TKVC = "D:\TokenVector\3.code\dist\tkvc.exe",
    [string]$OutDir = "build\bench"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }

Write-Host "=== build benches (1 lan) ==="
& $TKVC build examples/TkvUI.BenchText.tkv --entry bench_text_block --out "$OutDir/bench_text.exe"
& $TKVC build examples/TkvUI.BenchWidgets.tkv --entry bench_widgets_create --out "$OutDir/bench_widgets.exe"
& $TKVC build examples/TkvUI.CrudBench.tkv --entry bench_run --out "$OutDir/crudbench.exe"

Write-Host "=== stability gates (3 lan/bench) ==="
$fail = 0
& python3 tools/bench_stats.py --repeat 3 --metric text_atlas --pattern 'atlas_ms=(\d+)' --unit ms --lt 100 --tol-abs 32 -- "$OutDir/bench_text.exe"
if ($LASTEXITCODE -ne 0) { $fail = 1 }
& python3 tools/bench_stats.py --repeat 3 --metric widgets_render --pattern 'render_ms=(\d+)' --unit ms --lt 900 --tol-abs 64 -- "$OutDir/bench_widgets.exe"
if ($LASTEXITCODE -ne 0) { $fail = 1 }
& python3 tools/bench_stats.py --repeat 3 --metric crud_total --pattern 'TOTAL avg/rep: (\d+)ms' --unit ms --lt 20 --tol-abs 16 -- "$OutDir/crudbench.exe"
if ($LASTEXITCODE -ne 0) { $fail = 1 }

if ($fail -ne 0) { Write-Host "BENCH_STABLE_FAIL"; exit 1 }
Write-Host "BENCH_STABLE_OK"
