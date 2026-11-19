"""Draft recruits for a forming cell: who could fill its empty seats, with the reasons spelled out.

Rule-based on purpose: a hive of 10-100 people needs reasons a human can argue with. The CEO
recruits; this only drafts a shortlist. Capacity (P5) and alumni-only advisors (P1) are respected.
"""

from __future__ import annotations

from typing import Any

from .data import ROLE_KEYS, load, roles_in


def _load_by_member(hive: dict[str, Any], season: str) -> dict[str, int]:
    """Roles each member already holds in `season`."""
    counts: dict[str, int] = {}
    for cell in hive["cells"]:
        if cell.get("season") == season:
            for member, _ in roles_in(cell):
                counts[member] = counts.get(member, 0) + 1
    return counts


def _fit(cand: dict[str, Any], ceo: dict[str, Any]) -> tuple[int, list[str]]:
    """Score a candidate against the CEO; no shared language -> (-1, [])."""
    shared = sorted(set(cand.get("languages", [])) & set(ceo.get("languages", [])))
    if not shared:
        return -1, []
    points, reasons = 1, [f"shares {', '.join(shared)} with the CEO"]
    if cand.get("field") and cand.get("field") == ceo.get("field"):
        points += 2
        reasons.append(f"same field ({cand['field']})")
    if cand.get("type") == "alumnus" and cand.get("school") != ceo.get("school", cand.get("school")):
        reasons.append("from another school (cross-hive)")
    return points, reasons


def suggest(hive: dict[str, Any], cell_id: str, model: dict[str, Any] | None = None) -> dict[str, list[dict]]:
    """For each role short of its minimum, rank candidates who still have capacity this season."""
    model = model or load("honeycomb")
    cell = next(c for c in hive["cells"] if c["id"] == cell_id)
    members = {m["id"]: m for m in hive["members"]}
    ceo = members[cell["ceo"]]
    taken = {m for m, _ in roles_in(cell)}
    load_now = _load_by_member(hive, cell["season"])
    limit = model["capacity"]["roles_per_season"]
    out: dict[str, list[dict]] = {}
    for key, role in ROLE_KEYS:
        need = model["cell"][key]["min"] - len(cell.get(key) or [])
        if need <= 0:
            continue
        ranked = []
        for m in members.values():
            if m["id"] in taken or load_now.get(m["id"], 0) >= limit:
                continue
            if role == "advisor" and m.get("type") != "alumnus":
                continue
            if role == "apprentice" and m.get("type") != "student":
                continue
            points, reasons = _fit(m, ceo)
            if points >= 0:
                ranked.append({"member": m["id"], "points": points, "reasons": reasons})
        out[key] = sorted(ranked, key=lambda r: (-r["points"], r["member"]))[: need + 2]
    return out
