# CLAUDE.md — Alumni Honeycomb

Read `README.md` (three levels), then `docs/SPEC.md` §0 (what we build, what we don't, the 10X). Board: `docs/STATUS.md`.
Public, MIT-licensed repo: never commit a real roster, name, contact detail or anything from `hives-private/`.

## Hard rules
1. **Data is spec.** Charter, model, federation, strategy and compass live in `data/*.yml`. `make build` regenerates
   `web/data.json` (committed; `build --check` in `make check` fails on drift). Never hand-edit `web/data.json`.
2. **The charter is signed by hash.** Any edit to `data/charter.yml` changes `sha256`; it needs a version bump, a ratified
   proposal in `data/federation.yml`, a new `charters[]` row and re-signed hive files. `federation check` enforces it.
3. **Principles are code.** P1–P6 live in `honeycomb/check.py` (one function per principle, listed in `RULES`). A new
   checkable principle gets a `checked:` key in the charter, a function, and a failing-case test.
4. **Privacy.** Real hives live in `hives-private/` (gitignored). Only `pulse` numbers are ever published. Minors need a guardian.
5. **No tokens, no fees, no foreign assets on the page.** P7; `test_site_loads_nothing_from_other_domains` keeps the page China-safe.
6. **Compass parity.** `web/compass.js` and `honeycomb/compass.py` must agree on every golden case in `data/compass.yml`.
7. **Never contact anyone, spend money, or register a hive on someone's behalf.** Founders own direction, money and evaluation.

## Gates
`make check` before every PR (drift · example hive · federation · pytest + node golden test · quality floor).
`make deploy` = check → Vercel prod → `live_check.py` on the origin and on the public address https://futuremake.io/honeycomb
(agentic-portfolio's `vercel.json` proxies `/honeycomb` here; the first `<script>` in `web/index.html` sets `<base href>`; keep it first). `make mirror` republishes `web/` to GitHub Pages, the URL
mainland China can reach (`*.vercel.app` is DNS-poisoned there); `make china` measures both from mainland probes.
Asset paths in `web/` stay relative (the mirror lives under `/alumni-honeycomb/`). Doc sync: a behavior change ships with `CHANGELOG.md`,
`README.md` and this file in the same PR.

## Where things are
| Topic | Files |
|---|---|
| Charter, North Star, principles | `data/charter.yml` |
| Roles, cell shape, capacity, seasons | `data/honeycomb.yml` |
| Rules engine | `honeycomb/check.py` (+ `tests/test_honeycomb.py`) |
| Vital signs, North Star, 10X verdict | `honeycomb/pulse.py`, `data/strategy.yml` |
| Recruit shortlist | `honeycomb/recruit.py` |
| Federation: hash, registry, 2/3 vote | `honeycomb/federation.py`, `data/federation.yml`, `docs/GOVERNANCE.md` |
| Calling Compass | `data/compass.yml`, `web/compass.js`, `honeycomb/compass.py`, `tests/compass.test.mjs` |
| Website | `web/index.html` (中文 first; three levels: concept · architecture · details), PWA files in `web/` |
| China access | `docs/CHINA-ACCESS.md`, `scripts/publish_mirror.sh`, `scripts/china_probe.py` |
