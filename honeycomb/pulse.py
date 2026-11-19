"""A hive's vital signs and the North Star. Aggregate numbers only: safe to publish.

active_cells    cells with status active (check.py P1 guarantees their full shape)
role_switchers  members who held 2+ different roles across all cells (the North Star)
ceo_share       share of students who are CEO of a cell in the latest season
"""

from __future__ import annotations

from typing import Any

from .data import roles_in


def _latest_season(hive: dict[str, Any]) -> str | None:
    """The season with the latest start date, or None."""
    seasons = sorted(hive["seasons"], key=lambda s: str(s["start"]))
    return seasons[-1]["id"] if seasons else None


def pulse(hive: dict[str, Any]) -> dict[str, Any]:
    """Return aggregate numbers for one hive (no names, no ids of people)."""
    roles: dict[str, set[str]] = {}
    for cell in hive["cells"]:
        for member, role in roles_in(cell):
            roles.setdefault(member, set()).add(role)
    latest = _latest_season(hive)
    students = [m["id"] for m in hive["members"] if m.get("type") == "student"]
    ceos_now = {c["ceo"] for c in hive["cells"] if c.get("season") == latest and c.get("status") != "forming"}
    return {
        "season": latest,
        "members": len(hive["members"]),
        "cells_total": len(hive["cells"]),
        "active_cells": sum(1 for c in hive["cells"] if c.get("status") == "active"),
        "closed_with_evidence": sum(1 for c in hive["cells"]
                                    if c.get("status") == "closed" and (c.get("outcome") or {}).get("evidence")),
        "role_switchers": sum(1 for r in roles.values() if len(r) >= 2),
        "ceo_share": round(len(ceos_now & set(students)) / len(students), 2) if students else 0.0,
        "checkins": len(hive["checkins"]),
    }


def verdict(numbers: dict[str, Any], targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compare numbers to targets; each row gets value and met: True/False. Missing measures count 0."""
    return [{**t, "value": numbers.get(t["measure"], 0), "met": numbers.get(t["measure"], 0) >= t["target"]}
            for t in targets]
