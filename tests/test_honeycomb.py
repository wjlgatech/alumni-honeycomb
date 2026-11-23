"""Tests for the hive rules, pulse, recruit, federation and the compass. Run: python -m pytest -q"""

import copy
import datetime as dt
import json
import re
import subprocess
from pathlib import Path

import pytest

from honeycomb import build, check, compass, federation, pulse, recruit
from honeycomb.data import ROOT, charter_sha256, load, load_hive

HIVE = ROOT / "hives" / "example" / "hive.yml"


@pytest.fixture
def hive():
    return load_hive(HIVE)


def cell(h, cid):
    return next(c for c in h["cells"] if c["id"] == cid)


def test_example_hive_keeps_the_charter(hive):
    assert check.check(hive) == []


def test_active_cell_needs_full_shape(hive):
    cell(hive, "c-physics-ai")["core"] = ["s-jun"]
    assert any("has 1 core; needs 2-3" in p for p in check.check(hive))


def test_forming_cell_may_be_short(hive):
    assert cell(hive, "c-calling-salon")["status"] == "forming"
    assert not any("c-calling-salon has" in p for p in check.check(hive))


def test_advisor_must_be_alumnus(hive):
    cell(hive, "c-physics-ai")["advisors"] = ["a-lin", "s-tao"]
    assert any("advisor s-tao" in p for p in check.check(hive))


def test_same_person_twice_in_a_cell(hive):
    cell(hive, "c-physics-ai")["apprentices"] = ["s-hao", "s-jun"]
    assert any("s-jun appears twice" in p for p in check.check(hive))


def test_criteria_first(hive):
    cell(hive, "c-food-waste")["good"] = "it goes well"
    assert any("P2" in p for p in check.check(hive))


def test_closed_needs_evidence(hive):
    cell(hive, "c-ai-tutor")["outcome"] = {"learned": "x"}
    assert any("P3" in p for p in check.check(hive))


def test_checkin_needs_next_step(hive):
    hive["checkins"].append({"cell": "c-food-waste", "date": dt.date(2026, 11, 18), "next_step": " "})
    assert any("P4" in p for p in check.check(hive))


def test_capacity_one_ceo_per_season(hive):
    cell(hive, "c-food-waste")["ceo"] = "s-mei"
    cell(hive, "c-food-waste")["core"] = ["s-jun", "s-tao"]
    problems = check.check(hive)
    assert any("s-mei is CEO of 2 cells in 2026-S4" in p for p in problems)


def test_capacity_three_roles_per_season(hive):
    hive["cells"].append({"id": "x", "season": "2026-S4", "status": "forming", "ceo": "a-wang",
                          "vision": "v", "good": "Good: g", "advisors": [], "core": ["s-hao"], "apprentices": []})
    assert any("s-hao holds 3 roles" in p for p in check.check(hive)) is False
    hive["cells"].append({"id": "y", "season": "2026-S4", "status": "forming", "ceo": "a-lin",
                          "vision": "v", "good": "Good: g", "advisors": [], "core": ["s-hao"], "apprentices": []})
    assert any("s-hao holds 4 roles" in p for p in check.check(hive))


@pytest.mark.parametrize("field,value", [("phone", "x"), ("wechat", "x"), ("note", "mail me a@b.com"),
                                         ("note", "call 138 0013 8000")])
def test_no_contact_details(hive, field, value):
    hive["members"][0][field] = value
    assert any("P6 safety" in p for p in check.check(hive))


def test_minor_needs_guardian(hive):
    hao = next(m for m in hive["members"] if m["id"] == "s-hao")
    del hao["guardian"]
    assert any("under 18" in p for p in check.check(hive))


def test_pulse_numbers(hive):
    n = pulse.pulse(hive)
    assert n == {"season": "2026-S4", "members": 10, "cells_total": 4, "active_cells": 2,
                 "closed_with_evidence": 1, "role_switchers": 4, "ceo_share": 0.33, "checkins": 5}
    assert not set(json.dumps(n)) & set("@"), "pulse must stay aggregate"


def test_recruit_respects_roles_and_capacity(hive):
    s = recruit.suggest(hive, "c-calling-salon")
    members = {m["id"]: m for m in hive["members"]}
    assert all(members[r["member"]]["type"] == "alumnus" for r in s["advisors"])
    assert all(members[r["member"]]["type"] == "student" for r in s["apprentices"])
    assert "a-chen" not in [r["member"] for r in s["advisors"]]  # already in the cell


