@echo off
TITLE Intentify Universal Cognitive Compiler
COLOR 0B

echo ========================================================
echo    Intentify Universal Cognitive Prompt Compiler
echo    100%% Local Inference & Zero External AI APIs
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH. Please install Python 3.11+.
    pause
    exit /b 1
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found in PATH. Please install Node.js 18+.
    pause
    exit /b 1
)

echo [2/3] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "Intentify Backend Service" cmd /k "cd /d "%~dp0backend" && set PYTHONPATH=..;.;../ml-engine && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo Waiting for Backend service to initialize...
timeout /t 3 /nobreak >nul

echo [3/3] Launching Next.js Frontend on http://localhost:3000 ...
start "Intentify Frontend Service" cmd /k "cd /d "%~dp0frontend" && npm run dev"

timeout /t 2 /nobreak >nul
echo Opening Intentify in your default web browser...
start http://localhost:3000

echo.
echo ========================================================
echo Intentify is running!
echo   Frontend: http://localhost:3000
echo   API Docs: http://127.0.0.1:8000/docs
echo Close the respective terminal windows to terminate.
echo ========================================================
pause
