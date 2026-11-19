"""Docs claims that must stay true: the live URL at the top of the README, and the numbers it states."""

from pathlib import Path

import yaml

from honeycomb import pulse
from honeycomb.data import ROOT, load, load_hive


def test_readme_opens_with_the_live_url_and_the_china_mirror():
    site = load("site")
    top = "\n".join((ROOT / "README.md").read_text(encoding="utf-8").splitlines()[:4])
    assert site["home_url"] in top and site["mirror_url"] in top


def test_readme_example_hive_claim_matches_pulse():
    n = pulse.pulse(load_hive(ROOT / "hives" / "example" / "hive.yml"))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    claim = f"({n['members']} people, {n['cells_total']} cells, 2 seasons, {n['role_switchers']} role-switchers)"
    assert claim in readme


def test_readme_10x_table_matches_strategy():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for t in load("strategy")["targets"]:
        assert f"| {t['id']} |" in readme and f"≥ {t['target']} | {t['due']} |" in readme
