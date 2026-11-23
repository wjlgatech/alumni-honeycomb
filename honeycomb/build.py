"""data/*.yml -> web/data.json, the only data the website reads. `--check` fails on drift."""

from __future__ import annotations

import json
import sys

from . import __version__
from .data import ROOT, charter_sha256, load

OUT = ROOT / "web" / "data.json"
SOURCES = ("charter", "honeycomb", "events", "arc", "dimensions", "compass", "boundaries", "strategy")


def _federation_summary() -> dict:
    """The numbers the site shows from federation/index.json (no cards' text, no seats' detail)."""
    path = ROOT / "federation" / "index.json"
    if not path.exists():
        return {}
    ix = json.loads(path.read_text(encoding="utf-8"))
    return {"as_of": ix["as_of"], "season_now": ix["season_now"], "charter_latest": ix["charter_latest"],
            "simulated": all(h["status"] == "simulated" for h in ix["hives"]),
            "hives": [{k: h[k] for k in ("id", "charter", "heartbeat", "latest_season")} for h in ix["hives"]],
            "learning_cards": len(ix["learnings"]), "open_seats": len(ix["open_seats"]),
            "cross_hive_builds_on": ix["cross_hive_builds_on"], "ripe": [r["tag"] for r in ix["ripe"]]}


def render() -> str:
    """Return the JSON text the site reads (stable key order, dates as strings)."""
    payload = {"version": __version__, "charter_sha256": charter_sha256(), **{n: load(n) for n in SOURCES},
               "federation_index": _federation_summary()}
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
