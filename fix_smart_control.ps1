# Smart App Control Bypass & Unblock Tool for Antigravity Launcher

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Windows Smart App Control 차단 해결 도구 " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Solution 1: Register Root Certificate in LocalMachine Store
try {
    $cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -match "AntigravityLauncherCert" } | Select-Object -First 1
    if ($cert) {
        Write-Host "[방법 1] 자체 서명 루트 인증서를 LocalMachine 신뢰 기관에 등록..." -ForegroundColor Yellow
        $lmRoot = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "LocalMachine")
        $lmRoot.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
        $lmRoot.Add($cert)
        $lmRoot.Close()
        
        $lmPub = New-Object System.Security.Cryptography.X509Certificates.X509Store("TrustedPublisher", "LocalMachine")
        $lmPub.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
        $lmPub.Add($cert)
        $lmPub.Close()
        Write-Host " -> 인증서 시스템 신뢰 등록 성공!" -ForegroundColor Green
    }
} catch {
    Write-Host " -> (LocalMachine 인증서 등록은 관리자 권한 실행 시 적용됩니다)" -ForegroundColor Gray
}

# Solution 2: Unblock-File on the executable
$exePath = "$env:LOCALAPPDATA\Programs\AntigravityLauncher\AntigravityLauncher.exe"
if (Test-Path $exePath) {
    Write-Host "[방법 2] 실행 파일 보안 차단 속성 해제(Unblock-File)..." -ForegroundColor Yellow
    Unblock-File -Path $exePath -ErrorAction SilentlyContinue
    Write-Host " -> Unblock-File 완료!" -ForegroundColor Green
}

# Solution 3: Create Direct Python Launcher Shortcut (100% SAC Bypass)
Write-Host "[방법 3] Smart App Control 우회용 Python Direct 바로가기 생성..." -ForegroundColor Yellow

$pythonwPath = Join-Path (Split-Path (Get-Command python.exe).Source) "pythonw.exe"
$appScript = "C:\Users\aceyo\antigravity\winluanch\app.py"
$iconPath = "C:\Users\aceyo\antigravity\winluanch\icon.ico"

if ((Test-Path $pythonwPath) -and (Test-Path $appScript)) {
    $DesktopPath = [Environment]::GetFolderPath("Desktop")
    $ShortcutPath = "$DesktopPath\Antigravity Launcher (Direct).lnk"
    
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $pythonwPath
    $Shortcut.Arguments = "`"$appScript`""
    $Shortcut.WorkingDirectory = "C:\Users\aceyo\antigravity\winluanch"
    if (Test-Path $iconPath) {
        $Shortcut.IconLocation = $iconPath
    }
    $Shortcut.Description = "Antigravity CLI Launcher (Direct Python Bypass)"
    $Shortcut.Save()
    
    Write-Host " -> 바탕화면에 'Antigravity Launcher (Direct)' 바로가기 생성 완료!" -ForegroundColor Green
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " 🎉 스마트 앱 컨트롤 차단 해결 작업 완료!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
