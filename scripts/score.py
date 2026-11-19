"""The ratchet: measure this repo, gate on a floor that only moves up, and write the scorecard.

PORTABLE TEMPLATE — copy to <repo>/scripts/score.py and edit the CONFIG block below. Nothing else
needs changing; it is stdlib-only and works on any Python repo. See ADOPT.md next to this file.

Why it exists: a README can *claim* quality; this computes it, fails the build when it slips, and
records every run so the trend is visible. That is the closed loop —
**measure → gate → improve → raise the floor** — applied to the repo itself.

    python3 scripts/score.py            # measure, write docs/SCORECARD.md, gate on the floor
    python3 scripts/score.py --bump     # ALSO raise the floor to today's score (after a real gain)
    python3 scripts/score.py --json     # the numbers, for a CI step or an agent

Stdlib only (``ast``), so it runs in CI where the private `anyagent` CLI is not installed. When
`anyagent` *is* on PATH, its independent OOP score is recorded alongside as a cross-check.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# ── CONFIG (edit these three lines per repo) ─────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = ("honeycomb", "scripts")  # graded for docs/typing/size/nesting
TEST_DIR = "tests"  # counted, not graded: a test's name is its docstring
# ─────────────────────────────────────────────────────────────────────────────
FLOOR_FILE = ROOT / "data" / "quality-floor.json"
HISTORY_FILE = ROOT / "data" / "quality-history.jsonl"
SCORECARD = ROOT / "docs" / "SCORECARD.md"

MAX_FUNCTION_LINES = 50
MAX_NESTING = 3
# Each metric is worth this many points; the weights say what this repo believes matters.
WEIGHTS = {"documented": 30, "sized": 20, "shallow": 15, "typed": 15, "tested": 20}


@dataclass
class Metrics:
    """Everything the ratchet measures, plus the offenders behind each number."""

    files: int = 0
    functions: int = 0
    classes: int = 0
    documented: float = 0.0
    sized: float = 0.0
    shallow: float = 0.0
    typed: float = 0.0
    tested: float = 0.0
    tests: int = 0
    score: int = 0
    anyagent_oop: int | None = None
    offenders: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        """The row recorded in the history file."""
        return {
            "score": self.score,
            "documented": round(self.documented, 1),
            "sized": round(self.sized, 1),
            "shallow": round(self.shallow, 1),
            "typed": round(self.typed, 1),
            "tested": round(self.tested, 1),
            "tests": self.tests,
            "files": self.files,
            "functions": self.functions,
            "classes": self.classes,
            "anyagent_oop": self.anyagent_oop,
        }


def python_files(*dirs: str) -> list[Path]:
    """Every tracked Python file under the given dirs (no caches, no virtualenv)."""
    out: list[Path] = []
    for directory in dirs:
        out += [p for p in sorted((ROOT / directory).rglob("*.py")) if "__pycache__" not in p.parts and ".venv" not in p.parts]
    return out


def count_tests() -> int:
    """Test functions in ``tests/`` — the count `make check` must never silently lose."""
    total = 0
    for path in python_files(TEST_DIR):
        total += sum(1 for n in ast.walk(ast.parse(path.read_text())) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_"))
    return total


@dataclass
class Tally:
    """Running counts while walking the AST: how many of each thing, and how many pass."""

    documented: int = 0
    documentable: int = 0
    typed: int = 0
    typeable: int = 0
    sized: int = 0
    shallow: int = 0


def nesting_depth(node: ast.AST, depth: int = 0) -> int:
    """How deeply the body of a function branches or loops (the readability proxy)."""
    deepest = depth
    for child in ast.iter_child_nodes(node):
        step = 1 if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.AsyncFor, ast.AsyncWith)) else 0
        deepest = max(deepest, nesting_depth(child, depth + step))
    return deepest


def function_lines(fn: ast.AST) -> int:
    """Body length in source lines (a docstring-only stub counts as small)."""
    return (getattr(fn, "end_lineno", fn.lineno) or fn.lineno) - fn.lineno + 1


def is_typed(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """A function counts as typed when it annotates its return and every real argument."""
    args = [a for a in (*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs) if a.arg not in ("self", "cls")]
    return fn.returns is not None and all(a.annotation is not None for a in args)


def measure() -> Metrics:
    """Walk the AST of every graded file and turn it into one 0-100 score."""
    m, tally = Metrics(), Tally()
    for path in python_files(*SOURCE_DIRS):
        m.files += 1
        _measure_file(ast.parse(path.read_text()), path.relative_to(ROOT), m, tally)
    m.tests = count_tests()

    m.documented = _pct(tally.documented, tally.documentable)
    m.typed = _pct(tally.typed, tally.typeable)
    m.sized = _pct(tally.sized, m.functions)
    m.shallow = _pct(tally.shallow, m.functions)
    m.tested = min(100.0, 100.0 * m.tests / max(1, m.functions * 0.5))  # ~1 test per 2 functions = full marks
    m.score = round(sum(WEIGHTS[k] * getattr(m, k) / 100 for k in WEIGHTS))
    m.anyagent_oop = anyagent_oop_score()
    return m


def _measure_file(tree: ast.Module, rel: Path, m: Metrics, tally: Tally) -> None:
    """Score one module: its own docstring, then every class and function inside it."""
    tally.documentable += 1
    tally.documented += 1 if ast.get_docstring(tree) else 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            m.classes += 1
            tally.documentable += 1
            tally.documented += 1 if ast.get_docstring(node) else 0
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            m.functions += 1
            _measure_function(node, rel, m, tally)


def _measure_function(node: ast.AST, rel: Path, m: Metrics, tally: Tally) -> None:
    """Docstring, annotations, length and nesting for one function; record any offender."""
    tally.documentable += 1
    tally.documented += 1 if ast.get_docstring(node) else 0
    tally.typeable += 1
    tally.typed += 1 if is_typed(node) else 0
    lines, depth = function_lines(node), nesting_depth(node)
    tally.sized += 1 if lines <= MAX_FUNCTION_LINES else 0
    tally.shallow += 1 if depth <= MAX_NESTING else 0
    if lines > MAX_FUNCTION_LINES:
        m.offenders.append(f"[oversized] {rel}:{node.name} is {lines} lines (>{MAX_FUNCTION_LINES})")
    if depth > MAX_NESTING:
        m.offenders.append(f"[deep-nesting] {rel}:{node.name} nests {depth} deep (>{MAX_NESTING})")


def _pct(got: int, total: int) -> float:
    """Percentage, treating "nothing to grade" as full marks rather than a divide-by-zero."""
    return 100.0 * got / total if total else 100.0


def anyagent_oop_score() -> int | None:
    """The independent second opinion — opt-in, because it runs its own (slow) analysis.

    Enable with ``--second-opinion`` or ``COLAB_SECOND_OPINION=1``; the ratchet itself never waits
    on it, so `make check` stays under a second.
    """
    if not (os.environ.get("SECOND_OPINION") == "1" or "--second-opinion" in sys.argv):
        return None
    if not shutil.which("anyagent"):
        return None
    try:
        out = subprocess.run(["anyagent", "analyze", str(ROOT)], capture_output=True, text=True, timeout=180).stdout
    except (subprocess.SubprocessError, OSError):
        return None
    m = re.search(r"OOP quality:\s*(\d+)/100", out)
    return int(m.group(1)) if m else None


def load_floor() -> dict:
    """The bar this repo has already cleared. Missing file = no bar yet."""
    return json.loads(FLOOR_FILE.read_text()) if FLOOR_FILE.exists() else {}


def check_floor(m: Metrics, floor: dict) -> list[str]:
    """Every metric that fell below the recorded floor (the ratchet only ever tightens)."""
    failures = []
    for key, minimum in floor.items():
        if key == "updated":
            continue
        current = m.tests if key == "tests" else (m.score if key == "score" else getattr(m, key, None))
        if current is None:
            continue
        if current < minimum:
            failures.append(f"{key}: {current} < floor {minimum}")
    return failures


def write_history(m: Metrics) -> list[dict]:
    """Append one line per run; the scorecard's trend is read back from here."""
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    entry = {"at": datetime.now(timezone.utc).strftime("%Y-%m-%d"), **m.as_dict()}
    previous = read_history()
    if not previous or previous[-1] != entry:  # any changed number is worth a row, not just the score
        with HISTORY_FILE.open("a") as fh:
            fh.write(json.dumps(entry) + "\n")
    return read_history()


