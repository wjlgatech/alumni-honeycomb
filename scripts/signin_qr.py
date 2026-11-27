"""Show a sign-in QR for the private room on THIS Mac's screen: scan it and the phone is signed in for 30 days.

The owner passphrase is read from the login keychain (server futuremake.io, account owner) or HONEYCOMB_OWNER_TOKEN,
turned into a signed 30-day session (same HMAC as agentic-portfolio lib/owner.ts), and never printed. The QR page is
written to a private temp file, opened, and deleted 30 seconds later.

    python3 scripts/signin_qr.py        # or: make signin
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import subprocess
import sys
import tempfile
import time

ROOM = "https://futuremake.io/honeycomb/room.html"
DAYS = 30


def owner_secret() -> str:
    """The futuremake.io owner passphrase from the environment or the macOS login keychain; '' if neither has it."""
    if os.environ.get("HONEYCOMB_OWNER_TOKEN"):
        return os.environ["HONEYCOMB_OWNER_TOKEN"]
    r = subprocess.run(["security", "find-internet-password", "-s", "futuremake.io", "-a", "owner", "-w"],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def mint_session(secret: str, now_ms: int, days: int = DAYS) -> str:
    """A signed session `sess.<expMs>.<hex hmac-sha256(sess.<expMs>, secret)>`, accepted by the owner gate."""
    exp = now_ms + days * 24 * 3600 * 1000
    return f"sess.{exp}.{hmac.new(secret.encode(), f'sess.{exp}'.encode(), hashlib.sha256).hexdigest()}"


def qr_page(url: str) -> str:
    """A tiny local page that draws the QR (qrcodejs from cdnjs) with a do-not-share note."""
    return ("<!doctype html><meta charset=utf-8><title>Honeycomb sign-in QR</title>"
            "<style>body{font:18px system-ui;display:grid;place-items:center;min-height:95vh;background:#faf9f5;"
            "color:#141413;text-align:center}#q{padding:16px;background:#fff;border-radius:12px}</style>"
            f"<div><h2>Scan with your phone camera</h2><div id=q></div><p>Signs your phone into the Honeycomb Room for "
            f"{DAYS} days. Close this tab after scanning; don't screenshot or share it.</p></div>"
            "<script src=\"https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js\"></script>"
            f"<script>new QRCode(document.getElementById('q'),{{text:{json.dumps(url)},width:320,height:320}});</script>")


def main() -> int:
    """Mint, show, then remove the QR page."""
    secret = owner_secret()
    if not secret:
        print("No owner passphrase found: add it to the login keychain (server futuremake.io, account owner) "
              "or set HONEYCOMB_OWNER_TOKEN.", file=sys.stderr)
        return 1
    url = f"{ROOM}?owner={mint_session(secret, int(time.time() * 1000))}"
    fd, path = tempfile.mkstemp(suffix=".html", prefix="honeycomb-signin-")
    with os.fdopen(fd, "w") as fh:
        fh.write(qr_page(url))
    subprocess.run(["open", path], check=False)
    print(f"QR is on your screen. Scan it within 30 seconds; the page is then deleted.")
    time.sleep(30)
    os.remove(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
