# Scale: from one cell to thousands of schools · 从一个蜂房到上千所学校

**One question:** when a hive has 10,000 alumni and the federation has thousands of schools, how do the right people
find each other, and how do hives talk, efficiently, safely, at any size, inside and outside mainland China?
**This page does NOT answer** how one cell runs (README Level 2), how a member proves who they are
([MEMBERSHIP.md](MEMBERSHIP.md)), or how hives vote ([GOVERNANCE.md](GOVERNANCE.md)).

**Honest status:** 0 real cells, 2 simulated hives. This is a blueprint. One piece is built now because it is cheap now
and expensive to retrofit: **signed feeds**. Everything else is built when a hive needs it (signal before scale).

## The picture: a national food supply chain

One kitchen (a cell) cooks one dish with about 10 people. A restaurant (a hive) has many kitchens, and its staff list
never leaves the building. A chain of restaurants doesn't phone every cook: each restaurant sends head office a signed
weekly report (numbers, tested recipe cards, shifts it needs filled). At national scale, trucks (relays) carry sealed
crates (signed feeds) between depots, and anyone can check the seal without trusting the truck. A cook who needs a
specialist from another city asks their manager, who asks the other manager; the two cooks meet only if both say yes.

| Supply chain | Honeycomb | Exact handle |
|---|---|---|
| A kitchen of ~10 | **Cell**: 1 CEO + 2–3 advisors + 2–3 core + 2–3 apprentices | `cells[]`, charter P1 |
| A station team of ~50–150 | **Circle**: a class year, a lab, a city (Dunbar's 50 and 150 layers) | `circle:` on a member card (planned) |
| A restaurant | **Hive**: one school, private roster | `hives-private/<school>.yml` |
| The weekly report to head office | **Public feed**: numbers, learning cards, open seats, never people | `honeycomb publish` → `feed.json` (`ah-feed/1`) |
| The wax seal on the crate | **Signature**: Ed25519, by the hive's own key | `feed.json.sig`, `honeycomb/sign.py` (**built**) |
| The list of real restaurants and their seals | **Registry**: each hive's public key | `data/federation.yml` `pubkey` (**built**) |
| Trucks and depots | **Relays/mirrors**: copy feeds anywhere, trusted by nobody | GitHub Pages, futuremake.io, a CN mirror (planned) |
| Head office's catalogue | **Index**: merge and rank feeds; anyone can run one | `federation pull` → `federation/index.json` |
| Manager-to-manager request | **Warm, double-opt-in intro** across cells or hives | `introducer` (planned) |

## Layer by layer

### 1 · Inside a cell (about 10 people)
They already know each other. A group chat is enough; build nothing.

### 2 · Inside a hive (up to 10,000 alumni)
A flat directory of 10,000 names fails: nobody reads it, and it leaks. Instead:
- **Circles of 50–150** (class year, lab, city) are where people already trust each other (Dunbar's layers: about
  5 / 15 / 50 / 150, each about 3× the last).
- **Offers meet asks.** Every member card has one offer and one ask. The hive's steward matches asks to offers
  across circles and proposes **at most 3 introductions a week per person**.
- **Warm and double opt-in.** An introducer who knows both sides asks each privately; contact details are shared
  only after both say yes. Warm introductions get replies about 20× as often as cold ones (one dataset: 20.1% vs 1.06%).
- **Prefer moderately weak ties.** The largest experiment on this (LinkedIn, 20M people) found that moderately weak ties
  move careers most. So the matcher favours a person in another circle over one in your own.

### 3 · Between hives (Georgia Tech ↔ Yale ↔ 中大)
- **Only public feeds cross schools.** A feed carries numbers, anonymous learning cards and **open seats** (the seat,
  never the person). People never cross; that is charter P8, enforced by `feed.leaks`.
- **A cross-hive intro is steward to steward.** A Georgia Tech CEO needs a biotech advisor; the open seat appears in
  the index; Yale's steward sees it and asks a Yale alum privately; only on a double yes do the two meet.
- **Learning compounds.** A Yale cell cites `builds_on: georgia-tech/<cell>`. `federation.cross_hive_builds_on()`
  counts it, and a tag proven in 3+ cards from 2+ hives becomes a draft proposal (`ripe_patterns`).

### 4 · Thousands of schools
- **Static signed files, cheap relays, competing indexes.** Each hive publishes a small signed JSON file. Any relay
  copies it, any index merges it, and nobody needs to trust the copy, because the signature proves the origin. This
  is the split that makes AT Protocol (Bluesky) cheap to relay (a full-network relay costs about $34 a month), without
  its weak point: there, one company runs the expensive index; here, the files are small enough that anyone can.
- **Hive identity by domain.** A hive publishes its public key at `https://<hive-domain>/.well-known/honeycomb.json`,
  the same pattern as WebFinger, `did:web` and Nostr NIP-05. No blockchain is needed to know whose key it is.
- **Admission is the spam defence.** Every open federation studied (Mastodon, Matrix, Nostr) fought spam. A hive joins
  by signing the charter and being accepted under the 2/3 rule; any index may drop a feed (defederation).
- **China.** Feeds hold no personal information, so they cross borders without a CAC mechanism (CAC 2024 Art. 3). A
  mainland hive's roster never leaves the mainland. Mirrors go on China-reachable hosts (`*.vercel.app` is blocked;
  futuremake.io reached 6/6 mainland probes).
