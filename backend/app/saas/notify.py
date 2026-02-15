from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Iterable

def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()

def send_email(subject: str, body: str, to_emails: Iterable[str]) -> None:
    host = _env("SMTP_HOST")
    port = int(_env("SMTP_PORT", "587") or "587")
    user = _env("SMTP_USER")
    password = _env("SMTP_PASS")
    from_email = _env("SMTP_FROM", user or "no-reply@happyrentals.local")

    to_list = [e.strip() for e in to_emails if (e or "").strip()]
    if not to_list:
        return

    # Dev fallback: if SMTP not set, just log
    if not host:
        print("EMAIL (dev log):", subject)
        print("TO:", to_list)
        print(body)
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(to_list)
    msg.set_content(body)

    with smtplib.SMTP(host, port, timeout=10) as s:
        s.ehlo()
        if port in (587, 25):
            try:
                s.starttls()
                s.ehlo()
            except Exception:
                pass
        if user and password:
            s.login(user, password)
        s.send_message(msg)
