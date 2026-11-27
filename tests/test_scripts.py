"""Offline tests for the deploy scripts (network calls are replaced by fakes)."""

import importlib.util

from honeycomb.data import ROOT


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fake_results(codes):
    return {"status": "finished", "results": [
        {"probe": {"city": f"City{i}", "network": "net"}, "result": {"statusCode": c, "timings": {"total": 500}}}
        for i, c in enumerate(codes)]}


def test_china_probe_counts_ok_probes(monkeypatch, capsys):
    cp = _load("china_probe")
    sent = {}
    monkeypatch.setattr(cp, "_post", lambda body: sent.update(body) or "id1")
    monkeypatch.setattr(cp, "_get", lambda mid: _fake_results([200, 200, None, 200]))
    assert cp.probe("https://example.org/sub/") == (3, 4)
    assert sent["target"] == "example.org" and sent["locations"][0]["country"] == "CN"
    assert sent["measurementOptions"]["request"]["path"] == "/sub/"
    assert "3/4 mainland probes OK" in capsys.readouterr().out


def test_china_probe_fails_when_mirror_mostly_blocked(monkeypatch):
    cp = _load("china_probe")
    monkeypatch.setattr(cp, "_post", lambda body: "id")
    monkeypatch.setattr(cp, "_get", lambda mid: _fake_results([None, None, 200]))
    assert cp.main(["https://example.org/"]) == 1
    monkeypatch.setattr(cp, "_get", lambda mid: _fake_results([200, 200, None]))
    assert cp.main(["https://example.org/"]) == 0


def test_live_check_reports_bad_asset(monkeypatch, capsys):
    lc = _load("live_check")

    class Page:
        def read(self):
            return b'<link href="manifest.webmanifest"><script src="compass.js"></script><a href="https://x.org">'

    monkeypatch.setattr(lc.urllib.request, "urlopen", lambda *a, **k: Page())
    monkeypatch.setattr(lc, "status", lambda url: 404 if url.endswith("compass.js") else 200)
    assert lc.main("https://site.test/") == 1
    out = capsys.readouterr().out
    assert "✗ 404 https://site.test/compass.js" in out and "x.org" not in out


def test_signin_session_matches_the_owner_gate_format():
    """Same HMAC as agentic-portfolio lib/owner.ts: sess.<expMs>.<hex sha256 hmac of 'sess.<expMs>'>."""
    import hashlib
    import hmac
    import re
    from honeycomb import owner
    s = owner.mint_session("k", 1000, days=1)
    exp = 1000 + 24 * 3600 * 1000
    assert s == f"sess.{exp}." + hmac.new(b"k", f"sess.{exp}".encode(), hashlib.sha256).hexdigest()
    assert re.fullmatch(r"sess\.\d+\.[0-9a-f]{64}", s)
