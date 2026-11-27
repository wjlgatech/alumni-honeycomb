"""Meeting summaries: what a honeycomb (cell) may release from a meeting, checked against the Release Agreement.

  check(m, hive)          problems that block release: missing fields, missing approvals (a guardian for a minor),
                          names, contacts, sensitive topics, long or unapproved quotes
  card(m, hive_id)        the released summary: about the work, never the people (no attendees, no approvals)
  released(hive, tier)    every summary in a hive that passes check and is released at least to `tier`
  digest(cards, tags, n)  what one member sees: the n best summaries for the tags they follow, newest first

Rules: data/release.yml (Chatham House Rule + every person approves the exact text). The same message shape serves a
honeycomb, a beehive and the federation: one protocol, many scales (docs/TOOLKIT.md).
"""

from __future__ import annotations

import json
import re
from typing import Any

from .data import load

TIERS = ("cell", "hive", "federation")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(?<![\d-])(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?![\d-])|(?<!\d)1[3-9]\d{9}(?!\d)")  # US-style or China mobile
# Topics that never leave a meeting (release.yml never_release). Kept short and explicit; extend by PR.
SENSITIVE = re.compile(r"\b(hospital\w*|mental health|depress\w*|anxiety|therap\w*|diagnos\w*|medication|suicid\w*|"
                       r"divorce|custody|lawsuit|salary|debt|pregnan\w*)\b|住院|抑郁|焦虑|离婚|自杀|诊断", re.IGNORECASE)
PUBLIC_KEYS = ("date", "purpose", "decisions", "next_steps", "learned", "tags", "asks", "offers", "open_questions")


def _public_text(m: dict[str, Any]) -> str:
    """Everything in a summary that would be released, as one string to scan."""
    parts = [m.get(k) for k in PUBLIC_KEYS] + [[q.get("text", "") for q in m.get("quotes") or []]]
    return json.dumps(parts, ensure_ascii=False, default=str)


def check(m: dict[str, Any], hive: dict[str, Any], cfg: dict[str, Any] | None = None) -> list[str]:
    """Why this summary may not be released yet (empty = it may)."""
    cfg = cfg or load("release")
    sid = m.get("id", "?")
    out = [f"{sid}: missing {f['key']}" for f in cfg["summary_fields"]["required"] if not m.get(f["key"])]
    if m.get("release", cfg["approval"]["default_tier"]) not in TIERS:
        out.append(f"{sid}: release must be one of {', '.join(TIERS)}")
    members = {p["id"]: p for p in hive.get("members", [])}
    approved = set(m.get("approved_by") or [])
    for who in m.get("attendees") or []:
        p = members.get(who, {})
        need = f"guardian:{who}" if p.get("age_band") == "under18" else who
        if need not in approved:
            out.append(f"{sid}: not yet approved by {need}")
    text = _public_text(m)
    for p in members.values():
        for token in (p.get("id"), p.get("name"), str(p.get("name", "")).replace(" (sim)", "")):
            if token and len(token) > 2 and re.search(r"\b" + re.escape(token) + r"\b", text):
                out.append(f"{sid}: names a person ({p['id']})")
                break
    if EMAIL.search(text) or PHONE.search(text):
        out.append(f"{sid}: contains an email or phone number")
    if SENSITIVE.search(text):
        out.append(f"{sid}: touches a topic that never leaves a meeting ('{SENSITIVE.search(text).group(0)}')")
    for q in m.get("quotes") or []:
        if not q.get("quote_ok") or len(str(q.get("text", "")).split()) > 25:
            out.append(f"{sid}: a quote needs its speaker's yes and at most 25 words")
    return out


def card(m: dict[str, Any], hive_id: str) -> dict[str, Any]:
    """The released form: the work, never the people."""
    return {"id": f"{hive_id}/{m['cell']}/{m['id']}", "hive": hive_id, "cell": f"{hive_id}/{m['cell']}",
            "release": m.get("release", "cell"), **{k: (str(m[k]) if k == "date" else m[k]) for k in PUBLIC_KEYS if m.get(k)},
            **({"quotes": [q["text"] for q in m["quotes"]]} if m.get("quotes") else {})}


def released(hive: dict[str, Any], tier: str) -> list[dict[str, Any]]:
    """Summaries that pass `check` and are released to `tier` or wider."""
    floor = TIERS.index(tier)
    return [card(m, hive["hive"]["id"]) for m in hive.get("meetings", []) or []
            if TIERS.index(m.get("release", "cell")) >= floor and not check(m, hive)]


def digest(cards: list[dict[str, Any]], tags: list[str], limit: int = 5) -> list[dict[str, Any]]:
    """A member's digest: summaries sharing their tags, most shared tags first, then newest; capped so nobody drowns."""
    want = {t.lower() for t in tags}
    scored = [(len(want & {t.lower() for t in c.get("tags", [])}), str(c.get("date", "")), c) for c in cards]
    ranked = sorted((x for x in scored if x[0] > 0), key=lambda x: (x[0], x[1]), reverse=True)
    return [c for _, _, c in ranked][:limit]
