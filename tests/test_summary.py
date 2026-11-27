"""The Release Agreement: a meeting summary leaves a honeycomb only when everyone approved it and it names no one."""

import copy

import pytest

from honeycomb import feed, summary
from honeycomb.data import ROOT, load_hive


@pytest.fixture
def hive():
    return load_hive(ROOT / "hives" / "example" / "hive.yml")


def meeting(h, mid):
    return copy.deepcopy(next(m for m in h["meetings"] if m["id"] == mid))


def test_approved_summary_is_released_and_unapproved_is_held(hive):
    assert summary.check(meeting(hive, "m-2026-10-14"), hive) == []
    assert any("not yet approved by a-chen" in p for p in summary.check(meeting(hive, "m-2026-11-02"), hive))
    ids = [c["id"] for c in summary.released(hive, "hive")]
    assert ids == ["example/c-ai-tutor/m-2026-10-14"]


def test_released_card_carries_the_work_not_the_people(hive):
    c = summary.card(meeting(hive, "m-2026-10-14"), "example")
    assert "attendees" not in c and "approved_by" not in c
    assert feed.leaks({"x": c}, hive) == []


def test_a_minor_needs_a_guardian_yes(hive):
    m = meeting(hive, "m-2026-10-14")
    m["attendees"].append("s-hao")              # under 18 in the example hive
    m["approved_by"].append("s-hao")
    assert any("guardian:s-hao" in p for p in summary.check(m, hive))
    m["approved_by"].append("guardian:s-hao")
    assert summary.check(m, hive) == []


@pytest.mark.parametrize("field,value,why", [
    ("learned", "Lin (sim) said the Friday slot fails", "names a person"),
    ("asks", ["write to lin@example.org"], "email or phone"),
    ("asks", ["call 404-555-0123"], "email or phone"),
    ("learned", "one member was in hospital that week", "never leaves a meeting"),
    ("learned", "她最近很焦虑", "never leaves a meeting"),
])
def test_names_contacts_and_sensitive_topics_block_release(hive, field, value, why):
    m = meeting(hive, "m-2026-10-14")
    m[field] = value
    assert any(why in p for p in summary.check(m, hive))


def test_dates_are_not_phone_numbers():
    assert not summary.PHONE.search("decided 2026-10-14, next by 10-16")


def test_quotes_need_a_yes_and_25_words(hive):
    m = meeting(hive, "m-2026-10-14")
    m["quotes"] = [{"text": "word " * 26, "quote_ok": True}]
    assert any("quote" in p for p in summary.check(m, hive))
    m["quotes"] = [{"text": "short", "quote_ok": False}]
    assert any("quote" in p for p in summary.check(m, hive))


def test_feed_carries_only_federation_tier_summaries(hive):
    f = feed.build_feed(hive)
    assert [s["id"] for s in f["summaries"]] == ["example/c-ai-tutor/m-2026-10-14"]


def test_digest_ranks_by_shared_tags_and_caps(hive):
    cards = [{"id": "a", "tags": ["x"], "date": "2026-01-01"}, {"id": "b", "tags": ["x", "y"], "date": "2025-01-01"},
             {"id": "c", "tags": ["z"], "date": "2026-02-01"}]
    assert [c["id"] for c in summary.digest(cards, ["x", "y"], limit=5)] == ["b", "a"]
    assert len(summary.digest(cards * 10, ["x"], limit=3)) == 3
