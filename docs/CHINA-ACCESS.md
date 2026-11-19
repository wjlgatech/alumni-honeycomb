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

**Resolved 2026-11-19: the public address is https://futuremake.io/honeycomb.** futuremake.io is Paul's portfolio site (Vercel
project `agentic-portfolio`, custom domain, reachable from mainland China). Its `vercel.json` rewrites `/honeycomb` and
`/honeycomb/:path+` to this repo's Vercel origin at the edge, so a reader's browser only ever talks to futuremake.io and every
deploy of this repo shows up there with nothing copied. Because Next.js strips trailing slashes, the page is served at
`/honeycomb` (no slash) and sets its own `<base href>` from `location.pathname` (first script in `web/index.html`), which
keeps the relative asset paths right on all three hosts.

| Address | Role | Mainland China |
|---|---|---|
| https://futuremake.io/honeycomb | **share this one**, with everyone | reachable (see `docs/STATUS.md`) |
| https://wjlgatech.github.io/alumni-honeycomb | backup mirror (`make mirror`) | 8/8 |
| https://alumni-honeycomb.vercel.app | origin only; never share it with China readers | 0/6 |

GitHub Pages is a mirror, not a promise: GitHub has been intermittently disrupted in China before. That is why the probe is a script, not a sentence.
