"""Measure whether mainland China can load the site, using free Globalping probes (no key needed).

    python3 scripts/china_probe.py                 # probe live_url and mirror_url from data/site.yml
    python3 scripts/china_probe.py https://x.y/    # probe one URL

Prints one row per probe and a summary per URL; exits 1 if the mirror is reachable from fewer than
half the probes. Globalping's free tier is rate-limited, so run it once per deploy, not in CI.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

API = "https://api.globalping.io/v1/measurements"
ROOT = Path(__file__).resolve().parents[1]


def _post(body: dict) -> str:
    """Start a measurement; return its id."""
    req = urllib.request.Request(API, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["id"]


def _get(mid: str) -> dict:
    """Poll until the measurement finishes (max ~60 s)."""
    for _ in range(20):
        with urllib.request.urlopen(f"{API}/{mid}", timeout=30) as r:
            data = json.load(r)
        if data["status"] != "in-progress":
            return data
        time.sleep(3)
    return data


def probe(url: str, limit: int = 8) -> tuple[int, int]:
    """HTTP GET `url` from up to `limit` mainland probes; return (ok, total)."""
    u = urllib.parse.urlparse(url)
    mid = _post({"type": "http", "target": u.hostname, "locations": [{"country": "CN", "limit": limit}],
                 "measurementOptions": {"protocol": "HTTPS", "request": {"path": u.path or "/", "method": "GET"}}})
    results = _get(mid)["results"]
    ok = 0
    for r in results:
        res, p = r["result"], r["probe"]
        good = res.get("statusCode") == 200
        ok += good
        print(f"  {'✓' if good else '✗'} {p['city']:<10} {p.get('network', '')[:26]:<26} "
              f"{res.get('statusCode')} {(res.get('timings') or {}).get('total')} ms")
    print(f"{url}: {ok}/{len(results)} mainland probes OK")
    return ok, len(results)


def main(argv: list[str]) -> int:
    """Probe the given URL, or both site URLs; fail if the mirror is mostly unreachable."""
    if argv:
        ok, total = probe(argv[0])
        return 0 if total and ok * 2 >= total else 1
    site = yaml.safe_load((ROOT / "data" / "site.yml").read_text(encoding="utf-8"))
    probe(site["live_url"] + "/")
    ok, total = probe(site["mirror_url"] + "/")
    return 0 if total and ok * 2 >= total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
