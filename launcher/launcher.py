import subprocess
import sys
import os
import time
import webbrowser

print("=== HappyRentals Launcher Started ===")

# -------------------------------
# Resolve REAL install directory
# -------------------------------
if getattr(sys, 'frozen', False):
    # Running as EXE
    EXE_DIR = os.path.dirname(sys.executable)
else:
    # Running as python script
    EXE_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = os.path.abspath(os.path.join(EXE_DIR, ".."))

BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

PYTHON_EXE = os.path.join(BACKEND_DIR, ".venv", "Scripts", "python.exe")

print("EXE_DIR    =", EXE_DIR)
print("ROOT_DIR   =", ROOT_DIR)
print("BACKEND_DIR=", BACKEND_DIR)
print("FRONTEND_DIR=", FRONTEND_DIR)
print("PYTHON_EXE =", PYTHON_EXE)

# -------------------------------
# Validation
# -------------------------------
if not os.path.exists(PYTHON_EXE):
    print("❌ Backend venv python not found")
    input("Press Enter to exit")
    sys.exit(1)

if not os.path.exists(os.path.join(FRONTEND_DIR, "package.json")):
    print("❌ Frontend package.json not found")
    input("Press Enter to exit")
    sys.exit(1)

print("✅ Paths validated")

# -------------------------------
# Start Backend
# -------------------------------
print("Starting backend...")
backend = subprocess.Popen(
    [
        PYTHON_EXE,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
    ],
    cwd=BACKEND_DIR,
)

time.sleep(4)
if backend.poll() is not None:
    print("❌ Backend failed to start")
    input("Press Enter to exit")
    sys.exit(1)

print("✅ Backend running on http://127.0.0.1:8000")

# -------------------------------
# Start Frontend
# -------------------------------
print("Starting frontend...")
npm_cmd = "npm.cmd" if sys.platform.startswith("win") else "npm"

frontend = subprocess.Popen(
    [npm_cmd, "run", "dev"],
    cwd=FRONTEND_DIR,
)

time.sleep(6)
if frontend.poll() is not None:
    print("❌ Frontend failed to start")
    input("Press Enter to exit")
    sys.exit(1)

print("✅ Frontend running")

# -------------------------------
# Open Browser
# -------------------------------
webbrowser.open("http://localhost:5173")

print("🚀 HappyRentals is running")
input("Press Enter to close launcher (services keep running)")
