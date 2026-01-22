\
@echo off
setlocal enabledelayedexpansion
cd /d %~dp0\backend

if not exist ".venv\Scripts\python.exe" (
  echo [backend] Creating venv...
  py -3.11 -m venv .venv 2>nul || python -m venv .venv
)

call ".venv\Scripts\activate.bat"
echo [backend] Installing requirements...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt

if not exist ".env" (
  copy ".env.example" ".env" >nul
)

echo [backend] Starting FastAPI on http://127.0.0.1:8000 ...
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
