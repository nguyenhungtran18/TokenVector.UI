# Tai HarfBuzz official win64 (license MIT, nguon GitHub release chinh harfbuzz/harfbuzz).
# Lay libharfbuzz-0.dll + libglib-2.0-0.dll + libintl-8.dll, rename bang
# "libharfbuzz.dll" cho khop ten pinvoke trong TkvUI.Bidi.tkv.
#   powershell -ExecutionPolicy Bypass -File tools/fetch_harfbuzz.ps1
param([string]$Version = "14.5.0")
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$tmp = Join-Path $root "build\hb"
$out = Join-Path $root "build"
New-Item -ItemType Directory -Force -Path $tmp, $out | Out-Null
$zip = Join-Path $tmp "hb.zip"
$url = "https://github.com/harfbuzz/harfbuzz/releases/download/$Version/harfbuzz-win64-$Version.zip"
if (-not (Test-Path $zip)) {
    Write-Host "tai $url"
    $ProgressPreference = "SilentlyContinue"
    Invoke-WebRequest -Uri $url -OutFile $zip
}
$ex = Join-Path $tmp "x"
$src = Join-Path $ex "harfbuzz-win64\libharfbuzz-0.dll"
if (-not (Test-Path $src)) {
    Expand-Archive -Force -Path $zip -DestinationPath $ex
}
Copy-Item -Force (Join-Path $ex "harfbuzz-win64\libharfbuzz-0.dll") (Join-Path $out "libharfbuzz.dll")
Copy-Item -Force (Join-Path $ex "harfbuzz-win64\libglib-2.0-0.dll") (Join-Path $out "libglib-2.0-0.dll")
Copy-Item -Force (Join-Path $ex "harfbuzz-win64\libintl-8.dll") (Join-Path $out "libintl-8.dll")
Write-Host "OK: build\libharfbuzz.dll (+ libglib-2.0-0, libintl-8) - HarfBuzz $Version MIT"
