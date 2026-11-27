"""Pre-launch discovery: pick whom to meet 1:1, tally what they said and did, print the question card.

Relationship first, research second (Paul, 2026-11-26). A 1:1 succeeds first when the person feels heard
and gets something from us; second when they act (the ladder rung), and only third when they hold an opinion.

  plan(people)        greedy picks: two voices per people group, three overlapping hubs in the first hive's
                      circle (complex contagion), then 2 end users and 1 skeptic to correct for hub bias
  tally(interviews)   aggregate numbers, the D-targets, which pre-committed rules fire, breaks with no detector
  card()              the bilingual one-page question card (docs/DISCOVERY-CARD.md, drift-gated)

Input files are private (hives-private/discovery/); outputs carry pseudonymous ids and numbers only.
"""

from __future__ import annotations

from typing import Any, Callable

from .data import load


def _gain(p: dict[str, Any], voices: dict[str, int], cluster_n: int, cfg: dict[str, Any], target: str | None) -> tuple[int, list[str]]:
    """Marginal value of meeting `p` next, given voices already heard per segment."""
    sel = cfg["selection"]
    open_segs = [s for s in p.get("segments", []) if voices.get(s, 0) < sel["voices_per_segment"]]
    points, reasons = len(open_segs), ([f"speaks for {', '.join(open_segs)}"] if open_segs else [])
    if target and p.get("cluster") == target and cluster_n < sel["cluster_voices"]:
        points += 1
        reasons.append(f"in the first hive's circle ({target}): reinforcing tie")
    return points, reasons


def _rank_key(p: dict[str, Any], points: int, cfg: dict[str, Any]) -> tuple:
    """Sort key: most points, then most trust, then in person, then id (stable)."""
    bonus = cfg["selection"]["in_person_bonus"] if p.get("in_person") else 0
    return (-points, -p.get("trust", 0), -bonus, p["id"])


