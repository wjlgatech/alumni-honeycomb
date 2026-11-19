# Changelog

All notable changes to this project are recorded here (Keep a Changelog).

## [Unreleased]

### Added
- The honeycomb model as data (`data/honeycomb.yml`): a cell = 1 CEO + 2–3 alumni advisors + 2–3 core + 2–3 apprentices for one 3-month season, with roles that switch between cells. It is the North Star mechanism: everyone is the CEO of something.
- The federation charter (`data/charter.yml`): North Star, philosophy, principles P1–P7; hives sign it by SHA-256 and `federation check` verifies the registry; charter changes need 2/3 of hives (`federation.ratified`).
- Rules engine `honeycomb check` (P1–P6), `pulse` (aggregate numbers + 10X verdict), `recruit` (shortlist for empty seats), and a simulated example hive.
- Calling Compass: 8 questions scored in the browser (`web/compass.js`), mirrored in Python, both held to golden cases.
- Static, installable website (`web/`), 中文 first, three levels (concept · architecture · details), no third-party assets so it loads from China.
- Docs: SPEC §0 with a 10X that can fail, ARCHITECTURE, GOVERNANCE (the decentralized committee), CHINA-ACCESS, STATUS.
- Gates: `make check` (drift, charter rules, federation, pytest + node golden test, quality floor), CI workflow, `live_check.py`.

### Investigated / Rejected
- **A token or on-chain registry for the "web3 committee"**: rejected. Token issuance and trading are illegal in mainland China (2021-09-24 notice), and minors' data must not sit on a public ledger. A signed hash plus git votes verifies membership and governance for the first dozens of hives.
- **A hosted app with logins and a database for v0.1**: rejected for now. A 10–50 person hive runs on one YAML file; build it when an operator says the file is the bottleneck.
- **An LLM matcher**: rejected for v0.1. With 10–50 people, rule-based reasons a human can argue with beat a model's opaque ranking.
- **"Alumni Companion" (one-to-one companion pairs)**: the first draft this session. Replaced by the honeycomb, because pairs don't make anyone a CEO and don't switch roles.
