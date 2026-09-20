<#
.SYNOPSIS
    TkvUI Benchmark Suite - Cross-platform benchmark driver
    Chạy: .\tools\bench_all.ps1

.NOTES
    Tương đương tools/bench_all.sh cho Windows PowerShell
    Cần: tkvc.exe, python3, PyQt6 (đối chứng)
#>

param(
    [string]$TKVC = "D:\TokenVector\3.code\dist\tkvc.exe",
    [string]$OutDir = "build\bench"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$OUTDIR = $OutDir
if (-not (Test-Path $OUTDIR)) {
    New-Item -ItemType Directory -Force -Path $OUTDIR | Out-Null
}

Write-Host "=== TkvUI Benchmark Suite ===" -ForegroundColor Cyan
Write-Host "Build + run all benchmarks..." -ForegroundColor Gray

$TKVC = Resolve-Path $TKVC
if (-not (Test-Path $TKVC)) {
    Write-Error "Khong tim thay tkvc.exe: $TKVC"
    exit 1
}

$OUTDIR_FULL = Resolve-Path $OUTDIR

function Run-Benchmark {
    param(
        [string]$Name,
        [string]$Source,
        [string]$Entry,
        [string]$OutExe
    )
    Write-Host "[$Name] Building..." -ForegroundColor Yellow
    & $TKVC build $Source --entry $Entry --out $OutExe | Out-Null
    if (-not (Test-Path $OutExe)) {
        Write-Error "Build failed: $OutExe"
        exit 1
    }
    Write-Host "[$Name] Running..." -ForegroundColor Green
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    & $OutExe
    $sw.Stop()
    Write-Host "[$Name] Done in $($sw.ElapsedMilliseconds) ms" -ForegroundColor Green
}

# 1. Text render bench (std: 400 dong x 54 ky tu, 5 reps)
Write-Host "`n[1/7] Text render bench..." -ForegroundColor Cyan
Run-Benchmark -Name "TextRender" `
    -Source "examples/TkvUI.BenchText.tkv" `
    -Entry "bench_text_block" `
    -OutExe "$OUTDIR/bench_text.exe"

# 2. Widget creation + render bench (std: 1000 nut, construct x100 + render x20)
Write-Host "`n[2/7] Widget creation bench..." -ForegroundColor Cyan
Run-Benchmark -Name "WidgetCreate" `
    -Source "examples/TkvUI.BenchWidgets.tkv" `
    -Entry "bench_widgets_create" `
    -OutExe "$OUTDIR/bench_widgets.exe"

# 3. CRUD bench (std: 10 reps x 1000 rows, fresh table/rep, in-memory)
Write-Host "`n[3/7] CRUD bench..." -ForegroundColor Cyan
Run-Benchmark -Name "CRUD" `
    -Source "examples/TkvUI.CrudBench.tkv" `
    -Entry "bench_run" `
    -OutExe "$OUTDIR/crudbench.exe"

# 3b. CRUD persist bench (P1: file-backed TKVSQL1 dual-slot)
Write-Host "`n[3b/7] CRUD persist bench..." -ForegroundColor Cyan
Run-Benchmark -Name "CRUDPersist" `
    -Source "examples/TkvUI.CrudBench.tkv" `
    -Entry "bench_persist" `
    -OutExe "$OUTDIR/persistbench.exe"

# 4. PyQt6 baseline chuan hoa (cung workload, cung reps)
Write-Host "`n[4/7] PyQt6 baseline..." -ForegroundColor Cyan
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $env:QT_QPA_PLATFORM = "offscreen"
    & python3 tools/bench/bench_text_pyqt.py
    & python3 tools/bench/bench_widgets_pyqt.py
    & python3 tools/bench/crud_pyqt_bench_mem.py
} else {
    Write-Host "SKIP: python3 not found" -ForegroundColor Gray
}

# 5. Memory bench (std: peak RSS cung workload text 108K chars)
Write-Host "`n[5/7] Memory bench..." -ForegroundColor Cyan
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    & python3 tools/bench/bench_mem.py "$OUTDIR_FULL/bench_text.exe"
    & python3 tools/bench/bench_mem.py python3 tools/bench/bench_text_pyqt.py
} else {
    Write-Host "SKIP: python3 not found" -ForegroundColor Gray
}

# 6. Live demo (khong phai bench so gang)
Write-Host "`n[6/7] Live demo..." -ForegroundColor Cyan
Run-Benchmark -Name "LiveMem" `
    -Source "examples/TkvUI.Live.tkv" `
    -Entry "run_live" `
    -OutExe "$OUTDIR/live_mem.exe"

Write-Host "`n=== Done ===" -ForegroundColor Green
Write-Host "Kết quả ghi trong docs/BENCH.md (cập nhật thủ công sau khi chạy)" -ForegroundColor Gray