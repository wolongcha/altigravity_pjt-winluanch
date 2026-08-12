# Antigravity Launcher Automated Installation Script

$ErrorActionPreference = "Stop"

$InstallDir = "$env:LOCALAPPDATA\Programs\AntigravityLauncher"
$BuildDir = "$PSScriptRoot\dist\AntigravityLauncher"

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host " Antigravity CLI Launcher 설치 프로그램 " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

if (-not (Test-Path $BuildDir)) {
    Write-Error "빌드 폴더를 찾을 수 없습니다: $BuildDir. 먼저 build_exe.py를 실행하세요."
}

# 1. Target Folder Setup
Write-Host "[1/4] 설치 디렉토리 준비 중: $InstallDir" -ForegroundColor Yellow
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

# Copy files
Write-Host "[2/4] 프로그램 파일 복사 중..." -ForegroundColor Yellow
Copy-Item -Path "$BuildDir\*" -Destination $InstallDir -Recurse -Force

$ExePath = "$InstallDir\AntigravityLauncher.exe"

# Code Signing
$SignScript = "$PSScriptRoot\sign_exe.ps1"
if (Test-Path $SignScript) {
    & $SignScript
}

# 2. Desktop Shortcut
Write-Host "[3/4] 바탕화면 바로가기 생성 중..." -ForegroundColor Yellow
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$DesktopLnk = "$DesktopPath\Antigravity Launcher.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($DesktopLnk)
$Shortcut.TargetPath = $ExePath
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "Antigravity CLI Session & Session Launcher"
$Shortcut.Save()

# 3. Start Menu Shortcut
Write-Host "[4/4] 시작 메뉴 바로가기 생성 중..." -ForegroundColor Yellow
$StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
$StartMenuLnk = "$StartMenuPath\Antigravity Launcher.lnk"

$ShortcutStart = $WshShell.CreateShortcut($StartMenuLnk)
$ShortcutStart.TargetPath = $ExePath
$ShortcutStart.WorkingDirectory = $InstallDir
$ShortcutStart.Description = "Antigravity CLI Session & Session Launcher"
$ShortcutStart.Save()

Write-Host "`n===============================================" -ForegroundColor Green
Write-Host " 🎉 설치가 완료되었습니다!" -ForegroundColor Green
Write-Host " - 실행 파일: $ExePath" -ForegroundColor White
Write-Host " - 바탕화면 바로가기: Antigravity Launcher" -ForegroundColor White
Write-Host " - 시작 메뉴 바로가기: Antigravity Launcher" -ForegroundColor White
Write-Host "===============================================" -ForegroundColor Green
