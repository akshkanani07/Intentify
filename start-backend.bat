@echo off
title Intentify AI - Backend Server
echo ========================================================
echo Starting Intentify AI FastAPI Backend on http://127.0.0.1:8000
echo ========================================================
cd /d C:\intentify\backend
set PYTHONPATH=C:\intentify\backend;C:\intentify\ml-engine
"C:\Python315\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause