# Self-Signed Code Signing Script for AntigravityLauncher.exe

$ErrorActionPreference = "Stop"
$certName = "AntigravityLauncherCert"

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host " 코드 서명(Code Signing) 인증서 발급 및 서명 " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# 1. Look for existing certificate or create a new code signing cert
$cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -match $certName } | Select-Object -First 1

if (-not $cert) {
    Write-Host "[1/3] 새 자체 코드 서명 인증서 생성 중..." -ForegroundColor Yellow
    $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=$certName" -CertStoreLocation "Cert:\CurrentUser\My" -NotAfter (Get-Date).AddYears(5)
} else {
    Write-Host "[1/3] 기존 코드 서명 인증서 사용: $($cert.Thumbprint)" -ForegroundColor Green
}

# 2. Export public certificate to .crt file & add to TrustedPublisher
$tempCertFile = Join-Path $env:TEMP "AntigravityLauncherCert.crt"
Write-Host "[2/3] 신뢰할 수 있는 게시자 저장소 등록..." -ForegroundColor Yellow
[System.IO.File]::WriteAllBytes($tempCertFile, $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert))
certutil -user -addstore -f "TrustedPublisher" $tempCertFile | Out-Null

if (Test-Path $tempCertFile) {
    Remove-Item $tempCertFile -Force -ErrorAction SilentlyContinue
}

# 3. Sign target executables
$targetExes = @(
    "$env:LOCALAPPDATA\Programs\AntigravityLauncher\AntigravityLauncher.exe",
    "$PSScriptRoot\dist\AntigravityLauncher\AntigravityLauncher.exe",
    "C:\Users\aceyo\AntigravityLauncher\dist\AntigravityLauncher\AntigravityLauncher.exe"
)

Write-Host "[3/3] 실행 파일 디지털 서명(Authenticode) 적용 중..." -ForegroundColor Yellow
foreach ($exe in $targetExes) {
    if (Test-Path $exe) {
        $sigResult = Set-AuthenticodeSignature -FilePath $exe -Certificate $cert
        $check = Get-AuthenticodeSignature -FilePath $exe
        Write-Host " - 서명 대상: $exe" -ForegroundColor White
        Write-Host "   서명 상태: $($check.Status) | 서명자: $($check.SignerCertificate.Subject)" -ForegroundColor Green
    }
}

Write-Host "`n===============================================" -ForegroundColor Green
Write-Host " 🎉 코드 서명이 성공적으로 완료되었습니다!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
