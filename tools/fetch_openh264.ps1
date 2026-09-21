<#
.SYNOPSIS
    Tai OpenH264 DLL chinh chu Cisco (khong build, khong GPL).
    Chay: powershell -ExecutionPolicy Bypass -File tools/fetch_openh264.ps1
    Ket qua: build/openh264-win64.dll (import boi .gitignore, khong commit).

    Tai sao phai la binary cua Cisco: chi binary do Cisco phan phoi moi duoc
    Cisco tra MPEG-LA royalties (xem docs/OPENH264.md). Build tu source thi
    tu chiu trach nhiem license. x264 TUYET DOI khong dung (GPL).
#>
param(
    [string]$Version = "2.6.0",
    [string]$OutDir = "build"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }

$url = "https://ciscobinary.openh264.org/openh264-$Version-win64.dll.bz2"
$bz2 = Join-Path $OutDir "openh264-win64.dll.bz2"
$dll = Join-Path $OutDir "openh264-win64.dll"
Write-Host "GET $url"
curl.exe -sL --max-time 120 -o $bz2 $url
if (-not (Test-Path $bz2)) { Write-Error "tai that bai"; exit 1 }

# Giai nen bang Python (bz2) - khong can tool ngoai
& python3 -c "import bz2; open(r'$dll','wb').write(bz2.decompress(open(r'$bz2','rb').read())); print('extract ok')"
$fi = Get-Item $dll
if ($fi.Length -lt 500000) { Write-Error "file qua nho, nghi ngo ($($fi.Length))"; exit 1 }
$mz = [System.IO.File]::ReadAllBytes($dll)[0..1]
if ($mz[0] -ne 77 -or $mz[1] -ne 90) { Write-Error "khong phai PE (MZ)"; exit 1 }

# Verify exports can ban (strings trong .edata)
$bytes = [System.IO.File]::ReadAllBytes($dll)
$text = [System.Text.Encoding]::ASCII.GetString($bytes)
foreach ($fn in @("WelsCreateDecoder", "WelsCreateSVCEncoder", "WelsDestroyDecoder")) {
    if ($text -notmatch $fn) { Write-Error "thieu export $fn"; exit 1 }
    Write-Host "export ok: $fn"
}
Write-Host "OPENH264_OK ($dll, $($fi.Length) bytes)"
