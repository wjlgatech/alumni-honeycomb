"""Load the YAML files under data/ and hives/ (the single source of truth)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load(name: str) -> dict[str, Any]:
    """Load data/<name>.yml as a dict; raise FileNotFoundError if it is missing."""
    with open(DATA / f"{name}.yml", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def charter_sha256() -> str:
    """SHA-256 of data/charter.yml's exact bytes: the hash a hive signs."""
    return hashlib.sha256((DATA / "charter.yml").read_bytes()).hexdigest()


def load_hive(path: str | Path) -> dict[str, Any]:
    """Load a hive file and fill missing sections with empty lists."""
    with open(path, encoding="utf-8") as fh:
        hive = yaml.safe_load(fh) or {}
    for key in ("members", "seasons", "cells", "checkins"):
        hive.setdefault(key, [])
    hive.setdefault("hive", {})
    return hive


ROLE_KEYS = (("advisors", "advisor"), ("core", "core"), ("apprentices", "apprentice"))


def roles_in(cell: dict[str, Any]) -> list[tuple[str, str]]:
    """Every (member_id, role) in one cell, CEO first."""
    out = [(cell["ceo"], "ceo")] if cell.get("ceo") else []
    for key, role in ROLE_KEYS:
        out += [(m, role) for m in cell.get(key) or []]
    return out
