@echo off
setlocal

echo ================================
echo Starting HappyRentals Frontend
echo ================================

REM Resolve script directory
set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%frontend"

REM Safety check
if not exist package.json (
    echo ERROR: package.json not found in frontend folder
    pause
    exit /b 1
)

REM Ensure node is available
where node >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not on PATH
    pause
    exit /b 1
)

REM Install deps if missing
if not exist node_modules (
    echo Installing frontend dependencies...
    npm install
    if errorlevel 1 (
        echo ERROR: npm install failed
        pause
        exit /b 1
    )
)

echo Launching Vite dev server...
echo Frontend will open at http://localhost:5173
echo.

REM KEEP WINDOW OPEN
cmd /k npm run dev
