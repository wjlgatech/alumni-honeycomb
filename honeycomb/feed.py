"""A hive's PUBLIC feed: what crosses from one school to the federation. Numbers, learnings, open seats; never people.

The analogy: each restaurant in a chain keeps its staff list in the back office, and sends head office only
its weekly numbers, its new tested recipe cards, and the shifts it still needs to fill.

    feed = {schema, hive, charter, as_of, seasons, latest_season, pulse, learnings[], open_seats[]}

`as_of` is derived from the hive's own data (latest check-in or season start), so the feed is
deterministic and can be drift-gated like web/data.json.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from typing import Any

from . import pulse
from .data import ROLE_KEYS, load

SCHEMA = "ah-feed/1"


def season_of(day: dt.date) -> str:
    """The federation clock: calendar quarters, `YYYY-S1` (Jan-Mar) .. `YYYY-S4` (Oct-Dec)."""
    return f"{day.year}-S{(day.month - 1) // 3 + 1}"


def previous_season(season: str) -> str:
    """The season before `season` on the federation clock."""
    year, q = int(season[:4]), int(season[-1])
    return f"{year - 1}-S4" if q == 1 else f"{year}-S{q - 1}"


def _date(v: Any) -> dt.date:
    """Accept a date or an ISO string."""
    return v if isinstance(v, dt.date) else dt.date.fromisoformat(str(v))


def as_of(hive: dict[str, Any]) -> str:
    """The latest date the hive's own data mentions (check-ins and season starts)."""
    days = [_date(c["date"]) for c in hive["checkins"]] + [_date(s["start"]) for s in hive["seasons"]]
    return max(days).isoformat() if days else "1970-01-01"


def learning_card(hive_id: str, cell: dict[str, Any]) -> dict[str, Any]:
    """A closed cell, as a card another hive can build on. Id = `<hive>/<cell>`; no people."""
    out = cell.get("outcome") or {}
    return {"id": f"{hive_id}/{cell['id']}", "hive": hive_id, "season": cell.get("season"),
            "tags": list(cell.get("tags") or []), "vision": cell.get("vision", ""), "good": cell.get("good", ""),
            "evidence": out.get("evidence", ""), "learned": out.get("learned", ""),
            "builds_on": list(cell.get("builds_on") or [])}


def open_seat(hive_id: str, cell: dict[str, Any], model: dict[str, Any]) -> dict[str, Any] | None:
    """A forming cell's empty seats (how many of each role it still needs), or None if it is full."""
    needs = {key: max(0, model["cell"][key]["min"] - len(cell.get(key) or [])) for key, _ in ROLE_KEYS}
    if not any(needs.values()):
        return None
    return {"id": f"{hive_id}/{cell['id']}", "hive": hive_id, "season": cell.get("season"),
            "tags": list(cell.get("tags") or []), "vision": cell.get("vision", ""), "needs": needs}


def build_feed(hive: dict[str, Any]) -> dict[str, Any]:
    """The public feed for one hive (see module docstring)."""
    meta, model = hive["hive"], load("honeycomb")
    cells = hive["cells"]
    seats = [open_seat(meta["id"], c, model) for c in cells if c.get("status") == "forming"]
    numbers = pulse.pulse(hive)
    return {"schema": SCHEMA, "hive": meta["id"], "simulated": bool(meta.get("simulated")),
            "charter": meta.get("charter", {}), "as_of": as_of(hive),
            "seasons": [s["id"] for s in hive["seasons"]], "latest_season": numbers["season"], "pulse": numbers,
            "learnings": [learning_card(meta["id"], c) for c in cells if c.get("status") == "closed"],
            "open_seats": [s for s in seats if s]}


def leaks(feed: dict[str, Any], hive: dict[str, Any]) -> list[str]:
    """Member ids or names that appear anywhere in the feed text (must be empty before publishing)."""
    text = json.dumps(feed, ensure_ascii=False)
    found = []
    for m in hive["members"]:
        for token in (m.get("id"), m.get("name"), str(m.get("name", "")).replace(" (sim)", "")):
            if token and len(token) > 2 and re.search(r"\b" + re.escape(token) + r"\b", text):
                found.append(f"{m['id']}: '{token}' appears in the feed")
                break
    return found


def render(feed: dict[str, Any]) -> str:
    """Stable JSON text for a feed (sorted keys, trailing newline)."""
    return json.dumps(feed, ensure_ascii=False, indent=1, sort_keys=True, default=str) + "\n"
