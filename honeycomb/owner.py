"""The futuremake.io owner credential on this Mac, without prompts: find the passphrase, mint a signed session.

Order: HONEYCOMB_OWNER_TOKEN / PORTFOLIO_OWNER_TOKEN env → agentic-portfolio's .env.local next to this repo (already on
this Mac, no prompt) → the login keychain (futuremake.io / owner; macOS may ask once). Never printed.
The session format matches agentic-portfolio lib/owner.ts: sess.<expMs>.<hex hmac-sha256("sess.<expMs>", passphrase)>.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import subprocess

from .data import ROOT

ENV_LOCAL = ROOT.parent / "agentic-portfolio" / ".env.local"


def secret() -> str:
    """The owner passphrase, or '' if this Mac doesn't have it."""
    for k in ("HONEYCOMB_OWNER_TOKEN", "PORTFOLIO_OWNER_TOKEN"):
        if os.environ.get(k):
            return os.environ[k]
    if ENV_LOCAL.exists():
        for line in ENV_LOCAL.read_text(encoding="utf-8").splitlines():
            if line.startswith("PORTFOLIO_OWNER_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"')
    r = subprocess.run(["security", "find-internet-password", "-s", "futuremake.io", "-a", "owner", "-w"],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def mint_session(key: str, now_ms: int, days: int = 30) -> str:
    """A signed session accepted by the owner gate for `days` days."""
    exp = now_ms + days * 24 * 3600 * 1000
    return f"sess.{exp}.{hmac.new(key.encode(), f'sess.{exp}'.encode(), hashlib.sha256).hexdigest()}"