- **Small counts are suppressed** in feeds from real hives (no number under 5), so numbers can't identify a person
  (planned, before the first real hive publishes).

## What Web3 adds, and what it would break

| Technology | Decision | Why |
|---|---|---|
| Digital signatures (Ed25519) | **Adopt, built** | Proves a feed's origin on any mirror. Free, no chain |
| Content hashes (SHA-256) | **Adopt, built** | The charter is already signed by hash; a feed's hash names it exactly |
| W3C Verifiable Credentials 2.0 / Open Badges 3.0, issued by hives as `did:web` | **Adopt next**, for member proof | A member can carry "confirmed Georgia Tech alum" anywhere. W3C standard since May 2025. No chain |
| Selective disclosure (SD-JWT, RFC 9901) | **Adopt next** | Show "is a Georgia Tech alum" and nothing else |
| Append-only transparency log (Merkle tree, the Certificate Transparency pattern) | **Adapt** | Makes registry and vote history tamper-evident for anyone, with no gas and no token. Git plus signed commits already gives most of this |
| One hive one signed vote, m-of-n stewards | **Adapt** (Snapshot/Safe ideas without tokens) | Average DAO turnout is about 6%, and token-weighted votes can be bought (Beanstalk lost $182M in 2022). Never weight a vote by anything that can be borrowed |
| Zero-knowledge membership (Semaphore) | **Later** | Real privacy, but Ethereum-centred and heavy on phones; revisit if anonymous voting is ever needed |
| Public blockchains, tokens, NFTs, stablecoins, RWA | **Reject** | China banned crypto trading in 2021, and the 2026-02-06 notice that replaced that notice widens the ban to stablecoins and RWA. It conflicts with P7 (no fees, no selling) |
| Any personal data on a permanent ledger, hashed or not | **Reject** | EDPB guidelines (v2.0, July 2026) say keep personal data, even hashed, off-chain. PIPL Art. 47 requires deletion, and members include minors |

So the Web3 *ideas* (no centre, verifiable without trust, own your data, exit freely) are kept, and the crypto-economic
parts (tokens, chains) are left out on purpose. A chain adds cost and legal risk, and it would verify nothing a
signature does not.

## The 12X, defined so it can fail

| Measure | Target | How it is measured |
|---|---|---|
| Feeds anyone can verify on any mirror | 100% of registered hives | `federation check` fails on a missing or bad signature (**gated now**) |
| Personal data in public feeds | 0 | `feed.leaks` at publish; small-count suppression before the first real hive |
| Time for a new school to join | 1 day, 3 files, 1 command | measured when hive 3 joins (T3) |
| A warm cross-hive introduction, ask to first meeting | ≤ 7 days | measured on the first one (T4 period) |

## Run it

```
python -m honeycomb publish hives/<school>/hive.yml     # writes feed.json and, with a key, feed.json.sig
python -m honeycomb federation check                      # fails on a missing or bad signature
python -m honeycomb federation pull                       # index shows signature: ok | missing | bad | unkeyed
```
A real hive's private key goes in `hives-private/keys/<hive>.key`. Make one with
`python -c "from honeycomb import sign; from pathlib import Path; print(sign.keygen(Path('hives-private/keys/<hive>.key')))"`,
and put the printed public key in that hive's row in `data/federation.yml`. The two simulated hives commit their TEST
keys, named `TEST-ONLY-signing.key`.

## Research (read 2026-11-27)

| Fact | Source |
|---|---|
| Dunbar's layers ≈ 5 / 15 / 50 / 150, each ≈ 3× the last | Zhou, Sornette, Hill & Dunbar, Proc R Soc B 272:439 (2005) |
| Moderately weak ties produce the most job moves (20M LinkedIn users) | Rajkumar et al., Science 377:1304 (2022) |
| Warm vs cold intros: 20.1% vs 1.06% replies (one dataset) | BuzzStream journalist study |
| A full-network AT Protocol relay costs about $34/month; the index is the costly part | Bluesky ops blog; Newbold |
| Mastodon, Matrix, Nostr all hit spam; Nostr relays struggle to stay up | operator reports; Wei & Tyson, arXiv 2402.05709 |
| Data with no personal information is outside China's cross-border rules; consent is still needed for personal data | CAC Provisions 2024 Art. 3, Art. 10; PIPL Art. 38–39 |
| VC 2.0 W3C Recommendation 2025-05-15; SD-JWT is RFC 9901 (Nov 2025) | w3.org; rfc-editor.org |
| China's 2021 crypto notice was repealed on 2026-02-06 by a broader 8-agency notice (stablecoins, RWA) | csrc.gov.cn |
| EDPB Guidelines 02/2025 v2.0 (2026-07-07): keep personal data, even hashed, off-chain | edpb.europa.eu |
| DAO turnout about 6.3%; Beanstalk governance attack, 2022-04-17 | Harvey & Rabetti via HBS; CertiK |

**What this design cannot see:** whether stewards answer intro requests (only that requests exist), and whether a
signed feed tells the truth (only that its hive wrote it). The first is measured by the 7-day intro target; the second
by evidence rules (P3) and the 2/3 of hives who can drop a dishonest feed.
