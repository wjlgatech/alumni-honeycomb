"""The member card: how sure we are of each school claim, and whether the card supports the roles it asks for.

  level(school)      0 stated · 1 supported · 2 confirmed, from evidence points (data/membership.yml `evidence`)
  check(card)        problems: missing minimal fields, roles the level or hours can't support, P5 capacity,
                     minors without safeguarding, profit without disclosure
  one_pager(card)    the card as Markdown (minimal → standard → full), levels in words, never "verified"

Proof grows with the role's risk; school proof is never treated as safety (that is `safeguarding`).
"""

from __future__ import annotations

from typing import Any

from .data import load


def level(school: dict[str, Any], cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    """Level of one school claim, with the points, kinds and reasons behind it."""
    cfg = cfg or load("membership")
    kinds = {e["kind"]: e for e in cfg["evidence"]}
    points, used, circles, counts = 0, set(), set(), {}
    for ev in school.get("evidence", []) or []:
        k = kinds.get(ev.get("kind"))
        if not k:
            continue
        if k["peer"]:
            circle = (ev.get("circle") or ev.get("how") or "").strip().lower()
            if not circle or circle in circles:
                continue  # a vouch must say how they know you, and one circle counts once
            circles.add(circle)
        counts[k["kind"]] = counts.get(k["kind"], 0) + 1
        if counts[k["kind"]] > k.get("max", 99):
            continue
        points += k["points"]
        if k["points"]:
            used.add(ev["kind"])
    non_peer = any(not kinds[k]["peer"] for k in used)
    lv = 0
    for row in cfg["levels"][1:]:
        if points >= row["min_points"] and len(used) >= row.get("min_kinds", 0) and (non_peer or not row.get("needs_non_peer")):
            lv = row["level"]
    return {"school": school.get("name"), "level": lv, "name": cfg["levels"][lv]["name"], "points": points, "kinds": sorted(used)}


def check(card: dict[str, Any], cfg: dict[str, Any] | None = None, model: dict[str, Any] | None = None) -> list[str]:
    """Everything that stops this card from supporting what it asks for."""
    cfg = cfg or load("membership")
    model = model or load("honeycomb")
    problems = [f"missing {f['key']}" for f in cfg["tiers"]["minimal"] if not card.get(f["key"])]
    roles = card.get("roles") or []
    cap = model["capacity"]
    if len(roles) > cap["roles_per_season"] or roles.count("ceo") > cap["ceo_per_season"]:
        problems.append(f"P5: at most {cap['roles_per_season']} roles and {cap['ceo_per_season']} CEO role a season")
    need = sum(cfg["roles"][r]["hours_min"] for r in roles if r in cfg["roles"])
    if card.get("hours_per_week") is not None and need > card["hours_per_week"]:
        problems.append(f"{', '.join(roles)} need about {need} h/week; the card offers {card['hours_per_week']}")
    if "advisor" in roles:
        alumni = [level(s, cfg) for s in card.get("schools", []) if s.get("relation") == "alumnus"]
        if not any(lv["level"] >= cfg["roles"]["advisor"]["min_level"] for lv in alumni):
            problems.append("advisor: no school is supported yet (add a registry, public record or 2 vouches)")
    if card.get("works_with_minors") and not (card.get("safeguarding") or {}).get("screened"):
        problems.append("minors: a dated screen and the two-adult rule are needed before joining a cell with a minor")
    if not card.get("purpose"):
        problems.append("no purpose yet: one sentence on what you are becoming, and for whom")
    if card.get("interests") and any(i.get("commercial") for i in card["interests"]) and not card.get("conflicts"):
        problems.append("a commercial interest is listed but no conflict is disclosed")
    return problems


def loop_health(card: dict[str, Any]) -> dict[str, Any]:
    """The personal loop in numbers: weeks logged, hours given vs promised, next steps kept, energy trend."""
    weeks = card.get("weekly") or []
    promised = card.get("hours_per_week") or 0
    given = [w.get("hours_given", 0) or 0 for w in weeks]
    kept = sum(1 for a, b in zip(weeks, weeks[1:]) if a.get("next_step") and b.get("kept_last_step"))
    return {"weeks": len(weeks), "avg_hours_given": round(sum(given) / len(given), 1) if given else 0.0,
            "promised": promised, "steps_kept": kept, "steps_due": max(len(weeks) - 1, 0),
            "energy_last": weeks[-1].get("energy") if weeks else None,
            "has_purpose": bool(card.get("purpose")), "has_goal": bool((card.get("season_goal") or {}).get("good"))}


def one_pager(card: dict[str, Any], cfg: dict[str, Any] | None = None) -> str:
    """The card as one page of Markdown, minimal first."""
    cfg = cfg or load("membership")
    out = [f"# {card.get('name', '?')}", "",
           f"**Offers:** {card.get('offer', '—')}  ", f"**Asks:** {card.get('ask', '—')}  ",
           f"**Roles this season:** {', '.join(card.get('roles') or []) or '—'} · **{card.get('hours_per_week', '?')} h/week** · "
           f"{', '.join(card.get('languages') or [])} · {card.get('timezone', '')} · {card.get('mode', '')}", "",
           "## Schools", "", "| School | As | Field, years | Proof | Level |", "|---|---|---|---|---|"]
    for s in card.get("schools", []):
        lv = level(s, cfg)
        out.append(f"| {s.get('name')} | {s.get('relation')} | {s.get('field', '')} {s.get('years', '')} | "
                   f"{', '.join(lv['kinds']) or 'none yet'} ({lv['points']} pts) | **{lv['name']}** |")
    if card.get("interests"):
        out += ["", "## Would lead or help with", ""]
        out += [f"- {i['what']}" + (" (commercial: see conflicts)" if i.get("commercial") else "") for i in card["interests"]]
    if card.get("conflicts"):
        out += ["", "## Could profit from", ""] + [f"- {c}" for c in card["conflicts"]]
    if card.get("purpose") or card.get("season_goal"):
        g = card.get("season_goal") or {}
        h = loop_health(card)
        out += ["", "## My loop", "", f"**Purpose:** {card.get('purpose', '—')}  ",
                f"**This season:** {g.get('what', '—')} · Good: {g.get('good', '—')}  ",
                f"**So far:** {h['weeks']} weekly check-ins · {h['avg_hours_given']} h/week given of {h['promised']} promised · "
                f"{h['steps_kept']}/{h['steps_due']} next steps kept"]
    problems = check(card, cfg)
    out += ["", "## Not yet supported", ""] + ([f"- {p}" for p in problems] or ["- nothing: this card supports what it asks for"])
    return "\n".join(out) + "\n"
