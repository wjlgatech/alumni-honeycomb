"""Pre-launch discovery: the plan picks with reasons, the tally counts acts not words, rules are code."""

import copy

import pytest
import yaml

from honeycomb import discovery
from honeycomb.data import ROOT, load

EX = ROOT / "hives" / "example" / "discovery"


def _yaml(name):
    return yaml.safe_load((EX / name).read_text(encoding="utf-8"))


@pytest.fixture
def cfg():
    return load("discovery")


def test_every_rule_in_data_is_code_and_back(cfg):
    assert {r["id"] for r in cfg["rules"]} == set(discovery.RULES)


def test_every_question_answers_a_known_unknown_and_all_unknowns_are_asked(cfg):
    unknowns = {u["id"] for u in cfg["unknowns"]}
    asked = {q["unknown"] for q in cfg["questions"]}
    assert asked == unknowns


def test_questions_never_ask_would_you(cfg):
    for q in cfg["questions"]:
        assert "would you" not in q["en"].lower().replace("would you introduce", ""), q["n"]


def test_plan_fills_reserves_and_never_picks_trust_zero(cfg):
    out = discovery.plan(_yaml("people.yml"), cfg)
    ids = [p["id"] for p in out["picks"]]
    assert len(ids) == cfg["selection"]["max_meetings"]
    assert "H-famous" not in ids
    kinds = [p["kind"] for p in out["picks"]]
    assert kinds.count("end_user") == 2 and kinds.count("skeptic") == 1
    assert out["gaps"] == []


def test_plan_puts_three_hubs_in_the_first_hive_circle(cfg):
    out = discovery.plan(_yaml("people.yml"), cfg)
    hubs = [p for p in out["picks"] if p["kind"] == "hub"]
    assert sum(1 for p in hubs if p["cluster"] == "sysu-bay") == cfg["selection"]["cluster_voices"]
    assert all(p["reasons"] for p in out["picks"])


def test_plan_reports_a_gap_when_a_group_has_no_voice(cfg):
    people = _yaml("people.yml")
    people["people"] = [p for p in people["people"] if "organizer" not in p["segments"]]
    assert "organizer" in discovery.plan(people, cfg)["gaps"]


def test_seats_named_twice_count_once():
    ivs = [{"id": "a", "seats": [{"role": "advisor", "who": "A-1"}]},
           {"id": "b", "seats": [{"role": "advisor", "who": "A-1"}, {"role": "core"}, {"role": "core"}]}]
    assert discovery.numbers(ivs)["seats_committed"] == 3


def test_example_tally_targets_rules_and_blind_spots(cfg):
    t = discovery.tally(_yaml("interviews.yml")["interviews"], cfg)
    n = t["numbers"]
    assert (n["seats_committed"], n["ceo_candidates"], n["parent_value"]) == (7, 2, 1.5)
    assert {r["id"] for r in t["fired"]} == {"R2", "R3", "R4"}
    assert "faith_complaint" in t["undetected"] and "advisor_fade" not in t["undetected"]
    assert t["unknown_breaks"] == ["homework_load"]
    assert {r["id"]: r["met"] for r in t["targets"]}["D1"] is False


def test_compliments_are_not_seats(cfg):
    t = discovery.tally([{"id": "x", "rung": 0, "felt_heard": True}], cfg)
    assert t["numbers"]["seats_committed"] == 0 and any(r["id"] == "R5" for r in t["fired"])


def test_tally_numbers_name_no_one():
    ivs = _yaml("interviews.yml")["interviews"]
    text = str(discovery.numbers(copy.deepcopy(ivs)))
    for i in ivs:
        assert i["person"] not in text
        for s in i.get("seats", []):
            assert s.get("who", "@@") not in text


def test_card_is_current():
    assert (ROOT / "docs" / "DISCOVERY-CARD.md").read_text(encoding="utf-8") == discovery.card()
