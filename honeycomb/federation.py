"""The federation: hives that signed the same charter, verified by hash, governed by 2/3 vote.

Web3 ideas without a chain or a token: the protocol is a file anyone can fork; membership is a
verifiable hash; each hive owns its data; changes need a supermajority; exit is always open.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from .data import ROOT, charter_sha256, load, load_hive

QUORUM = Fraction(2, 3)


def known_hashes(registry: dict[str, Any]) -> dict[str, str]:
    """version -> sha256 for every charter the federation has ratified."""
    return {str(c["version"]): c["sha256"] for c in registry.get("charters", [])}


def check(registry: dict[str, Any] | None = None) -> list[str]:
    """Verify the registry: current charter hash recorded, every hive file present and signed correctly."""
    registry = registry or load("federation")
    charter = load("charter")
    hashes, out = known_hashes(registry), []
    if hashes.get(str(charter["version"])) != charter_sha256():
        out.append(f"charter: data/charter.yml v{charter['version']} hash is not the recorded one "
                   "(a changed charter needs a new version and a ratified proposal)")
    for row in registry.get("hives", []):
        path = ROOT / row["path"]
        if not path.exists():
            out.append(f"hive {row['id']}: {row['path']} not found")
            continue
        signed = load_hive(path)["hive"].get("charter", {})
        if hashes.get(str(signed.get("version"))) != signed.get("sha256"):
            out.append(f"hive {row['id']}: signed charter {signed.get('version')} does not match a ratified hash")
    for p in registry.get("proposals") or []:
        if p.get("status") == "ratified" and not ratified(p, registry):
            out.append(f"proposal {p['id']}: marked ratified without 2/3 of voting hives")
    return out


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
