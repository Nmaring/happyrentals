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

    # Ensure Python can import bundled source package `app/` when frozen
    if _is_frozen():
        meipass = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        sys.path.insert(0, str(meipass))

    # Used by app/main.py for static mount (works for source + frozen)
    os.environ.setdefault("STATIC_DIR", str(bundle_path("static")))

    from app.main import app as fastapi_app

    url = f"http://127.0.0.1:{port}/"
    health_url = f"http://127.0.0.1:{port}/api/health"

    threading.Thread(
        target=open_browser_when_ready, args=(url, health_url), daemon=True
    ).start()

    try:
        uvicorn.run(
            fastapi_app,
            host="127.0.0.1",
            port=port,
            log_level="info",
        )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
