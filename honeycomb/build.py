"""data/*.yml -> web/data.json, the only data the website reads. `--check` fails on drift."""

from __future__ import annotations

import json
import sys

from . import __version__
from .data import ROOT, charter_sha256, load

OUT = ROOT / "web" / "data.json"
SOURCES = ("charter", "honeycomb", "events", "arc", "dimensions", "compass", "boundaries", "strategy")


def render() -> str:
    """Return the JSON text the site reads (stable key order, dates as strings)."""
    payload = {"version": __version__, "charter_sha256": charter_sha256(), **{n: load(n) for n in SOURCES}}
    return json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True, default=str) + "\n"


def main(check: bool = False) -> int:
    """Write web/data.json, or with check=True return 1 if it differs from data/."""
    text = render()
    if check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print("drift: web/data.json is stale; run `make build` and commit it", file=sys.stderr)
            return 1
        print("ok: web/data.json matches data/")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0
