"""Command line: python -m honeycomb <command> [...]

  check   <hive.yml>                 enforce the charter principles; exit 1 on any problem
  pulse   <hive.yml> [--json]        vital signs + the 10X targets (aggregate numbers only)
  recruit <hive.yml> <cell-id>       draft a shortlist for a forming cell's empty seats
  publish <hive.yml> [--out F] [--check]   write the hive's PUBLIC feed (numbers, learning cards, open seats; no people)
  federation check | hash | pull [--check]   verify the registry / charter hash / merge all feeds -> federation/index.json
  learn   <hive.yml> <cell-id> [--index F]  what other cells (any hive) already learned that fits this cell
  compass 3 2 1 1 2 0 3 3            score 8 Calling Compass answers (0..3) in question order
  build   [--check]                  data/*.yml -> web/data.json
  discovery plan  <people.yml>       pre-launch 1:1s: whom to meet, with reasons (relationship first)
  discovery tally <interviews.yml>   numbers, D-targets, fired rules, breaks nobody detects yet
  discovery card  [--check]          data/discovery.yml -> docs/DISCOVERY-CARD.md (the question card)
  member  check|card <card.yml>      a member card: school proof levels, roles it supports, personal loop
  discovery push  [--dir D] [--base URL]   private files -> the owner-only room at futuremake.io/honeycomb/room.html
  discovery pull  [--dir D] [--base URL]   phone notes from the room -> D/interviews.yml (then push again)
"""

from __future__ import annotations

import argparse
import json
import sys

from . import build, check, compass, discovery, member, federation, feed, learn, pulse, recruit
from pathlib import Path

import yaml

from .data import ROOT, charter_sha256, load, load_hive


