"""Sign in to the private room everywhere at once: this Mac's own browser opens the room signed in, and a QR on screen
signs the phone in. Both last 30 days. The passphrase is found by honeycomb/owner.py (no prompts) and never printed;
the QR page is a private temp file deleted 60 seconds later.

    python3 scripts/signin_qr.py        # or: make signin
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time

ROOM = "https://futuremake.io/honeycomb/room.html"
DAYS = 30
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from honeycomb.owner import mint_session, secret as owner_secret  # noqa: E402


def qr_page(url: str) -> str:
    """A tiny local page that draws the QR (qrcodejs from cdnjs) with a do-not-share note."""
    return ("<!doctype html><meta charset=utf-8><title>Honeycomb sign-in QR</title>"
            "<style>body{font:18px system-ui;display:grid;place-items:center;min-height:95vh;background:#faf9f5;"
            "color:#141413;text-align:center}#q{padding:16px;background:#fff;border-radius:12px}</style>"
            f"<div><h2>Scan with your phone camera</h2><div id=q></div><p>Signs your phone into the Honeycomb Room for "
            f"{DAYS} days. This Mac's browser is already signed in. Close this tab after scanning; don't screenshot or share it.</p></div>"
            "<script src=\"https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js\"></script>"
            f"<script>new QRCode(document.getElementById('q'),{{text:{json.dumps(url)},width:320,height:320}});document.querySelector('#q').removeAttribute('title');</script>")


def main() -> int:
    """Mint, show, then remove the QR page."""
    secret = owner_secret()
    if not secret:
        print("No owner passphrase on this Mac (env, agentic-portfolio/.env.local, or the keychain).", file=sys.stderr)
        return 1
    url = f"{ROOM}?owner={mint_session(secret, int(time.time() * 1000), DAYS)}"
    subprocess.run(["open", url], check=False)  # this Mac's default browser: the room, signed in
    fd, path = tempfile.mkstemp(suffix=".html", prefix="honeycomb-signin-")
    with os.fdopen(fd, "w") as fh:
        fh.write(qr_page(url))
    subprocess.run(["open", path], check=False)
    print("The room is open in your browser, signed in. Scan the QR for the phone within 60 seconds.")
    time.sleep(60)
    os.remove(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