def plan(people: dict[str, Any], cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    """Pick up to max_meetings people; every pick carries its reasons. Trust 0 is never picked."""
    cfg = cfg or load("discovery")
    sel, target = cfg["selection"], people.get("first_hive_cluster")
    pool = [p for p in people.get("people", []) if p.get("trust", 0) >= 1]
    voices: dict[str, int] = {}
    picks: list[dict[str, Any]] = []
    hub_slots = sel["max_meetings"] - sum(sel["reserve"].values())
    hubs = [p for p in pool if p.get("kind", "hub") == "hub"]
    while len(picks) < hub_slots and hubs:
        cluster_n = sum(1 for k in picks if k["cluster"] == target)
        scored = [(p, *_gain(p, voices, cluster_n, cfg, target)) for p in hubs]
        p, points, reasons = min(scored, key=lambda t: _rank_key(t[0], t[1], cfg))
        if points <= 0:
            break
        hubs.remove(p)
        for s in p.get("segments", []):
            voices[s] = voices.get(s, 0) + 1
        picks.append({"id": p["id"], "kind": "hub", "cluster": p.get("cluster"), "in_person": bool(p.get("in_person")),
                      "reasons": reasons})
    for kind, n in sel["reserve"].items():
        cands = sorted((p for p in pool if p.get("kind") == kind),
                       key=lambda p: (p.get("cluster") != target, -p.get("trust", 0), p["id"]))
        for p in cands[:n]:
            for s in p.get("segments", []):
                voices[s] = voices.get(s, 0) + 1
            why = "is the user, not a hub: ground truth" if kind == "end_user" else "expects it to fail: hears what fans won't say"
            picks.append({"id": p["id"], "kind": kind, "cluster": p.get("cluster"), "in_person": bool(p.get("in_person")),
                          "reasons": [why]})
    need = sel["voices_per_segment"]
    gaps = [s["id"] for s in cfg["segments"] if voices.get(s["id"], 0) < need]
    return {"picks": picks, "voices": voices, "gaps": gaps}


def _seats(interviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Committed seats, de-duplicated by `who` when two people name the same person."""
    seen, out = set(), []
    for i in interviews:
        for k, s in enumerate(i.get("seats", []) or []):
            key = (s.get("who"), s["role"]) if s.get("who") else (i["id"], k)
            if key not in seen:
                seen.add(key)
                out.append(s)
    return out


def numbers(interviews: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate numbers only (no ids of people): safe to share with the team."""
    seats = _seats(interviews)
    parents = [i["value"] for i in interviews if i.get("speaks_as") == "parent" and "value" in i]
    breaks: dict[str, int] = {}
    for i in interviews:
        for b in set(i.get("breaks", []) or []):
            breaks[b] = breaks.get(b, 0) + 1
    return {
        "interviews": len(interviews),
        "in_person": sum(1 for i in interviews if i.get("mode") == "in_person"),
        "segments_heard": len({i["speaks_as"] for i in interviews if i.get("speaks_as")}),
        "felt_heard": sum(1 for i in interviews if i.get("felt_heard")),
        "gave_first": sum(1 for i in interviews if i.get("gave")),
        "rung_intro_or_more": sum(1 for i in interviews if i.get("rung", 0) >= 2),
        "seats_committed": len(seats),
        "ceo_candidates": sum(1 for s in seats if s["role"] == "ceo"),
        "parent_value": round(sum(parents) / len(parents), 2) if parents else None,
        "breaks": dict(sorted(breaks.items(), key=lambda kv: (-kv[1], kv[0]))),
    }


# Pre-committed rules (data/discovery.yml `rules`): one function each, so the data decides, not the mood.
def _r1(n: dict[str, Any]) -> bool:
    """R1: fewer than two CEO candidates."""
    return n["ceo_candidates"] < 2


def _r2(n: dict[str, Any]) -> bool:
    """R2: some break raised by three or more people."""
    return any(c >= 3 for c in n["breaks"].values())


def _r3(n: dict[str, Any]) -> bool:
    """R3: parents heard rate the value below 2."""
    return n["parent_value"] is not None and n["parent_value"] < 2


def _r4(n: dict[str, Any]) -> bool:
    """R4: two or more people raise faith content as a risk."""
    return n["breaks"].get("faith_complaint", 0) >= 2


def _r5(n: dict[str, Any]) -> bool:
    """R5: fewer than six committed seats."""
    return n["seats_committed"] < 6


RULES: dict[str, Callable[[dict[str, Any]], bool]] = {"R1": _r1, "R2": _r2, "R3": _r3, "R4": _r4, "R5": _r5}


def tally(interviews: list[dict[str, Any]], cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    """Numbers, D-target verdicts, fired rules, and raised breaks that nothing detects yet."""
    cfg = cfg or load("discovery")
    n = numbers(interviews)
    targets = [{**t, "value": n.get(t["measure"]) or 0, "met": (n.get(t["measure"]) or 0) >= t["target"]}
               for t in cfg["targets"]]
    fired = [r for r in cfg["rules"] if RULES[r["id"]](n)]
    blind = [b["id"] for b in cfg["breaks"] if b["detector"] == "none" and n["breaks"].get(b["id"])]
    unknown = sorted(set(n["breaks"]) - {b["id"] for b in cfg["breaks"]})
    return {"numbers": n, "targets": targets, "fired": fired, "undetected": blind, "unknown_breaks": unknown}


def card(cfg: dict[str, Any] | None = None) -> str:
    """The one-page question card, 中文 first. Generated from data/discovery.yml; never hand-edit the output."""
    cfg = cfg or load("discovery")
    unk = {u["id"]: u for u in cfg["unknowns"]}
    out = ["# 一对一访谈卡 · 1:1 interview card", "",
           "_Generated from `data/discovery.yml` by `python -m honeycomb discovery card`. Do not edit by hand._", "",
           "**先关系，后研究。** 先给，再问。只问过去发生的事和具体的行动，不问「你会不会」。",
           "**Relationship first, research second.** Give before you ask. Ask about the past and concrete acts, never \"would you\".",
           "", "30 分钟：5 分钟听对方正在做的事 → 20 分钟问题 → 5 分钟邀请（阶梯）。结束后 15 分钟内记录。",
           "30 minutes: 5 on what they are building → 20 on questions → 5 on the ask (the ladder). Write it up within 15 minutes.", "",
           "| # | 要弄清 · Unknown | 问题 | Question | 听什么 · Listen for |", "|---|---|---|---|---|"]
    for q in cfg["questions"]:
        u = unk[q["unknown"]]
        out.append(f"| {q['n']} | {u['zh']} · {u['en']} | {q['zh']} | {q['en']} | {q['listen']} |")
    out += ["", "## 阶梯 · The ladder (record what they DID)", "", "| Rung | 中文 | English |", "|---|---|---|"]
    out += [f"| {r['rung']} | {r['zh']} | {r['en']} |" for r in cfg["ladder"]]
    out += ["", "## 会坏在哪 · What breaks it", "", "| Break | Kind | 中文 | English | Detector today |", "|---|---|---|---|---|"]
    out += [f"| `{b['id']}` | {b['kind']} | {b['zh']} | {b['en']} | {b['detector']} |" for b in cfg["breaks"]]
    out += ["", "## 预先承诺的规则 · Pre-committed rules", "", "| Rule | When | 那么 | Then |", "|---|---|---|---|"]
    out += [f"| {r['id']} | `{r['when']}` | {r['then_zh']} | {r['then_en']} |" for r in cfg["rules"]]
    return "\n".join(out) + "\n"


def build_room(people: dict[str, Any], names: dict[str, Any], briefs: dict[str, Any],
               interviews: list[dict[str, Any]], cfg: dict[str, Any] | None = None, today: str = "",
               me: dict[str, Any] | None = None) -> dict[str, Any]:
    """The private room snapshot the futuremake.io room page renders: plan, people, briefs, tally. Never committed."""
    cfg = cfg or load("discovery")
    t = tally(interviews, cfg)
    plan_ = plan(people, cfg)
    picked = {p["id"]: p for p in plan_["picks"]}
    last = {i.get("person", ""): i for i in interviews}
    rows = []
    for p in people.get("people", []):
        n, iv = names.get(p["id"], {}), last.get(p["id"])
        rows.append({"id": p["id"], "name": n.get("name", p["id"]), "why": n.get("why", ""), "kind": p.get("kind", "hub"),
                     "segments": p.get("segments", []), "cluster": p.get("cluster"), "in_person": bool(p.get("in_person")),
                     "picked": p["id"] in picked, "reasons": picked.get(p["id"], {}).get("reasons", []),
                     "brief": (briefs.get("people") or {}).get(p["id"]), "met": bool(iv),
                     "rung": iv.get("rung") if iv else None, "seats": iv.get("seats", []) if iv else []})
    first = people.get("first_hive_cluster")
    rows.sort(key=lambda r: (r["cluster"] != first, not r["picked"], r["id"]))
    return {"updated": today, "first_hive": first, "networks": people.get("networks", {}),
            "card": {k: v for k, v in briefs.items() if k != "people"}, "people": rows, "gaps": plan_["gaps"],
            "numbers": t["numbers"], "targets": t["targets"], "fired": t["fired"], "undetected": t["undetected"],
            "ladder": cfg["ladder"], "rules": cfg["rules"],
            "merged": [i["note_at"] for i in interviews if i.get("note_at")],
            "me": _member_view(me) if me else None}


def _member_view(card: dict[str, Any]) -> dict[str, Any]:
    """The owner's member card, as the room page renders it (levels in words, problems, loop numbers)."""
    from . import member
    return {"name": card.get("name"), "purpose": card.get("purpose"), "offer": card.get("offer"), "ask": card.get("ask"),
            "roles": card.get("roles", []), "hours_per_week": card.get("hours_per_week"),
            "schools": [{**member.level(s), "field": s.get("field", ""), "years": s.get("years", "")} for s in card.get("schools", [])],
            "interests": card.get("interests", []), "conflicts": card.get("conflicts", []),
            "season_goal": card.get("season_goal"), "loop": member.loop_health(card), "problems": member.check(card)}


def merge_notes(interviews: list[dict[str, Any]], notes: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Fold phone notes into the interview list, one interview per note keyed by its server time. Returns (list, added)."""
    seen = {i.get("note_at") for i in interviews}
    added = 0
    for n in notes:
        if n.get("at") in seen:
            continue
        seats = [{"role": n["seat"]}] if n.get("seat") not in (None, "", "none") else []
        interviews.append({"id": f"N-{n['at'][:19]}", "note_at": n["at"], "person": n["person"], "date": n["at"][:10],
                           "mode": "in_person", "rung": n.get("rung", 0), "seats": seats, "quote": n.get("quote", ""),
                           "risk": n.get("risk", ""), "gave": n.get("gave", ""), "felt_heard": bool(n.get("heard"))})
        added += 1
    return interviews, added
