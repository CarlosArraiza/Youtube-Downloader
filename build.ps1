# Compila la app (PyInstaller) y el instalador (Inno Setup) con la versión de src\version.py.
# Uso: .\build.ps1   ->  installer_output\YouTubeDownloader-Setup-vX.Y.Z.exe
# Sin $ErrorActionPreference = "Stop": en Windows PowerShell 5.1 convierte en error lo que
# PyInstaller escribe por stderr (sus mensajes INFO). Los fallos se miran con $LASTEXITCODE.
Set-Location $PSScriptRoot

$match = Select-String -Path "src\version.py" -Pattern '__version__\s*=\s*"([^"]+)"'
if (-not $match) { throw "No encuentro __version__ en src\version.py" }
$version = $match.Matches[0].Groups[1].Value
Write-Host "Versión $version"

$iscc = @(
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) { throw "No encuentro ISCC.exe (Inno Setup 6)" }

& .\venv\Scripts\python.exe -m PyInstaller --noconfirm --clean YouTubeDownloader.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller ha fallado" }

& $iscc "/DMyAppVersion=$version" installer.iss
if ($LASTEXITCODE -ne 0) { throw "Inno Setup ha fallado" }

$setup = "installer_output\YouTubeDownloader-Setup-v$version.exe"
Write-Host "Instalador: $setup"
Write-Host "SHA-256:    $((Get-FileHash $setup -Algorithm SHA256).Hash.ToLower())"
