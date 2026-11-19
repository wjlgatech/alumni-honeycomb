"""The Calling Compass rule: 8 answers (0..3) -> a level per dimension + where to start.

Mirrors web/compass.js exactly; the golden cases in data/compass.yml keep the two in step.
"""

from __future__ import annotations

from typing import Any

from .data import load

DIM_ORDER = ("spirit", "mind", "heart", "strategy")


def level_for(total: int, levels: list[dict[str, Any]]) -> str:
    """Map a dimension total (0..6) to a level id; raise ValueError if no band covers it."""
    for band in levels:
        if band["min"] <= total <= band["max"]:
            return band["id"]
    raise ValueError(f"no level covers total {total}")


def score(answers: list[int], spec: dict[str, Any] | None = None) -> dict[str, Any]:
    """Score one person's answers.

    Returns {"totals": {dim: int}, "levels": {dim: level_id}, "start": dim | None}.
    `start` is the lowest dimension (ties broken by DIM_ORDER), or None when every
    dimension is already at the top level (nothing to start with: they can companion someone).
    """
    spec = spec or load("compass")
    questions = spec["questions"]
    if len(answers) != len(questions):
        raise ValueError(f"expected {len(questions)} answers, got {len(answers)}")
    if any(a not in (0, 1, 2, 3) for a in answers):
        raise ValueError("each answer must be 0, 1, 2 or 3")
    totals = {d: 0 for d in DIM_ORDER}
    for q, a in zip(questions, answers):
        totals[q["dim"]] += a
    levels = {d: level_for(t, spec["levels"]) for d, t in totals.items()}
    top = max(band["max"] for band in spec["levels"])
    gaps = [d for d in DIM_ORDER if totals[d] < top]
    start = min(gaps, key=lambda d: (totals[d], DIM_ORDER.index(d))) if gaps else None
    return {"totals": totals, "levels": levels, "start": start}
