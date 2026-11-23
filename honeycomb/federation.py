"""The federation: hives that signed the same charter, kept in step without a headquarters.

Three verbs, each a function here (research and rationale: docs/FEDERATION.md):
    synchronize  one clock (feed.season_of) + a heartbeat: each hive's feed must name the current or previous season
    harmonize    one feed schema + one charter, verified by SHA-256; an older ratified charter is allowed but flagged
    compound     closed cells become learning cards; cards that build on another hive's card are counted; a tag
                 seen in 3+ cards from 2+ hives becomes a DRAFT proposal (the steward drafts; hives decide)

Web3 ideas without a chain or a token: the protocol is a file anyone can fork; membership is a verifiable
hash; each hive owns its data and publishes only its feed; changes need 2/3 of hives; exit is always open.
"""

from __future__ import annotations

import json
import urllib.request
from collections import defaultdict
from fractions import Fraction
from typing import Any

from .data import ROOT, charter_sha256, load
from .feed import previous_season, season_of
import datetime as dt

QUORUM = Fraction(2, 3)
FOUNDING_UNTIL_HIVES = 3
RIPE_CARDS, RIPE_HIVES = 3, 2
INDEX = ROOT / "federation" / "index.json"


def known_hashes(registry: dict[str, Any]) -> dict[str, str]:
    """version -> sha256 for every charter the federation has ratified."""
    return {str(c["version"]): c["sha256"] for c in registry.get("charters", [])}


def latest_version(registry: dict[str, Any]) -> str:
    """The newest ratified charter version (semantic-version order)."""
    return max(known_hashes(registry), key=lambda v: tuple(int(x) for x in v.split(".")))


def voting_hives(registry: dict[str, Any]) -> list[str]:
    """Hives that vote: registered and not simulated."""
    return [h["id"] for h in registry.get("hives", []) if h.get("status") != "simulated"]


def ratified(proposal: dict[str, Any], registry: dict[str, Any]) -> bool:
    """True when yes-votes from voting hives reach 2/3 of all voting hives (one hive, one vote)."""
    voters = voting_hives(registry)
    if not voters:
        return False
    yes = sum(1 for h in voters if (proposal.get("votes") or {}).get(h) == "yes")
    return Fraction(yes, len(voters)) >= QUORUM


def read_feed(ref: str) -> dict[str, Any]:
    """Load a hive feed from a repo path or an https URL."""
    if ref.startswith("https://"):
        with urllib.request.urlopen(urllib.request.Request(ref, headers={"User-Agent": "honeycomb-federation"}), timeout=20) as r:
            return json.load(r)
    return json.loads((ROOT / ref).read_text(encoding="utf-8"))


def _proposal_problems(registry: dict[str, Any]) -> list[str]:
    """Ratified needs 2/3 of voting hives; founding needs decided_by and fewer than 3 voting hives."""
    out = []
    founding = len(voting_hives(registry)) < FOUNDING_UNTIL_HIVES
    for p in registry.get("proposals") or []:
        if p.get("status") == "ratified" and not ratified(p, registry):
            out.append(f"proposal {p['id']}: marked ratified without 2/3 of voting hives")
        if p.get("status") == "founding" and not (founding and p.get("decided_by")):
            out.append(f"proposal {p['id']}: 'founding' needs decided_by and fewer than {FOUNDING_UNTIL_HIVES} voting hives")
    return out


def check(registry: dict[str, Any] | None = None) -> list[str]:
    """Verify the registry: current charter hash recorded, every feed present and signed with a ratified hash."""
    registry = registry or load("federation")
    charter, hashes, out = load("charter"), known_hashes(registry), []
    if hashes.get(str(charter["version"])) != charter_sha256():
        out.append(f"charter: data/charter.yml v{charter['version']} hash is not the recorded one "
                   "(a changed charter needs a new version and a ratified proposal)")
    for row in registry.get("hives", []):
        try:
            signed = read_feed(row["feed"]).get("charter", {})
        except (OSError, ValueError) as exc:
            out.append(f"hive {row['id']}: feed {row.get('feed')} unreadable ({exc.__class__.__name__})")
            continue
        if hashes.get(str(signed.get("version"))) != signed.get("sha256"):
            out.append(f"hive {row['id']}: signed charter {signed.get('version')} does not match a ratified hash")
    return out + _proposal_problems(registry)


def sync_status(feed: dict[str, Any], registry: dict[str, Any], season_now: str) -> dict[str, str]:
    """Synchronize + harmonize for one hive: its charter (current/older/unknown) and heartbeat (current/late)."""
    signed, hashes = feed.get("charter", {}), known_hashes(registry)
    if hashes.get(str(signed.get("version"))) != signed.get("sha256"):
        charter = "unknown"
    else:
        charter = "current" if str(signed.get("version")) == latest_version(registry) else "older: re-sign"
    beat = "current" if feed.get("latest_season") in (season_now, previous_season(season_now)) else "late"
    return {"charter": charter, "heartbeat": beat}


def ripe_patterns(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Tags seen in RIPE_CARDS+ learning cards from RIPE_HIVES+ hives: each one is a DRAFT playbook proposal."""
    by_tag: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in cards:
        for t in c.get("tags", []):
            by_tag[t].append(c)
    out = []
    for tag, cs in sorted(by_tag.items()):
        hives = sorted({c["hive"] for c in cs})
        if len(cs) >= RIPE_CARDS and len(hives) >= RIPE_HIVES:
            out.append({"tag": tag, "cards": sorted(c["id"] for c in cs), "hives": hives, "status": "draft",
                        "draft": f"Write a shared '{tag}' playbook from {len(cs)} closed cells in {len(hives)} hives; "
                                 "every hive votes (charter: 2/3, one hive one vote)."})
    return out


def cross_hive_builds_on(cards: list[dict[str, Any]]) -> int:
    """Learning cards that build on a card from ANOTHER hive: compounding across schools, counted."""
    return sum(1 for c in cards for ref in c.get("builds_on", []) if ref.split("/")[0] != c["hive"])


def build_index(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Pull every registered feed and merge them into the federation index (deterministic)."""
    registry = registry or load("federation")
    feeds = [(row, read_feed(row["feed"])) for row in registry.get("hives", [])]
    as_of = max((f["as_of"] for _, f in feeds), default="1970-01-01")
    season_now = season_of(dt.date.fromisoformat(as_of))
    cards = [c for _, f in feeds for c in f.get("learnings", [])]
    totals: dict[str, float] = defaultdict(float)
    for _, f in feeds:
        for k, v in f["pulse"].items():
            if isinstance(v, (int, float)) and k != "ceo_share":
                totals[k] += v
    return {"schema": "ah-federation/1", "as_of": as_of, "season_now": season_now,
            "charter_latest": latest_version(registry),
            "hives": [{"id": row["id"], "status": row.get("status", "active"), "latest_season": f["latest_season"],
                       **sync_status(f, registry, season_now), "pulse": f["pulse"]} for row, f in feeds],
            "totals": {k: int(v) for k, v in sorted(totals.items())},
            "learnings": cards, "open_seats": [s for _, f in feeds for s in f.get("open_seats", [])],
            "cross_hive_builds_on": cross_hive_builds_on(cards), "ripe": ripe_patterns(cards)}


def render_index(index: dict[str, Any]) -> str:
    """Stable JSON text for the federation index."""
    return json.dumps(index, ensure_ascii=False, indent=1, sort_keys=True, default=str) + "\n"
