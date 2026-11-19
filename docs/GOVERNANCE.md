# Governance · the decentralized committee

**In one line:** the committee does not run the hives. It keeps the charter and helps every hive run itself.

Think of a cooking school that trains restaurant owners. It owns no restaurant. It keeps the shared recipe book and the
food-safety rules, trains new owners, and improves the tools. Each restaurant chooses its own menu, staff and hours.

| Analogy | Exact handle |
|---|---|
| The recipe book and the safety rules | `data/charter.yml` (North Star, philosophy, P1–P7) |
| A restaurant | a hive: one school's operation, `hives-private/<school>.yml` |
| Owner's licence on the wall | `hive.charter.sha256`, verified by `python -m honeycomb federation check` |
| The owners' assembly | the **Council**: one steward per registered, non-simulated hive |
| Changing the rules | a proposal in `data/federation.yml` → `proposals`, ratified at ≥ 2/3 of hives (`federation.ratified`) |
| Leaving | fork the repo and keep your data; nothing to ask |

## What the Council does (empower, not command)

1. **Keeps the charter.** Merges a charter change only when its proposal is ratified, bumps `version`, records the new hash in
   `charters`. Hives re-sign by updating their hash; a hive on an older version stays registered until it re-signs.
2. **Trains operators.** A new hive's operator walks one season as an advisor in an existing hive first (recommended, not required).
3. **Keeps the tools.** Maintains this repo: `make check` green, the quality floor only rises.
4. **Publishes the federation pulse.** Collects each hive's `pulse --json` once a season. Numbers only, never names.

## What the Council never does

Choose a hive's members, cells, subjects or rhythm. Hold any hive's roster. Charge fees, sell anything, or issue tokens (P7).
Speak for a university: hives are volunteer alumni groups, not official university bodies.

## How a hive joins

1. Fork the repo; write `hives-private/<school>.yml` from `hives/example/hive.yml`.
2. `python -m honeycomb check hives-private/<school>.yml` until it is green.
3. Run `python -m honeycomb federation hash`; put the result in `hive.charter.sha256`.
4. Open a PR adding one row to `data/federation.yml` → `hives` (id, school, operator pseudonym, `charter_version`, `status: active`,
   and a `path` to a **public** file that holds only `hive:` + `pulse:` numbers, never members).
5. The Council merges it if `make check` is green. One hive, one vote, from that moment.

## Founding period

Until three hives are registered, the founders (D-COUNCIL in `docs/SPEC.md` §4) act as the Council, and every decision they
take is written in `data/federation.yml` → `proposals` with `status` and reasons, so the record exists before the vote does.
