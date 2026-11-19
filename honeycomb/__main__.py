"""Command line: python -m honeycomb <command> [...]

  check   <hive.yml>                 enforce the charter principles; exit 1 on any problem
  pulse   <hive.yml> [--json]        vital signs + the 10X targets (aggregate numbers only)
  recruit <hive.yml> <cell-id>       draft a shortlist for a forming cell's empty seats
  federation check | hash            verify the registry / print the charter hash a hive signs
  compass 3 2 1 1 2 0 3 3            score 8 Calling Compass answers (0..3) in question order
  build   [--check]                  data/*.yml -> web/data.json
"""

from __future__ import annotations

import argparse
import json
import sys

from . import build, check, compass, federation, pulse, recruit
from .data import charter_sha256, load, load_hive


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
    federated = {**numbers, "hives": len(federation.voting_hives(load("federation")))}
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


def _federation(a: argparse.Namespace) -> int:
    if a.action == "hash":
        print(charter_sha256())
        return 0
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
    p = sub.add_parser("federation"); p.add_argument("action", choices=["check", "hash"]); p.set_defaults(fn=_federation)
    p = sub.add_parser("compass"); p.add_argument("answers", nargs=8, type=int)
    p.set_defaults(fn=lambda a: print(json.dumps(compass.score(a.answers), indent=1)) or 0)
    p = sub.add_parser("build"); p.add_argument("--check", action="store_true")
    p.set_defaults(fn=lambda a: build.main(check=a.check))
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
