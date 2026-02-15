param(
  [switch]$Run
)

$ErrorActionPreference = "Stop"

function WriteFileUtf8($path, $content) {
  $dir = Split-Path -Parent $path
  if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
  Set-Content -Path $path -Value $content -Encoding UTF8 -Force
}

$Root     = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Frontend = Join-Path $Root "frontend"
$Backend  = Join-Path $Root "backend"

if (!(Test-Path $Frontend)) { throw "Missing folder: $Frontend" }
if (!(Test-Path $Backend))  { throw "Missing folder: $Backend" }

Write-Host "=== HappyRentals Windows EXE Build ==="
Write-Host "Root:     $Root"
Write-Host "Frontend: $Frontend"
Write-Host "Backend:  $Backend"
Write-Host ""

# 1) Write backend/run_happyrentals.py (launcher)
$runPy = @"
from __future__ import annotations

import os
import sys
import time
import socket
import threading
import webbrowser
import urllib.request
from pathlib import Path

import uvicorn


def _is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False)) and hasattr(sys, "_MEIPASS")


def bundle_path(*parts: str) -> Path:
    # PyInstaller: data lives under sys._MEIPASS
    if _is_frozen():
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent  # backend/
    return base.joinpath(*parts)


def pick_free_port(default: int = 8000) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", default))
            return default
        except OSError:
            s.bind(("127.0.0.1", 0))
            return int(s.getsockname()[1])


def open_browser_when_ready(url: str, health_url: str) -> None:
    deadline = time.time() + 25.0
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(health_url, timeout=0.75) as resp:
                if 200 <= resp.status < 300:
                    webbrowser.open(url)
                    return
        except Exception:
            time.sleep(0.25)
    webbrowser.open(url)


def main() -> None:
    port = int(os.getenv("PORT", "0")) or pick_free_port(8000)

    # Ensure FastAPI can find the built UI when frozen
    os.environ.setdefault("STATIC_DIR", str(bundle_path("static")))

    url = f"http://127.0.0.1:{port}/"
    health_url = f"http://127.0.0.1:{port}/api/health"

    threading.Thread(
        target=open_browser_when_ready, args=(url, health_url), daemon=True
    ).start()

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
"@

WriteFileUtf8 (Join-Path $Backend "run_happyrentals.py") $runPy
Write-Host "Wrote: backend/run_happyrentals.py"

# 2) Write backend/app/spa_static.py (mounts static + adds /api/health)
$spaPy = @"
from __future__ import annotations

import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles


def mount_spa(app) -> None:
    \"\"\"Mount SPA static assets with HTML fallback, and provide /api/health.\"\"\"

    @app.get("/api/health")
    def health():
        return {"ok": True}

    static_dir = os.getenv("STATIC_DIR")
    if static_dir:
        static_path = Path(static_dir)
    else:
        # backend/app/... -> backend/static
        static_path = Path(__file__).resolve().parents[1] / "static"

    if static_path.exists():
        # IMPORTANT: mount after /api routes are registered in main.py
        app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")
"@

WriteFileUtf8 (Join-Path $Backend "app\spa_static.py") $spaPy
Write-Host "Wrote: backend/app/spa_static.py"

# 3) Patch backend/app/main.py to call mount_spa(app) at the end (safe append)
$mainPath = Join-Path $Backend "app\main.py"
if (!(Test-Path $mainPath)) { throw "Missing file: $mainPath" }

$main = Get-Content $mainPath -Raw
if ($main -notmatch "mount_spa\s*\(") {
  $patch = @"

# --- Auto-added: SPA static mount + /api/health ---
from app.spa_static import mount_spa
mount_spa(app)
"@
  Add-Content -Path $mainPath -Value $patch -Encoding UTF8
  Write-Host "Patched: backend/app/main.py (appended mount_spa(app))"
} else {
  Write-Host "Skipped patch: backend/app/main.py already references mount_spa()"
}

# 4) Build frontend (Vite)
Push-Location $Frontend
try {
  Write-Host ""
  Write-Host "=== Building frontend ==="
  if (Test-Path "package-lock.json") {
    npm ci
  } else {
    npm install
  }
  npm run build
} finally {
  Pop-Location
}

# 5) Copy frontend/dist -> backend/static
$distPath   = Join-Path $Frontend "dist"
$staticPath = Join-Path $Backend "static"

if (!(Test-Path $distPath)) { throw "Missing frontend dist output: $distPath (did build fail?)" }

Write-Host ""
Write-Host "=== Copying frontend dist to backend/static ==="
Remove-Item $staticPath -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $staticPath | Out-Null
Copy-Item (Join-Path $distPath "*") $staticPath -Recurse -Force
Write-Host "Copied dist -> backend/static"

# 6) Build PyInstaller EXE
Push-Location $Backend
try {
  Write-Host ""
  Write-Host "=== Building Windows EXE (PyInstaller) ==="
  python -m pip install -U pyinstaller | Out-Null
  # Clean old builds
  Remove-Item ".\build" -Recurse -Force -ErrorAction SilentlyContinue
  Remove-Item ".\dist"  -Recurse -Force -ErrorAction SilentlyContinue
  Remove-Item ".\HappyRentals.spec" -Force -ErrorAction SilentlyContinue
  python -m PyInstaller `
    --noconfirm `
    --clean `
    --name HappyRentals `
    --onefile `
    --console `
    --paths "." `
    --add-data "static;static" `
    --collect-submodules uvicorn `
    --collect-submodules fastapi `
    run_happyrentals.py

} finally {
  Pop-Location
}

# 7) Copy EXE to release/
$exe = Join-Path $Backend "dist\HappyRentals.exe"
if (!(Test-Path $exe)) { throw "Build failed: EXE not found at $exe" }

$releaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force $releaseDir | Out-Null
Copy-Item $exe (Join-Path $releaseDir "HappyRentals.exe") -Force

# Add a tiny README
$readme = @"
HappyRentals
- Run: HappyRentals.exe
- Opens browser automatically
- API base: /api
"@
WriteFileUtf8 (Join-Path $releaseDir "README.txt") $readme

Write-Host ""
Write-Host "✅ Done!"
Write-Host "EXE: $(Join-Path $releaseDir "HappyRentals.exe")"

if ($Run) {
  Write-Host "Launching..."
  Start-Process (Join-Path $releaseDir "HappyRentals.exe")
}




