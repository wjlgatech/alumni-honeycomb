# Scorecard — generated, do not edit

`make score` writes this file. The numbers come from `scripts/score.py` walking the AST of
`honeycomb`, `scripts` (tests are counted, not graded), so they cannot drift from the code the way a hand-written claim does.

## Today: **99/100**

15 files · 84 functions · 2 classes · 47 tests.
_Second opinion not run — it is opt-in because it is slow: `make score ARGS=--second-opinion`._

| Metric | Now | Weight | Floor | What it means |
|---|---:|---:|---:|---|
| `documented` | 96.0% | 30 | 96 | modules, classes and functions with a docstring — the two-reader rule, machine-checked |
| `sized` | 100.0% | 20 | 100 | functions ≤ 50 lines (one function, one job) |
| `shallow` | 100.0% | 15 | 100 | functions nested ≤ 3 deep (readable branching) |
| `typed` | 98.8% | 15 | 98 | functions annotating every argument and their return |
| `tested` | 100.0% | 20 | 100 | test functions vs production functions (~1 per 2 = 100%) |

## The ratchet

`data/quality-floor.json` is the bar already cleared. `make check` fails if any metric drops below
it, so quality cannot quietly regress. After a real improvement, `make score-bump` raises the floor
to the new number — the loop only tightens.

Floor today: `documented` ≥ 96, `score` ≥ 99, `shallow` ≥ 100, `sized` ≥ 100, `tested` ≥ 100, `tests` ≥ 47, `typed` ≥ 98.

## Trend

| Date | Score | Tests | anyagent OOP |
|---|---:|---:|---:|
| 2026-11-19 | 96 | 24 | — |
| 2026-11-19 | 97 | 27 | — |
| 2026-11-19 | 98 | 30 | — |
| 2026-11-23 | 99 | 47 | — |

No function is over 50 lines or nested deeper than 3.
