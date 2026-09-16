# Dong goi TokenVector.UI thanh .nupkg (NuGet) + DLL (.NET assembly tu umbrella).
#
#   powershell -File tools\pack_nupkg.ps1
#
# Buoc:
#   1. Build DLL: bien dich TokenVector.UI.tkv (entry main) thanh assembly .NET
#      (tkvc sinh .exe; exe .NET van tham chieu duoc nhu thu vien, nhung doi chuan
#      la .dll -> chep doi ten thanh TokenVector.UI.dll).
#   2. nuget pack nuget/TokenVector.UI.nuspec (them file DLL vao thu muc pack tam)
#   3. Ket qua: dist/TokenVector.UI.2.1.0.nupkg

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$tkvc = "$env:TKVC"
if (-not $tkvc -or -not (Test-Path $tkvc)) { $tkvc = "D:\TokenVector\3.code\dist\tkvc.exe" }
if (-not (Test-Path $tkvc)) { Write-Host "Khong thay tkvc.exe - dat bien moi truong TKVC" -ForegroundColor Red; exit 2 }

$version = "2.1.0"
$distDir = Join-Path $root "dist"
$pkgStage = Join-Path $root "build\nupkgstage"
New-Item -ItemType Directory -Force -Path $distDir, $pkgStage | Out-Null

# 1. Build DLL tu umbrella (entry main chay ca selftest -> verify kem)
Write-Host "[1/3] Build TokenVector.UI.dll tu umbrella (entry main)..." -ForegroundColor Cyan
$exeOut = Join-Path $pkgStage "TokenVector.UI.exe"
& $tkvc build (Join-Path $root "TokenVector.UI.tkv") --out $exeOut
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $exeOut)) { Write-Host "Build DLL that bai" -ForegroundColor Red; exit 1 }
# .exe .NET la assembly hop le; chuan thu vien la .dll -> chep doi ten
Copy-Item $exeOut (Join-Path $pkgStage "TokenVector.UI.dll") -Force
Write-Host "      -> $($pkgStage)\TokenVector.UI.dll" -ForegroundColor Green

# 2. Them DLL vao stage cua nuspec (nuspec <file src="build\nupkgstage\TokenVector.UI.dll" .../>)
Write-Host "[2/3] nuget pack..." -ForegroundColor Cyan
$nugetCli = "D:\TokenVector\3.code\build\nuget.exe"
if (-not (Test-Path $nugetCli)) { Write-Host "Khong thay nuget.exe tai $nugetCli" -ForegroundColor Red; exit 2 }
& $nugetCli pack (Join-Path $root "nuget\TokenVector.UI.nuspec") -OutputDirectory $distDir -BasePath $root
if ($LASTEXITCODE -ne 0) { Write-Host "nuget pack that bai" -ForegroundColor Red; exit 1 }

# 3. Ket qua
Write-Host "[3/3] Done." -ForegroundColor Cyan
$nupkg = Get-ChildItem -Path $distDir -Filter "TokenVector.UI.*.nupkg" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Write-Host "[SUCCESS] $($nupkg.FullName) ($([math]::Round($nupkg.Length/1KB,1)) KB)" -ForegroundColor Green
Write-Host "De them vao feed: nuget push $($nupkg.Name) -ApiKey <KEY> -Source https://api.nuget.org/v3/index.json" -ForegroundColor Yellow
