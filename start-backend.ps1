# Intentify AI - Backend Server Startup Script
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting Intentify AI FastAPI Backend on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

Set-Location C:\intentify\backend
$env:PYTHONPATH="C:\intentify\backend;C:\intentify\ml-engine"
& "C:\Python315\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload