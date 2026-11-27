# The member card · 成员卡

**One question:** what does a person put on their honeycomb card so others can trust them as much as their role
needs, offer and receive help, and keep improving season after season?
**This page does NOT answer** how cells are formed (README Level 2) or how the first people are found
([DISCOVERY.md](DISCOVERY.md)).

## The picture: a kitchen pass

In a good kitchen, a new cook doesn't show a diploma at the door. The head chef watches one service, a sous-chef who
trained them says "I worked the line with her at the Ritz", and the menu they cooked last season is on the wall. Trust
comes from several small proofs, and the more dangerous the station (the fryer, the knives, a kid in the kitchen),
the more proof it takes. Each cook also keeps a notebook: what I'm learning this season, what I did each shift, what I'll
change. That notebook is how a line cook becomes a chef.

| Kitchen | Honeycomb | Exact handle |
|---|---|---|
| Several small proofs, not one diploma | Evidence points per school | `data/membership.yml` `evidence`, `member.level()` |
| A sous-chef who trained you vouches | A confirmed member vouches, saying how they know you | `kind: vouch`, `circle:`; same circle counts once, max 3 |
| The diploma itself, when you still have it | A registry report you order yourself | `kind: registry` (Clearinghouse DegreeVerify / 学信网) |
| The menu on the wall | Your thesis or paper with the school's name | `kind: public_record` (SMARTech, ProQuest, ORCID) |
| The more dangerous the station, the more proof | Each role has a minimum level | `roles.<role>.min_level` |
| Knives are not the same as kids in the kitchen | School proof never unlocks minors | `safeguarding`, `works_with_minors` |
| A cook who promises 3 shifts and works 1 | Stated hours vs given hours | `hours_per_week`, `member.loop_health()` |
| The cook's notebook | Your own closed loop | `purpose`, `season_goal.good`, `weekly[]`, `review` |

## Signing in, editing, staying the same person, keeping fakes out

| Concern | Answer | Handle |
|---|---|---|
| Passwords | None. A member confirms one contact (email or WeChat) with a one-time code; later a passkey on their own phone. Nobody, the steward included, ever holds a password | `identity.anchor`, `identity.sign_in` |
| Who edits a card | Only a session from the member's own contact. Changing a school, field or years puts that school back to *stated* until proof is re-added; every change is kept | `identity.edits` |
| Same person next year | Same contact + unbroken history. Lost the contact? Two members who know you vouch you back in | `identity.same_person` |
| One bad actor, many fake cards | Invite-only (every card says `invited_by`; founders seed), 3 invites a season, the inviter loses invites if a fake is found, duplicates flagged, and **no reward for numbers**: no fees or tokens (P7), and success counts cells with evidence, not members. A fake card can learn, but can't advise or reach a minor | `sybil`, `member.check`, `member.duplicates` |

The owner's room (futuremake.io/honeycomb/room.html) is different: it is the site owner's private page, opened with the
futuremake.io owner passphrase or a 30-day signed session (a sign-in QR shown on the owner's own Mac, or the emailed
recovery link once email is configured). The passphrase guards every private page on futuremake.io, so it is long and
random, never a short code.

## Three levels, per school

| Level | Meaning | Rule (`member.level`) |
|---|---|---|
| 0 · stated | You said it | no counted evidence (LinkedIn and your own word count 0) |
| 1 · supported | Some proof | 2+ points |
| 2 · confirmed | Solid proof | 4+ points, from 2+ kinds, at least one not from a peer |

Points: school email 3 · registry 3 · public record 2 · alumni association 2 · document seen 1 · photo 1 (max 1) ·
vouch 1 each (max 3). The card shows the level as a word. It never says "verified".

**Why peers alone can't confirm:** three friends can all be wrong together. One record that doesn't depend on any of
them (a thesis, a registry report) breaks the circle.

## What each role needs (the least, so nobody is blocked)

| Role | Proof | Hours a week |
|---|---|---|
| CEO | none: a student leads without proving anything | 4 |
| Core | none | 3 |
| Apprentice | none; a minor needs a guardian (P6) | 1 |
| Advisor | supported at a school; confirmed when the cell has a minor | 1 |