def _check(a: argparse.Namespace) -> int:
    problems = check.check(load_hive(a.hive))
    for p in problems:
        print(f"✗ {p}")
    print("✓ hive keeps the charter" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def _pulse(a: argparse.Namespace) -> int:
    hive = load_hive(a.hive)
    numbers = pulse.pulse(hive)
    if a.json:
        print(json.dumps(numbers, indent=1))
        return 0
    if hive["hive"].get("simulated"):
        print("(simulated hive: these numbers prove the tools run; they are not the 10X)")
    print(json.dumps(numbers, indent=1))
    federated = {**numbers, "hives": len(federation.voting_hives(load("federation"))),
                 "cross_hive_builds_on": federation.cross_hive_builds_on(
                     [c for row in load("federation")["hives"] for c in federation.read_feed(row["feed"]).get("learnings", [])
                      if row.get("status") != "simulated"])}
    for row in pulse.verdict(federated, load("strategy")["targets"]):
        print(f"{'✅' if row['met'] else '⬜'} {row['id']} {row['measure']}: {row['value']}/{row['target']} by {row['due']}")
    return 0


def _recruit(a: argparse.Namespace) -> int:
    for role, ranked in recruit.suggest(load_hive(a.hive), a.cell).items():
        print(f"{role}:")
        for r in ranked:
            print(f"  {r['member']} ({r['points']} pts): " + "; ".join(r["reasons"]))
    print("A shortlist, not a decision: the CEO recruits.")
    return 0


def _drift(path: Path, text: str, check_only: bool) -> int:
    """Write `text` to `path`, or with check_only fail if it differs (the drift gate)."""
    if check_only:
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current != text:
            print(f"drift: {path.relative_to(ROOT)} is stale; regenerate and commit it", file=sys.stderr)
            return 1
        print(f"ok: {path.relative_to(ROOT)} is current")
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")
    return 0


def _publish(a: argparse.Namespace) -> int:
    """Build a hive's public feed; refuse if the hive breaks the charter or the feed names anyone."""
    hive = load_hive(a.hive)
    f = feed.build_feed(hive)
    problems = check.check(hive) + feed.leaks(f, hive)
    for p in problems:
        print(f"✗ {p}")
    if problems:
        print("not published: fix the hive first (a feed must keep the charter and name no one)")
        return 1
    out = Path(a.out) if a.out else Path(a.hive).with_name("feed.json")
    text = feed.render(f)
    rc = _drift(out.resolve(), text, a.check)
    key = Path(a.key) if a.key else _key_for(f["hive"], Path(a.hive))
    if key and key.exists():  # signed feed: any mirror or relay can carry it untrusted
        from . import sign
        rc |= _drift(out.with_name(out.name + ".sig").resolve(), sign.sign(text, key), a.check)
    return rc


def _key_for(hive_id: str, hive_path: Path) -> Path | None:
    """The hive's private signing key: hives-private/keys/<id>.key, or a simulated hive's committed TEST key."""
    for p in (ROOT / "hives-private" / "keys" / f"{hive_id}.key", hive_path.with_name("TEST-ONLY-signing.key")):
        if p.exists():
            return p
    return None


def _learn(a: argparse.Namespace) -> int:
    """Print the learning cards (any hive) most relevant to one cell."""
    hive = load_hive(a.hive)
    index = json.loads(Path(a.index).read_text(encoding="utf-8")) if a.index else federation.build_index()
    cell = next(c for c in hive["cells"] if c["id"] == a.cell)
    for r in learn.rank(cell, hive["hive"]["id"], index["learnings"]):
        print(f"{'🌐' if r['cross_hive'] else '🏠'} {r['id']} ({r['points']} pts; {'; '.join(r['reasons'])})\n   learned: {r['learned']}")
    print("Cite the ones you use in the cell's builds_on: that is how the federation counts compounding.")
    return 0


def _federation(a: argparse.Namespace) -> int:
    """federation hash | check | pull [--check]."""
    if a.action == "hash":
        print(charter_sha256())
        return 0
    if a.action == "pull":
        index = federation.build_index()
        for h in index["hives"]:
            print(f"  {h['id']}: charter {h['charter']} · heartbeat {h['heartbeat']} ({h['latest_season']})")
        print(f"  {len(index['learnings'])} learning cards · {index['cross_hive_builds_on']} cross-hive builds_on · "
              f"{len(index['open_seats'])} open seats · {len(index['ripe'])} ripe draft(s)")
        return _drift(federation.INDEX, federation.render_index(index), a.check)
    problems = federation.check()
    for p in problems:
        print(f"✗ {p}")
    print("✓ federation registry verified" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def _room_request(method: str, base: str, body: dict | None = None) -> dict:
    """Call the owner-only room API with HONEYCOMB_OWNER_TOKEN (never printed, never stored in the repo)."""
    import os
    import urllib.request

    from . import owner

    token = owner.secret()
    if not token:
        raise SystemExit("no owner passphrase on this Mac (env, agentic-portfolio/.env.local, or the keychain)")
    data = json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    req = urllib.request.Request(f"{base.rstrip('/')}/api/honeycomb-room", data=data, method=method,
                                 headers={"content-type": "application/json", "x-portfolio-owner": token,
                                          "user-agent": "honeycomb-cli"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def _room(a: argparse.Namespace) -> int:
    """discovery push | pull: keep the private room on futuremake.io in step with the private files."""
    import datetime as dt

    d = Path(a.dir)
    read = lambda n, default: (yaml.safe_load((d / n).read_text(encoding="utf-8")) if (d / n).exists() else None) or default
    ivs = read("interviews.yml", {}).get("interviews") or []
    if a.action == "pull":
        notes = _room_request("GET", a.base).get("notes") or []
        ivs, added = discovery.merge_notes(ivs, notes)
        (d / "interviews.yml").write_text("# PRIVATE (gitignored). One entry per 1:1; phone notes are merged by `discovery pull`.\n"
                                          + yaml.safe_dump({"interviews": ivs}, allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(f"pulled {len(notes)} note(s), {added} new -> {d / 'interviews.yml'}")
        return 0
    me_path = Path(a.me)
    me = yaml.safe_load(me_path.read_text(encoding="utf-8")) if me_path.exists() else None
    room = discovery.build_room(read("people.yml", {}), read("names.yml", {}), read("briefs.yml", {}), ivs,
                                today=dt.date.today().isoformat(), me=me)
    out = _room_request("PUT", a.base, {"room": room})
    print(f"pushed room: {len(room['people'])} people, seats {room['numbers']['seats_committed']}/12 -> {a.base}/honeycomb/room.html"
          if out.get("ok") else f"push failed: {out}")
    return 0 if out.get("ok") else 1


def _discovery(a: argparse.Namespace) -> int:
    """discovery plan <people> | tally <interviews> | card [--check] | push | pull."""
    if a.action in ("push", "pull"):
        return _room(a)
    if a.action == "card":
        return _drift(ROOT / "docs" / "DISCOVERY-CARD.md", discovery.card(), a.check)
    if not a.file:
        print(f"discovery {a.action} needs a file (keep real ones in hives-private/discovery/)", file=sys.stderr)
        return 2
    with open(a.file, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh) or {}
    if a.action == "plan":
        out = discovery.plan(doc)
        for k, p in enumerate(out["picks"], 1):
            where = "in person" if p["in_person"] else "video"
            print(f"{k}. {p['id']} [{p['kind']}, {where}]: " + "; ".join(p["reasons"]))
        print("voices per group: " + ", ".join(f"{s} {n}" for s, n in sorted(out["voices"].items())))
        print("gaps (under 2 voices): " + (", ".join(out["gaps"]) or "none"))
        print("A plan, not a decision. Give first: ask what they are building before you ask anything.")
        return 0
    t = discovery.tally(doc.get("interviews", []))
    if a.json:
        print(json.dumps(t, ensure_ascii=False, indent=1))
        return 0
    print(json.dumps(t["numbers"], ensure_ascii=False, indent=1))
    for row in t["targets"]:
        print(f"{'✅' if row['met'] else '⬜'} {row['id']} {row['measure']}: {row['value']}/{row['target']}")
    for r in t["fired"]:
        print(f"⚑ {r['id']} fires ({r['when']}): {r['then_en']}")
    for b in t["undetected"]:
        print(f"👁 {b}: raised, and nothing detects it yet. Build a detector or a fix (R2).")
    for b in t["unknown_breaks"]:
        print(f"? {b}: a new break. Add it to data/discovery.yml with a detector.")
    return 0


def _member(a: argparse.Namespace) -> int:
    """member check | card <card.yml>."""
    card = yaml.safe_load(Path(a.card).read_text(encoding="utf-8")) or {}
    if a.action == "card":
        print(member.one_pager(card), end="")
        return 0
    problems = member.check(card)
    for s in card.get("schools", []):
        lv = member.level(s)
        print(f"  {lv['school']}: {lv['name']} ({lv['points']} pts: {', '.join(lv['kinds']) or 'no proof yet'})")
    for p in problems:
        print(f"✗ {p}")
    print("✓ card supports what it asks for" if not problems else f"{len(problems)} thing(s) not yet supported")
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    """Parse argv and run one command; return its exit code."""
    parser = argparse.ArgumentParser(prog="honeycomb", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check"); p.add_argument("hive"); p.set_defaults(fn=_check)
    p = sub.add_parser("pulse"); p.add_argument("hive"); p.add_argument("--json", action="store_true"); p.set_defaults(fn=_pulse)
    p = sub.add_parser("recruit"); p.add_argument("hive"); p.add_argument("cell"); p.set_defaults(fn=_recruit)
    p = sub.add_parser("federation"); p.add_argument("action", choices=["check", "hash", "pull"])
    p.add_argument("--check", action="store_true"); p.set_defaults(fn=_federation)
    p = sub.add_parser("publish"); p.add_argument("hive"); p.add_argument("--out"); p.add_argument("--check", action="store_true")
    p.add_argument("--key", help="private Ed25519 key (default hives-private/keys/<hive>.key)")
    p.set_defaults(fn=_publish)
    p = sub.add_parser("learn"); p.add_argument("hive"); p.add_argument("cell"); p.add_argument("--index"); p.set_defaults(fn=_learn)
    p = sub.add_parser("compass"); p.add_argument("answers", nargs=8, type=int)
    p.set_defaults(fn=lambda a: print(json.dumps(compass.score(a.answers), indent=1)) or 0)
    p = sub.add_parser("discovery"); p.add_argument("action", choices=["plan", "tally", "card", "push", "pull"]); p.add_argument("file", nargs="?")
    p.add_argument("--dir", default="hives-private/discovery"); p.add_argument("--base", default="https://futuremake.io")
    p.add_argument("--me", default="hives-private/members/paul.yml")
    p.add_argument("--check", action="store_true"); p.add_argument("--json", action="store_true"); p.set_defaults(fn=_discovery)
    p = sub.add_parser("member"); p.add_argument("action", choices=["check", "card"]); p.add_argument("card")
    p.set_defaults(fn=_member)
    p = sub.add_parser("build"); p.add_argument("--check", action="store_true")
    p.set_defaults(fn=lambda a: build.main(check=a.check))
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