def read_history() -> list[dict]:
    """Every recorded run, oldest first."""
    if not HISTORY_FILE.exists():
        return []
    return [json.loads(line) for line in HISTORY_FILE.read_text().splitlines() if line.strip()]


def write_scorecard(m: Metrics, floor: dict, history: list[dict]) -> None:
    """Regenerate ``docs/SCORECARD.md``. Generated, so it cannot drift from the code."""
    rows = "\n".join(
        f"| `{k}` | {round(getattr(m, k), 1)}% | {WEIGHTS[k]} | {floor.get(k, '—')} | {_metric_meaning(k)} |" for k in WEIGHTS
    )
    trend = "\n".join(f"| {h['at']} | {h['score']} | {h['tests']} | {h.get('anyagent_oop') or '—'} |" for h in history[-10:])
    second_opinion = (
        f"`anyagent analyze` (independent OOP scorer): **{m.anyagent_oop}/100**"
        if m.anyagent_oop is not None
        else "_Second opinion not run — it is opt-in because it is slow: `make score ARGS=--second-opinion`._"
    )
    SCORECARD.write_text(
        f"""# Scorecard — generated, do not edit

`make score` writes this file. The numbers come from `scripts/score.py` walking the AST of
`{"`, `".join(SOURCE_DIRS)}` (tests are counted, not graded), so they cannot drift from the code the way a hand-written claim does.

## Today: **{m.score}/100**

{m.files} files · {m.functions} functions · {m.classes} classes · {m.tests} tests.
{second_opinion}

| Metric | Now | Weight | Floor | What it means |
|---|---:|---:|---:|---|
{rows}

## The ratchet

`data/quality-floor.json` is the bar already cleared. `make check` fails if any metric drops below
it, so quality cannot quietly regress. After a real improvement, `make score-bump` raises the floor
to the new number — the loop only tightens.

Floor today: {", ".join(f"`{k}` ≥ {v}" for k, v in sorted(floor.items()) if k != "updated") or "not set yet"}.

## Trend

| Date | Score | Tests | anyagent OOP |
|---|---:|---:|---:|
{trend}

{"### Offenders" + chr(10) + chr(10) + chr(10).join("- " + o for o in m.offenders) if m.offenders else "No function is over "
 f"{MAX_FUNCTION_LINES} lines or nested deeper than {MAX_NESTING}."}
"""
    )


