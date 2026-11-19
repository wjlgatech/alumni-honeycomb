# Alumni Honeycomb · spec v0.1

## §0 The request, evaluated

**The request, reflected back (≤6 lines).** Build an open-source repo, an internationally reachable website
(especially from mainland China), and a decentralized committee for an international alumni ecosystem covering
entry (admission, hiring), professional and leadership growth, and jobs and ventures. Start with our own children,
our schoolmates' children and SYSU students, then other schools. The core is the **honeycomb model**: every season
(3 months) each student is the CEO of something they love, with 2–3 alumni advisors, 2–3 core teammates and 2–3
apprentices, and they switch roles between cells. The differentiator is companionship in spirit, mind, heart and strategy, not only a door.

**What is weak in it, plainly.**
1. **"Ecosystem" is the end state, not the first product.** Admission, hiring, growth, jobs and ventures for many
   schools is five markets. The first product is one thing: **one cell that runs one season and closes with
   evidence**. Everything else (more schools, a hiring board, a venture fund) waits for that signal.
2. **"Web3" can mean a token, and a token would kill it in China.** Issuing and trading tokens is illegal in mainland China
   (PBoC and nine other agencies, notice of 2021-09-24), and student data must never sit on a public ledger. So we keep
   web3's *ideas* (protocol not platform, verifiable membership, own your data, supermajority governance, free exit) and
   drop the chain. See `docs/ARCHITECTURE.md` §3.
3. **"Internationally accessible, especially China" is an infrastructure claim that needs a measurement**, not a vibe.
   `*.vercel.app` is commonly reported as unreliable from the mainland, and a mainland host needs an ICP filing. This repo
   makes the page China-safe (no foreign CDN, font or script; tested) and measures reachability from mainland probes. The
   durable fix is a decision about a domain and a host (§4).
4. **12 seasons × (CEO + 2 other roles) is a lot of load.** Passion has to be sustainable, so the charter caps it:
   at most 3 roles per season and 1 CEO role (P5, enforced by `check.capacity`).
5. **Minors.** Paul's first circle includes schoolmates' children. The charter requires an informed guardian for every
   under-18 member and pseudonyms everywhere (P6, enforced by `check.safety`).

**The 10X, defined so it can fail** (`data/strategy.yml`, computed by `python -m honeycomb pulse`):

| ID | Measure | Target | Due | Why it would fail |
|---|---|---|---|---|
| T1 | `active_cells`, full shape, in the first real hive | ≥ 2 | 2026-12-19 | Nobody commits to be a CEO, or alumni don't show up twice |
| T2 | `role_switchers`: people who held 2+ different roles | ≥ 3 | 2027-03-31 | The cells form but roles stay fixed (a mentoring club, not a honeycomb) |
| T3 | `hives`: non-simulated hives in `data/federation.yml` | ≥ 2 | 2027-06-30 | No second school wants to run it under the charter |

**Tripwire:** if T1 < 1 on 2026-12-19, no second school, no token, no new feature. Ask the people who stopped why.

**Decisions only the founders can make** (§4): D-DOMAIN, D-CHINA-HOST, D-FIRST-HIVE, D-COUNCIL.

## §1 What v0.1 builds

| Built | Where |
|---|---|
| The charter: North Star, philosophy, principles P1–P7, federation rules | `data/charter.yml` |
| The honeycomb model: four roles, cell shape, season clock, capacity | `data/honeycomb.yml` |
| The rules engine: P1–P6 checked on any hive file | `honeycomb/check.py` |
| Vital signs and the North Star (aggregate numbers only) | `honeycomb/pulse.py` |
| A shortlist for empty seats in a forming cell | `honeycomb/recruit.py` |
| Federation: charter hash signing, registry check, 2/3 vote | `honeycomb/federation.py`, `data/federation.yml` |
| Calling Compass: 8 questions, scored in the browser, nothing stored | `data/compass.yml`, `web/compass.js`, `honeycomb/compass.py` |
| A simulated hive (10 people, 4 cells, 2 seasons) | `hives/example/hive.yml` |
| The website, 中文 first, three levels, installable, no foreign assets | `web/` |

## §2 Deliberately later

- **A hosted app with logins and a database.** A hive of 10–50 people runs fine on one YAML file and a WeChat group.
  Build the app when an operator says the file is the bottleneck (signal, not faith).
- **An AI steward** that drafts check-ins or recruit messages. Later, with the Stanford Eden boundaries (drafts only,
  never claims God's will, crisis → qualified help).
- **Admission / hiring boards, a venture fund.** After T2.
- **Any token or on-chain record.** Not while mainland China is the first market (§0.2).

## §3 Success, beyond 30 days

A student who walks 12 seasons has been coached 12 times, has coached others about 24 times, and has led 12 things they
believe in. That is the long measure; `role_switchers` and `closed_with_evidence` are its early readings.

## §4 Open decisions (founders)

| ID | Question | Recommended default | Cost |
|---|---|---|---|
| D-DOMAIN | Buy a neutral domain (e.g. a `.org` with the project name)? | Yes: `*.vercel.app` is unreliable from the mainland and a name is reusable by every hive | ~US$10–15 / year |
| D-CHINA-HOST | Mainland mirror? | Start with a Hong Kong/Singapore-region static host on the new domain (no ICP needed); move to a mainland host with ICP filing only if probes show it is needed | HK static ~US$0–5 / month; mainland needs a Chinese entity or individual for ICP |
| D-FIRST-HIVE | Who is the first hive's operator, and is it "SYSU alumni" or "Paul's circle"? | Paul's circle, operated by one named alumnus; it becomes a school hive when 2 cells close | time |
| D-COUNCIL | Who sits on the founding council (one steward per hive + founders)? | Paul + 2 stewards from the first hive; rotate yearly | time |
