<#
.SYNOPSIS
    One-click local orchestrator for Intentify Universal Cognitive Compiler.
.DESCRIPTION
    Launches the FastAPI backend and Next.js frontend concurrently and opens the browser.
#>

$RootPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $RootPath

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Intentify Universal Cognitive Prompt Compiler" -ForegroundColor White
Write-Host "   100% Local Inference & Zero External AI APIs" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pyVer = & python --version 2>&1
    Write-Host "[✓] Python Environment: $pyVer" -ForegroundColor Green
} catch {
    Write-Host "[X] Python not found. Please install Python 3.11+." -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVer = & node --version 2>&1
    Write-Host "[✓] Node.js Environment: $nodeVer" -ForegroundColor Green
} catch {
    Write-Host "[X] Node.js not found. Please install Node.js 18+." -ForegroundColor Red
    exit 1
}

# Start Backend
Write-Host "`n[1/3] Starting Backend (FastAPI) on http://127.0.0.1:8000..." -ForegroundColor Yellow
$BackendJob = Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd /d `"$RootPath\backend`" && set PYTHONPATH=..;.;../ml-engine && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" -PassThru

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "[2/3] Starting Frontend (Next.js) on http://localhost:3000..." -ForegroundColor Yellow
$FrontendJob = Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd /d `"$RootPath\frontend`" && npm run dev" -PassThru

Start-Sleep -Seconds 2

# Open Browser
Write-Host "[3/3] Opening Intentify in your default browser..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"

Write-Host "`nIntentify is running successfully!" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Swagger:  http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "Press any key to exit this launcher window (services will stay running in their windows)..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
