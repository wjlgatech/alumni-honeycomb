# China access

**Goal:** a student in Guangzhou or Beijing opens the link inside WeChat and the page loads in a few seconds.

## What the page already does

| Risk | Handling | Gate |
|---|---|---|
| Blocked foreign fonts/CDNs make a page hang | Every asset is same-origin; system Chinese fonts | `tests/test_honeycomb.py::test_site_loads_nothing_from_other_domains` |
| Heavy pages time out on slow links | One HTML file, one small JSON, tiny PNG icons, no framework | page weight is visible in `make live-check` |
| WeChat in-app browser | No login, no cookies needed; install hint says "Open in browser" | manual check (eval: Paul) |

## What the host decides (measured)

The hosting domain is the remaining risk. `*.vercel.app` is commonly reported as unreliable or blocked from mainland networks.
The measurement from mainland probes, run on 2026-11-19, is in `docs/STATUS.md` (Globalping HTTP probes, `country: CN`).

Options, cheapest first (decision D-DOMAIN / D-CHINA-HOST in `docs/SPEC.md` §4):
1. **Own domain on the current host** (~US$10–15/year). Often enough, because the block usually targets the shared
   `vercel.app` name, not the servers.
2. **Own domain on a Hong Kong/Singapore-region static host.** No ICP filing; usually fast from South China.
3. **Mainland host + ICP filing.** Fastest, but it needs a mainland entity or individual and weeks of filing.

Because the site is static files in `web/`, it can be mirrored to any of these hosts by copying one folder. Nothing is
locked to Vercel.
