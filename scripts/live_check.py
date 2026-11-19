"""Fetch the live site and every same-origin asset it names; exit 1 if any is not HTTP 200.

Usage: python3 scripts/live_check.py [base-url]   (default: the URL in data/site.yml)
"""

from __future__ import annotations

import re
import sys
import urllib.request

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def status(url: str) -> int:
    """HTTP status of a GET (0 on network failure)."""
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "honeycomb-live-check"}), timeout=20) as r:
            return r.status
    except Exception:  # noqa: BLE001 - any failure is a red row
        return 0


def main(base: str) -> int:
    """Check the page and its assets; print one row each."""
    base = base.rstrip("/")
    html = urllib.request.urlopen(base + "/", timeout=20).read().decode("utf-8")
    paths = sorted(set(re.findall(r'(?:src|href)="(/[^"#]*)"', html)) | {"/data.json", "/sw.js", "/icon-192.png",
                                                                          "/icon-512.png", "/icon-512-maskable.png"})
    bad = 0
    for p in ["/"] + paths:
        code = status(base + p)
        bad += code != 200
        print(f"{'✓' if code == 200 else '✗'} {code} {base}{p}")
    return 1 if bad else 0


if __name__ == "__main__":
    default = yaml.safe_load((ROOT / "data" / "site.yml").read_text(encoding="utf-8"))["live_url"]
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else default))