def test_federation_registry_verifies():
    assert federation.check() == []


def test_changed_charter_is_caught():
    reg = copy.deepcopy(load("federation"))
    current = str(load("charter")["version"])
    next(c for c in reg["charters"] if str(c["version"]) == current)["sha256"] = "0" * 64
    assert any("charter:" in p for p in federation.check(reg))


def test_two_thirds_vote():
    reg = {"hives": [{"id": h} for h in "abc"]}
    assert federation.ratified({"votes": {"a": "yes", "b": "yes"}}, reg)
    assert not federation.ratified({"votes": {"a": "yes", "b": "no"}}, reg)
    assert not federation.ratified({"votes": {"x": "yes"}}, {"hives": [{"id": "x", "status": "simulated"}]})


def test_compass_golden_cases():
    spec = load("compass")
    for case in spec["golden"]:
        r = compass.score(case["answers"], spec)
        assert r["levels"] == case["levels"] and r["start"] == case["start"], case


def test_compass_rejects_bad_input():
    with pytest.raises(ValueError):
        compass.score([0] * 7)
    with pytest.raises(ValueError):
        compass.score([4] + [0] * 7)


def test_browser_compass_matches_golden_cases():
    node = subprocess.run(["node", str(ROOT / "tests" / "compass.test.mjs")], capture_output=True, text=True)
    assert node.returncode == 0, node.stdout + node.stderr


def test_site_data_has_no_drift():
    assert build.main(check=True) == 0


def test_site_loads_nothing_from_other_domains():
    """China access: every asset is same-origin and relative, so the same folder works on any host or sub-path
    (Vercel, GitHub Pages mirror). Blocked CDNs/fonts are the #1 reason a page hangs in China."""
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    for tag in re.findall(r"<(?:script|link|img|iframe)[^>]*>", html):
        for url in re.findall(r"(?:src|href)=\"([^\"]+)\"", tag):
            assert "//" not in url and not url.startswith("/"), f"use a relative same-origin path: {url} in {tag}"
    assert "@import" not in html and "fonts.googleapis" not in html


def test_manifest_icons_exist():
    m = json.loads((ROOT / "web" / "manifest.webmanifest").read_text(encoding="utf-8"))
    for icon in m["icons"]:
        assert (ROOT / "web" / icon["src"]).stat().st_size > 100


def test_charter_hash_is_the_signed_one():
    reg = load("federation")
    assert federation.known_hashes(reg)[str(load("charter")["version"])] == charter_sha256()


def test_first_meeting_is_after_thanksgiving_and_link_stays_private():
    """Sat 2026-12-05 5 PM Pacific = Sun 2026-12-06 9 AM Beijing; the meeting URL never sits in the public repo."""
    from zoneinfo import ZoneInfo

    ev = load("events")["events"][0]
    start = dt.datetime.fromisoformat(str(ev["start_utc"]).replace("Z", "+00:00"))
    pacific, beijing = start.astimezone(ZoneInfo("America/Los_Angeles")), start.astimezone(ZoneInfo("Asia/Shanghai"))
    assert (pacific.strftime("%a %Y-%m-%d %H:%M"), beijing.strftime("%a %Y-%m-%d %H:%M")) == ("Sat 2026-12-05 17:00", "Sun 2026-12-06 09:00")
    assert pacific.date() > dt.date(2026, 11, 29), "must fall after the Thanksgiving weekend"
    for path in list((ROOT / "data").glob("*.yml")) + [ROOT / "web" / "index.html", ROOT / "web" / "data.json"]:
        assert "meet.google.com/" not in path.read_text(encoding="utf-8"), f"meeting link leaked into {path.name}"


def test_page_links_the_ecosystem():
    """Paul (2026-11-23): the honeycomb page links FM-SC, Stanford Eden, ALL-IN AI and the ecosystem hub."""
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    for url in ("https://fmsc.futuremake.io/", "https://eden.futuremake.io/", "https://futuremake.io/all-in-ai",
                "https://futuremake.io/hub/ecosystem"):
        assert f'url: "{url}"' in html