def _metric_meaning(key: str) -> str:
    """One plain sentence per metric, for the generated scorecard."""
    return {
        "documented": f"modules, classes and functions with a docstring — the two-reader rule, machine-checked",
        "sized": f"functions ≤ {MAX_FUNCTION_LINES} lines (one function, one job)",
        "shallow": f"functions nested ≤ {MAX_NESTING} deep (readable branching)",
        "typed": "functions annotating every argument and their return",
        "tested": "test functions vs production functions (~1 per 2 = 100%)",
    }[key]


def main(argv: list[str] | None = None) -> int:
    """Measure, write, and gate. Exit 1 when a metric fell below the floor."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bump", action="store_true", help="raise the floor to today's numbers (only ever upward)")
    parser.add_argument("--json", action="store_true", help="print the metrics as JSON")
    parser.add_argument("--second-opinion", action="store_true", help="also run `anyagent analyze` (slow) and record its score")
    parser.add_argument("--no-write", action="store_true", help="measure and gate only; write nothing")
    args = parser.parse_args(argv)

    m = measure()
    floor = load_floor()
    failures = check_floor(m, floor)

    if not args.no_write:
        history = write_history(m)
        write_scorecard(m, floor, history)

    if args.bump:
        # Truncate, never round up: a floor above the measured value would fail its own next run.
        new_floor = {k: max(floor.get(k, 0), int(getattr(m, k))) for k in WEIGHTS}
        new_floor["score"] = max(floor.get("score", 0), m.score)
        new_floor["tests"] = max(floor.get("tests", 0), m.tests)
        new_floor["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        FLOOR_FILE.parent.mkdir(exist_ok=True)
        FLOOR_FILE.write_text(json.dumps(new_floor, indent=2, sort_keys=True) + "\n")
        write_scorecard(m, new_floor, read_history())
        print(f"↑ floor raised to score ≥ {new_floor['score']}, tests ≥ {new_floor['tests']}")
        return 0

    if args.json:
        print(json.dumps(m.as_dict(), indent=2))
    else:
        print(f"quality {m.score}/100 — " + " · ".join(f"{k} {round(getattr(m, k))}%" for k in WEIGHTS) + f" · {m.tests} tests")
        for offender in m.offenders:
            print(f"  • {offender}")

    if failures:
        print("✗ below the floor in data/quality-floor.json:", file=sys.stderr)
        for f in failures:
            print(f"  • {f}", file=sys.stderr)
        print("  fix it, or justify a lower bar by editing the floor deliberately.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
