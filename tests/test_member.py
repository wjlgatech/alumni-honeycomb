"""The member card: proof levels per school, roles the card can support, honest hours, the personal loop."""

import copy

import yaml

from honeycomb import member
from honeycomb.data import ROOT

LIN = yaml.safe_load((ROOT / "hives" / "example" / "members" / "lin.yml").read_text(encoding="utf-8"))


def school(*kinds, **circles):
    return {"name": "S", "relation": "alumnus", "evidence": [{"kind": k, "circle": circles.get(k, "")} for k in kinds]}


def test_example_card_is_confirmed_and_clean():
    assert member.level(LIN["schools"][0])["name"] == "confirmed"
    assert member.check(LIN) == []


def test_self_and_linkedin_never_count():
    assert member.level(school("self", "self"))["level"] == 0


def test_peers_alone_never_confirm():
    s = {"name": "S", "evidence": [{"kind": "vouch", "circle": c} for c in ("lab 2003", "class of 92", "church", "team")]}
    lv = member.level(s)
    assert lv["points"] == 3 and lv["level"] == 1  # max 3 vouches, and confirmed needs a non-peer kind


def test_same_circle_vouches_count_once_and_bare_vouches_not_at_all():
    s = {"name": "S", "evidence": [{"kind": "vouch", "circle": "Lab A"}, {"kind": "vouch", "circle": "lab a"}, {"kind": "vouch"}]}
    assert member.level(s)["points"] == 1


def test_old_graduate_reaches_confirmed_without_a_registry():
    s = {"name": "S", "evidence": [{"kind": "public_record"}, {"kind": "vouch", "circle": "math class 92"},
                                   {"kind": "vouch", "circle": "dorm 3"}]}
    assert member.level(s)["name"] == "confirmed"


def test_advisor_needs_a_supported_school():
    c = copy.deepcopy(LIN)
    c["schools"][0]["evidence"] = [{"kind": "self"}]
    assert any("advisor" in p for p in member.check(c))


def test_hours_must_cover_the_roles():
    c = copy.deepcopy(LIN)
    c["roles"], c["hours_per_week"] = ["ceo", "advisor"], 3
    assert any("need about 5 h/week" in p for p in member.check(c))


def test_capacity_and_minors_and_conflicts():
    c = copy.deepcopy(LIN)
    c["roles"] = ["ceo", "ceo"]
    c["works_with_minors"] = True
    c["interests"] = [{"what": "my company", "commercial": True}]
    problems = " ".join(member.check(c))
    assert "P5" in problems and "minors" in problems and "conflict" in problems


def test_loop_health_compares_given_with_promised():
    c = copy.deepcopy(LIN)
    c["weekly"] = [{"hours_given": 2, "next_step": "a"}, {"hours_given": 4, "kept_last_step": True, "next_step": "b"}]
    h = member.loop_health(c)
    assert (h["weeks"], h["avg_hours_given"], h["promised"], h["steps_kept"], h["steps_due"]) == (2, 3.0, 4, 1, 1)


def test_one_pager_never_says_verified():
    page = member.one_pager(LIN)
    assert "confirmed" in page and "verified" not in page.lower()


def test_every_member_is_introduced_except_founders():
    c = copy.deepcopy(LIN)
    del c["invited_by"]
    assert any("invited_by" in p for p in member.check(c))
    c["founder"] = True
    assert not any("invited_by" in p for p in member.check(c))


def test_duplicates_by_contact_or_by_name_school_years():
    a = copy.deepcopy(LIN)
    b = copy.deepcopy(LIN) | {"id": "a-lin-2", "anchor": "LIN@example.org "}
    c = copy.deepcopy(LIN) | {"id": "a-lin-3", "anchor": "other@example.org"}
    pairs = member.duplicates([a, b, c])
    assert ("a-lin", "a-lin-2", "same contact") in pairs
    assert any(p[1] == "a-lin-3" and "name, school" in p[2] for p in pairs)
