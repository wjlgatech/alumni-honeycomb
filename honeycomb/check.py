"""Enforce the machine-checkable charter principles (data/charter.yml `checked:`) on a hive file.

Each rule is a small function returning a list of problem strings; `check()` runs them all.
"""

from __future__ import annotations

import re
from typing import Any

from .data import ROLE_KEYS, load, roles_in

FORBIDDEN_KEYS = {"phone", "email", "wechat", "weixin", "id_number", "real_name", "address", "qq"}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d\s-]{9,}\d)(?!\d)")


def _walk(node: Any, path: str = ""):
    """Yield (path, key, value) for every key in a nested dict/list."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield path, str(k), v
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, f"{path}[{i}]")


def safety(hive: dict[str, Any], model: dict[str, Any]) -> list[str]:
    """P6: pseudonyms only, no contact details, a guardian for every minor, '(sim)' names when simulated."""
    out = []
    for path, key, value in _walk(hive):
        if key.lower() in FORBIDDEN_KEYS:
            out.append(f"P6 safety: field '{key}' at {path or 'top'} is not allowed")
        if isinstance(value, str) and (EMAIL.search(value) or PHONE.search(value)):
            out.append(f"P6 safety: {path}.{key} looks like contact details")
    simulated = bool(hive["hive"].get("simulated"))
    for m in hive["members"]:
        if m.get("age_band") == "under18" and not m.get("guardian"):
            out.append(f"P6 safety: {m['id']} is under 18 and has no guardian")
        if simulated and not str(m.get("name", "")).endswith("(sim)"):
            out.append(f"P6 safety: {m['id']} must be labelled '(sim)' in a simulated hive")
    return out


def cell_shape(hive: dict[str, Any], model: dict[str, Any]) -> list[str]:
    """P1: known members, valid status, an active/closed cell has 2-3 of each role, advisors are alumni."""
    out, members = [], {m["id"]: m for m in hive["members"]}
    seasons = {s["id"] for s in hive["seasons"]}
    shape = model["cell"]
    for cell in hive["cells"]:
        cid = cell.get("id", "?")
        if cell.get("status") not in shape["statuses"]:
            out.append(f"P1 cell_shape: {cid} has unknown status {cell.get('status')!r}")
        if cell.get("season") not in seasons:
            out.append(f"P1 cell_shape: {cid} names unknown season {cell.get('season')!r}")
        people = roles_in(cell)
        ids = [m for m, _ in people]
        out += [f"P1 cell_shape: {cid} names unknown member {m!r}" for m in ids if m not in members]
        out += [f"P1 cell_shape: {m} appears twice in {cid}" for m in sorted({m for m in ids if ids.count(m) > 1})]
        out += [f"P1 cell_shape: advisor {m} in {cid} must be an alumnus"
                for m in cell.get("advisors") or [] if members.get(m, {}).get("type") != "alumnus"]
        if cell.get("status") == "forming":
            continue
        for key, _ in ROLE_KEYS:
            n, band = len(cell.get(key) or []), shape[key]
            if not band["min"] <= n <= band["max"]:
                out.append(f"P1 cell_shape: {cid} has {n} {key}; needs {band['min']}-{band['max']}")
    return out


def vision_and_good(hive: dict[str, Any], model: dict[str, Any]) -> list[str]:
    """P2: every cell has a vision and a 'Good:' success criterion before it acts."""
    out = []
    for cell in hive["cells"]:
        if not str(cell.get("vision") or "").strip():
            out.append(f"P2 criteria-first: {cell['id']} has no vision")
        if not str(cell.get("good") or "").strip().startswith("Good:"):
            out.append(f"P2 criteria-first: {cell['id']} needs a 'Good:' success criterion")
    return out


def closed_has_evidence(hive: dict[str, Any], model: dict[str, Any]) -> list[str]:
    """P3: a closed cell records what was observed."""
    return [f"P3 evidence: closed cell {c['id']} has no outcome.evidence"
            for c in hive["cells"]
            if c.get("status") == "closed" and not str((c.get("outcome") or {}).get("evidence") or "").strip()]


def checkin_next_step(hive: dict[str, Any], model: dict[str, Any]) -> list[str]:
    """P4: every check-in names a known cell and ends with a written next step."""
    cells = {c["id"] for c in hive["cells"]}
    out = []
    for i, ci in enumerate(hive["checkins"]):
        if ci.get("cell") not in cells:
            out.append(f"P4 next-step: check-in {i} names unknown cell {ci.get('cell')!r}")
        if not str(ci.get("next_step") or "").strip():
            out.append(f"P4 next-step: check-in {i} has no written next step")
    return out


def capacity(hive: dict[str, Any], model: dict[str, Any]) -> list[str]:
    """P5: per season, at most N roles per person and at most one CEO role."""
    limits, out = model["capacity"], []
    per: dict[tuple[str, str], list[str]] = {}
    for cell in hive["cells"]:
        for member, role in roles_in(cell):
            per.setdefault((cell.get("season"), member), []).append(role)
    for (season, member), roles in sorted(per.items(), key=lambda kv: (str(kv[0][0]), kv[0][1])):
        if len(roles) > limits["roles_per_season"]:
            out.append(f"P5 capacity: {member} holds {len(roles)} roles in {season} (max {limits['roles_per_season']})")
        if roles.count("ceo") > limits["ceo_per_season"]:
            out.append(f"P5 capacity: {member} is CEO of {roles.count('ceo')} cells in {season} (max {limits['ceo_per_season']})")
    return out


RULES = (safety, cell_shape, vision_and_good, closed_has_evidence, checkin_next_step, capacity)


def check(hive: dict[str, Any], model: dict[str, Any] | None = None) -> list[str]:
    """Return every problem found (empty list = the hive keeps the charter)."""
    model = model or load("honeycomb")
    return [p for rule in RULES for p in rule(hive, model)]