A cell with anyone under 18 also needs, from every adult in it: a dated screen in their own country, and the rule that
every contact with a minor is **observable and interruptible, online too**. School proof is never safety.

## Minimal, standard, full

| Tier | Fields | Time |
|---|---|---|
| Minimal (join a cell) | name · schools · roles · hours a week · languages · one offer | 2 minutes |
| Standard (be picked) | + up to 3 interests · one ask · time zone · online/in person · evidence · anything you could profit from | 10 minutes |
| Full (earned) | + vouches · history of roles and closed cells (computed) · safeguarding · boundaries | grows each season |

## Your own closed loop

A cell's rules, applied to one person:
1. **Purpose:** one sentence on what you're becoming, and for whom.
2. **Season goal:** one goal with a "Good:" line someone else could check (P2).
3. **Weekly:** hours given, hours received, what you did, one next step (P4), energy 1–5.
4. **Review:** what was observed, not hoped (P3).
5. **Compound:** next season, take a different seat, and the review becomes a learning card (P8).

`member.loop_health()` turns the weekly lines into numbers: weeks logged, hours given vs promised, next steps kept.
Measured, not claimed.

## Scenarios

| Who | Gets to | How |
|---|---|---|
| **A 1992 SYSU graduate**, no digital record | confirmed | 学信网 cannot show pre-2002 records online, so: a public record (a paper) + 2 classmates from different circles vouching |
| **A current Georgia Tech student** | confirmed in a minute | the `@gatech.edu` code (3) + one teammate's vouch (1) |
| **An alum advising a cell with a 16-year-old** | needs more than a degree | confirmed at the school + a dated screen + every contact observable and interruptible |
| **Paul** (four schools, a CEO and an advisor) | Georgia Tech supported today | the dissertation in SMARTech; the card flags that CEO + advisor need about 5 h/week, not the 3 offered |

## Tools and money

Tools (AI companions, agents, templates) are shared **free** inside the hive, listed on the maker's card with what
they do and what data they touch. A paid tool lives on the maker's own site; the card may link it, with the profit
disclosed. Charging inside the hive would need a change to P7 ("no fees, no selling"), voted by 2/3 of hives (founders
while fewer than 3). It is not built.

Anyone who could profit from a cell's work says so on the card. Students' work on it is credited, and is either paid or
open-sourced.

## Run it

```
python -m honeycomb member check hives-private/members/<you>.yml   # levels, problems, exit 1 if not supported
python -m honeycomb member card  hives-private/members/<you>.yml   # the one-pager
python -m honeycomb discovery push                                  # puts your card in the private room
```

## Research behind it (read 2026-11-27)

| Fact | Source |
|---|---|
| Georgia Tech, Yale (College, GSAS) and USC Columbia verify degrees through the National Student Clearinghouse; Yale's professional schools verify themselves | each registrar's verification page |
| 学信网 (CHSI): online checks cover registered records; graduates before about 2002 get a written 学历认证报告; fees were cancelled in 2018 | chsi.com.cn/xlrz |
| Georgia Tech's repository holds its graduate theses | library.gatech.edu/theses |
| ORCID marks affiliations added by an institution and verified email domains (since Sept 2024) | info.orcid.org |
| LinkedIn verifies education only through a current school email or licence, which rarely helps older alumni | LinkedIn help |
| W3C Verifiable Credentials 2.0 is a Recommendation (May 2025); Open Badges 3.0 builds on it | w3.org, 1edtech.org |
| Related adults count as one adult in youth safeguarding ratios | church-insurer guidance |
| One-on-one contact with minors must be observable and interruptible, online included | US Center for SafeSport |
| 未成年人保护法 Art. 62: pre-hire checks for people in close contact with minors | gov.cn |
| Passkeys (WebAuthn, FIDO2) replace passwords with a key that never leaves the member's device | W3C WebAuthn Level 2/3; FIDO Alliance |
| An invite tree where each member is accountable for whom they invited keeps a community clean without central ID checks | Lobsters' public invitation tree (practice, not a study) |
| About 30% of youth mentoring matches end before 12 months, most often from mentor time constraints | Keller & Spencer, OJJDP |

**What this design cannot see:** whether a vouch is honest (only that it is independent), and whether hours logged are
true (only that they are logged). The steward's review and the next season's check-ins are the correction.
