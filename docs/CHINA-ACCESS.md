# China access

**Goal:** a student in Guangzhou or Beijing opens the link inside WeChat and the page loads in a few seconds.

## What the page already does

| Risk | Handling | Gate |
|---|---|---|
| Blocked foreign fonts/CDNs make a page hang | Every asset is same-origin; system Chinese fonts | `tests/test_honeycomb.py::test_site_loads_nothing_from_other_domains` |
| Heavy pages time out on slow links | One HTML file, one small JSON, tiny PNG icons, no framework | page weight is visible in `make live-check` |
| WeChat in-app browser | No login, no cookies needed; install hint says "Open in browser" | manual check (eval: Paul) |

## What the host decides (measured 2026-11-19, Globalping HTTP probes, `country: CN`)

| URL | Mainland probes OK | What happened |
|---|---|---|
| `https://alumni-honeycomb.vercel.app/` | **0 / 6** | DNS returned foreign decoy IPs (e.g. `104.244.43.57`), then TCP timed out: the `vercel.app` name is poisoned |
| a custom domain on the same Vercel servers (`stanfordeden.com`) | 6 / 6, ~0.8–1.2 s | the servers are reachable; only the shared name is blocked |
| `https://wjlgatech.github.io/alumni-honeycomb/` (the mirror) | **8 / 8**, ~0.5–0.9 s (one 3.3 s) | Beijing, Shanghai, Guangzhou, Shenzhen, Hangzhou, Chengdu, Nanjing, Changsha |
| `…/alumni-honeycomb/data.json` | 8 / 8 | the page's data loads too |

Re-measure any time with `make china` (`scripts/china_probe.py`; free, no key; exits 1 if the mirror drops below half).

**So, today:** share `https://wjlgatech.github.io/alumni-honeycomb` with people in mainland China. `make mirror` republishes it
from the same `web/` folder (`scripts/publish_mirror.sh` pushes `web/` to the `gh-pages` branch).

**Durable fix (decision D-DOMAIN in `docs/SPEC.md` §4):** one custom domain on Vercel would serve everyone from one URL,
because the measurement shows Vercel's servers are reachable under a custom name. Options, cheapest first:
1. A subdomain of a domain Paul already owns, e.g. `honeycomb.futuremake.io` (free; one CNAME `honeycomb → cname.vercel-dns.com`
   in that domain's Cloudflare DNS; then `vercel domains add honeycomb.futuremake.io`).
2. A new neutral domain for the project (~US$10–15/year).
3. A mainland host with ICP filing: only if probes ever show the custom domain failing. It needs a mainland entity or individual and weeks of filing.

GitHub Pages is a mirror, not a promise: GitHub has been intermittently disrupted in China before. That is why the probe is a script, not a sentence.
