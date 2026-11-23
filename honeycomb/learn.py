"""Before a cell acts, show it what other cells (any hive) already learned. The compounding step, made cheap.

Ranking is rule-based so a human can argue with it: shared tags count 3, shared vision words count 1.
A card from another hive is labelled cross-hive; citing it in the cell's `builds_on` is what
`federation.cross_hive_builds_on` counts.
"""

from __future__ import annotations

import re
from typing import Any

STOP = {"a", "an", "the", "and", "or", "of", "to", "for", "with", "in", "on", "by", "that", "they", "their",
        "who", "it", "is", "are", "be", "as", "at", "from", "this", "each", "one", "help", "helps"}


def _words(text: str) -> set[str]:
    """Content words (3+ letters, or CJK runs) of a vision line, minus stop words."""
    return {w for w in re.findall(r"[a-z一-鿿]{3,}", text.lower()) if w not in STOP}


def rank(cell: dict[str, Any], hive_id: str, cards: list[dict[str, Any]], top: int = 5) -> list[dict[str, Any]]:
    """Cards most relevant to `cell`, best first: {id, points, cross_hive, reasons, learned}."""
    own = f"{hive_id}/{cell['id']}"
    tags, words = set(cell.get("tags") or []), _words(str(cell.get("vision", "")))
    out = []
    for c in cards:
        if c["id"] == own:
            continue
        shared_tags = sorted(tags & set(c.get("tags", [])))
        shared_words = sorted(words & _words(c.get("vision", "")))
        points = 3 * len(shared_tags) + len(shared_words)
        if not points:
            continue
        reasons = ([f"tags: {', '.join(shared_tags)}"] if shared_tags else []) + \
                  ([f"words: {', '.join(shared_words[:4])}"] if shared_words else [])
        out.append({"id": c["id"], "points": points, "cross_hive": c["hive"] != hive_id,
                    "reasons": reasons, "learned": c.get("learned", "")})
    return sorted(out, key=lambda r: (-r["points"], r["id"]))[:top]
