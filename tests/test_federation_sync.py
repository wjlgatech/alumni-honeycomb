"""Synchronize · harmonize · compound: the federation mechanisms (docs/FEDERATION.md)."""

import copy
import datetime as dt
import json

import pytest

from honeycomb import check, federation, feed, learn
from honeycomb.data import ROOT, load, load_hive

A, B = ROOT / "hives" / "example" / "hive.yml", ROOT / "hives" / "example-b" / "hive.yml"


@pytest.mark.parametrize("day,season", [(dt.date(2026, 1, 1), "2026-S1"), (dt.date(2026, 3, 31), "2026-S1"),
                                        (dt.date(2026, 7, 1), "2026-S3"), (dt.date(2026, 12, 31), "2026-S4")])
def test_one_clock_for_every_hive(day, season):
    assert feed.season_of(day) == season


def test_previous_season_wraps_the_year():
    assert feed.previous_season("2027-S1") == "2026-S4" and feed.previous_season("2026-S3") == "2026-S2"


def test_season_ids_must_follow_the_clock():
    hive = load_hive(A)
    hive["seasons"][0]["start"] = dt.date(2026, 6, 1)
    assert any("clock: season 2026-S3" in p for p in check.check(hive))


def test_closed_cell_must_share_its_learning():
    hive = load_hive(A)
    cell = next(c for c in hive["cells"] if c["status"] == "closed")
    cell["outcome"].pop("learned")
    cell["tags"] = []
    problems = check.check(hive)
    assert any("no outcome.learned" in p for p in problems) and any("no tags" in p for p in problems)


def test_builds_on_must_name_a_card():
    hive = load_hive(B)
    hive["cells"][0]["builds_on"] = ["just some text"]
    assert any("builds_on" in p for p in check.check(hive))


def test_feed_names_no_one():
    for path in (A, B):
        hive = load_hive(path)
        f = feed.build_feed(hive)
        assert feed.leaks(f, hive) == []
        text = json.dumps(f)
        assert "members" not in f and "guardian" not in text and "contact" not in text


def test_a_leaking_feed_is_caught():
    hive = load_hive(A)
    f = feed.build_feed(hive)
    f["learnings"][0]["learned"] = "Mei did most of the work"
    assert any("s-mei" in p for p in feed.leaks(f, hive))


def test_feed_is_deterministic_and_committed():
    for path in (A, B):
        assert feed.render(feed.build_feed(load_hive(path))) == (path.parent / "feed.json").read_text(encoding="utf-8")


def test_open_seats_count_what_is_missing():
    seats = feed.build_feed(load_hive(B))["open_seats"]
    assert seats == [{"id": "example-b/c-history-ai", "hive": "example-b", "season": "2026-S4",
                      "tags": ["ai-study", "humanities"], "vision": seats[0]["vision"],
                      "needs": {"advisors": 1, "core": 1, "apprentices": 2}}]


def test_index_syncs_harmonizes_and_compounds():
    ix = federation.build_index()
    status = {h["id"]: (h["charter"], h["heartbeat"]) for h in ix["hives"]}
    assert status == {"example": ("current", "current"), "example-b": ("older: re-sign", "current")}
    assert ix["season_now"] == "2026-S4" and ix["charter_latest"] == "1.1.0"
    assert ix["cross_hive_builds_on"] == 2
    assert [r["tag"] for r in ix["ripe"]] == ["ai-study"] and ix["ripe"][0]["status"] == "draft"
    assert ix["totals"]["members"] == 18


def test_index_is_committed():
    assert federation.render_index(federation.build_index()) == federation.INDEX.read_text(encoding="utf-8")


def test_a_late_heartbeat_is_flagged():
    reg = load("federation")
    f = feed.build_feed(load_hive(B))
    f["latest_season"] = "2026-S2"
    assert federation.sync_status(f, reg, "2026-S4")["heartbeat"] == "late"


def test_an_unratified_signature_fails_the_check():
    reg = copy.deepcopy(load("federation"))
    reg["charters"] = [c for c in reg["charters"] if c["version"] != "1.0.0"]
    assert any("example-b" in p for p in federation.check(reg))


def test_founding_decisions_only_before_three_voting_hives():
    reg = copy.deepcopy(load("federation"))
    assert federation.check(reg) == []
    reg["hives"] += [{"id": f"h{i}", "status": "active", "feed": "hives/example/feed.json"} for i in range(3)]
    assert any("CP-001" in p and "founding" in p for p in federation.check(reg))


def test_ripe_needs_two_hives_not_just_three_cards():
    cards = [{"id": f"a/c{i}", "hive": "a", "tags": ["x"]} for i in range(5)]
    assert federation.ripe_patterns(cards) == []
    cards.append({"id": "b/c1", "hive": "b", "tags": ["x"]})
    assert federation.ripe_patterns(cards)[0]["hives"] == ["a", "b"]


def test_learn_ranks_cross_hive_cards():
    hive = load_hive(B)
    cell = next(c for c in hive["cells"] if c["id"] == "c-history-ai")
    ranked = learn.rank(cell, "example-b", federation.build_index()["learnings"])
    assert ranked[0]["points"] >= ranked[-1]["points"]
    assert any(r["cross_hive"] and r["id"] == "example/c-ai-tutor" for r in ranked)
    assert all(r["id"] != "example-b/c-history-ai" for r in ranked)
