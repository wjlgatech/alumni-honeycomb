"""Command line: python -m honeycomb <command> [...]

  check   <hive.yml>                 enforce the charter principles; exit 1 on any problem
  pulse   <hive.yml> [--json]        vital signs + the 10X targets (aggregate numbers only)
  recruit <hive.yml> <cell-id>       draft a shortlist for a forming cell's empty seats
  publish <hive.yml> [--out F] [--check]   write the hive's PUBLIC feed (numbers, learning cards, open seats; no people)
  federation check | hash | pull [--check]   verify the registry / charter hash / merge all feeds -> federation/index.json
  learn   <hive.yml> <cell-id> [--index F]  what other cells (any hive) already learned that fits this cell
  compass 3 2 1 1 2 0 3 3            score 8 Calling Compass answers (0..3) in question order
  build   [--check]                  data/*.yml -> web/data.json
"""

from __future__ import annotations

import argparse
import json
import sys

from . import build, check, compass, federation, feed, learn, pulse, recruit
from pathlib import Path

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
    return _drift(out.resolve(), feed.render(f), a.check)


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
    p.set_defaults(fn=_publish)
    p = sub.add_parser("learn"); p.add_argument("hive"); p.add_argument("cell"); p.add_argument("--index"); p.set_defaults(fn=_learn)
    p = sub.add_parser("compass"); p.add_argument("answers", nargs=8, type=int)
    p.set_defaults(fn=lambda a: print(json.dumps(compass.score(a.answers), indent=1)) or 0)
    p = sub.add_parser("build"); p.add_argument("--check", action="store_true")
    p.set_defaults(fn=lambda a: build.main(check=a.check))
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
