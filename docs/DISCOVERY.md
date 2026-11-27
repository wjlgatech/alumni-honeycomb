# Pre-launch 1:1s · 会前一对一

**One question:** before the first public meeting (Sat 2026-12-05, 5 PM Pacific = Sun 2026-12-06, 9 AM Beijing), whom
do we meet one at a time, what do we ask, and which answers change the plan?
**This page does NOT answer** how the meeting runs (`data/events.yml`) or how a cell works ([README](../README.md) Level 2).

**People relationship >> business. Technology (AI, robotics, web3, quantum …) magnifies and accelerates both** (Paul,
2026-11-26). So each 1:1 is a relationship first and research second. We give before we ask. The first number we count
is whether the person left feeling heard (`felt_heard`). Code only tallies the results and never replaces the meeting.

## §0 The request, evaluated

**Reflected back.** You have one week before the public meeting. Find the hub-like people whose circles listen to them.
Meet each 1:1, in person if possible. Learn how high the value is and how strong demand is in each group. Find what
makes it spark, what makes it an expensive failure, what makes it a compounding closed loop, how robust it is, and what
breaks it silently or loudly. Then name the questions we missed.

**What is weak in it, plainly.**
1. **A hub is not the user.** A hub *predicts* other people's demand, and predictions about others flatter. Eight hubs
   can agree that "students need this" while no student has ever asked. Fix: 2 of the 8 slots go to **end users** (a
   student, a teen with a guardian) and 1 goes to a **skeptic** (`selection.reserve`).
2. **"How high is the value?" asked directly returns a compliment.** Every question on the card asks about something
   that already happened, or for an act (The Mom Test). Value is scored from evidence: 0 = no story, 1 = an opinion,
   2 = a specific past story, 3 = they already spent time or money on it.
3. **Most connected is the wrong choice.** We are asking people to lead or advise a 3-month project, which is a
   high-commitment act. Acts like that spread through *overlapping* ties, where a person hears it from 2–3 people they
   trust, not through one far-reaching hub (complex contagion). So the plan puts **3 hubs in the first hive's own
   circle** and makes sure each people group is heard twice.
4. **"Understand the problem" has no finish line.** Seven days of interviews can end with good notes and an empty
   room. The 1:1s have a second job: **seat the first two cells before Dec 5**, so the meeting shows cells that already
   exist instead of recruiting into empty ones.
5. **Thanksgiving week.** US hubs are with family from Nov 26 to 29, and Beijing evenings are US mornings. So we book
   in-person meetings with local hubs over the weekend and China-side meetings by video at 8–9 PM Beijing time.

**The 12X, defined so it can fail** (computed by `python -m honeycomb discovery tally`, D-targets in `data/discovery.yml`):

| ID | Measure | Target by 2026-12-04 | Fails when |
|---|---|---|---|
| D1 | `seats_committed`: seats named by role, counted once per person | **≥ 12** (cold start ≈ 1, so 12X) | Everyone says "great idea" and nobody takes a seat |
| D2 | `ceo_candidates` | ≥ 2 | Nobody wants to lead something this season |
| D3 | `interviews` | ≥ 6 | We run out of week |
| D4 | `segments_heard`: groups heard from their own members | ≥ 4 | Only hubs spoke |
| D5 | `felt_heard` | ≥ 6 | We used people for data |

12 seats is most of two minimal cells (7 each), so D1 is the leading indicator for **T1** (2 active cells by 2026-12-19).

**Decisions only you can make:** (a) the real list of people (`hives-private/discovery/people.yml`, only you know
them); (b) R3 and R4 below, which change who the first season is for and what the meeting contains, so you accept them
in advance or overrule them now; (c) sending the invitations. Code never contacts anyone (CLAUDE.md rule 9).

## The picture · 一张图

Two rails, one domain: **a chef opening a small restaurant.**

| Analogy (the 15-year-old's picture) | Technical handle (the engineer's) |
|---|---|
| Before opening night, the chef cooks a private dinner for 8 people the neighborhood listens to | `discovery plan` picks `selection.max_meetings` = 8 |
| Not the 8 loudest people in town. Three are regulars in the **same** neighborhood, so word repeats inside one circle | `selection.cluster_voices` = 3 for `first_hive_cluster` (complex contagion) |
| Each kind of diner is tasted by two people: families, students, the market organizer | `voices_per_segment` = 2 over `segments` |
| Two seats go to ordinary diners and one to the critic who hates fusion food | `reserve: {end_user: 2, skeptic: 1}` |
| Feed them first. Ask what *they* are cooking at home | Q1 + Q12 (`unknown: give`), counted as `gave_first` |
| Ask about the last meal they loved or hated, never "would you eat here?" | every question is about the past (The Mom Test) |
| At the end, notice who books a table for their family, not who says "delicious" | `ladder` rung 0–4; `seats_committed` |
| Write down on the kitchen wall, before the dinners, what you'll change if X happens | `rules` R1–R5, one function each in `discovery.RULES` |
| Smoke alarms for the fires you'd miss; you'll hear the loud ones anyway | `breaks`, `kind: silent|loud`, each with a `detector` |

## The room: one private place for all of it

https://futuremake.io/honeycomb/room.html is where the week happens on the phone. It shows the next person to talk to, what to give and ask each one, a *Log this talk* form, and the live tally. Zoom with Glance · Room · Detail. The page is public code with no names. Its data comes from agentic-portfolio's owner-only `/api/honeycomb-room` (404 for anyone else), which the page reads with the same owner session as futuremake.io/brief.

| Step | Where |
|---|---|
| Send the private plan up | `HONEYCOMB_OWNER_TOKEN=… python -m honeycomb discovery push` (reads `hives-private/discovery/{people,names,briefs,interviews}.yml`) |
| After a talk | the phone: *Log this talk* on that person (rung, seat, quote, risk, what you gave, felt heard) |
| Bring notes home and re-tally | `discovery pull` then `discovery push` |

## How the week runs

| Date (Pacific) | Step | Handle |
|---|---|---|
| Thu 11-26 to Fri 11-27 | Write the real list: 10–15 people, pseudonymous ids, segments, circle, trust 0–3, in person? | `hives-private/discovery/people.yml` |
| Fri 11-27 | Run the plan; send 8 invitations (draft below) | `make discover` |
| Sat 11-28 to Tue 12-01 | 1:1s, at most 2 a day, 30 minutes each; write each up within 15 minutes | `hives-private/discovery/interviews.yml` |
| Wed 12-02 | Mid-point tally. R1 and R5 are dated for today. Apply every rule that fires | `make discover` |
| Thu 12-03 | Change the agenda if R1/R3/R4 fired; build a detector for anything R2 flagged | `data/events.yml`, `data/discovery.yml` |
| Fri 12-04 | Final tally (D1–D5). Ask each hub at rung ≥ 2 to bring their people **by name** | `make discover` |
| Sat 12-05 | The meeting: seated cells are introduced in the breakouts | `2026-12-05-kickoff` |
| Sat 12-19 | T1 check: 2 active cells, or the tripwire (`data/strategy.yml`) | `python -m honeycomb pulse` |

**The 30 minutes.** Spend 5 minutes on what they are building, and give something if you can. Spend 20 minutes on the
card ([DISCOVERY-CARD.md](DISCOVERY-CARD.md), 中文 first, 14 questions; pick the 6–8 that fit the person). Close with 5
minutes on the ask (Q11) and write down the rung they reached. Then do the 15-minute write-up, in this shape:

```yaml
- {id: I-03, person: H-prof, date: 2026-11-30, mode: video, speaks_as: advisor, value: 3, rung: 2,
   seats: [{role: core, who: K-1}, {role: advisor, who: A-1}], breaks: [advisor_fade, hub_only],
   felt_heard: true, gave: "a student for their lab's open project"}
```

Use the same pseudonym (`who`) when two people name the same person. They count once.

**Invitation draft** (you send it; code never does):

> 中文：「我在做一件听起来有点疯狂的事：让每个学生每一季都当一件自己热爱之事的 CEO，由校友陪着走。12 月 5 日开第一次见面会之前，我最想先听你的看法，因为你身边的人信你。能给我 30 分钟吗？我也很想听听你最近在忙什么。」
> English: "I'm working on something that sounds a little crazy: every student, every season, leads something they love, with alumni walking alongside. Before our first meeting on Dec 5, I'd most like to hear from you, because the people around you trust you. Could I have 30 minutes? I'd also love to hear what you're building right now."

The invitation works on tension and an invitation: something that sounds crazy, and a request for their judgment,
not their help. It also promises to listen to them first.

## The ten unknowns, and the ones you missed

Your eight unknowns are on the card, each mapped to past-behavior questions: value (Q2), demand per group (Q3, Q11),
spark (Q4), expensive failure (Q5, a pre-mortem), closed compounding loop (Q6), robustness (Q7), silent break (Q8) and
loud break (Q9). Four you did not list carry the most risk:

| Missed question | Why it matters | On the card |
|---|---|---|
| **What can we give this person first?** | Relationship first. A hub who gains nothing fades within a season (`hub_only`) | Q1, Q12 |
| **Whose yes does this need, and who would say no?** | An alumni-association head or a school office can quietly block reach | Q10 |
| **Who keeps it running if Paul disappears for 3 months?** | If every decision goes through you, it does not compound (`founder_bottleneck`) | Q7 |
| **What happens to minors, faith content and data in mainland China?** | The three loud breaks that end it overnight; see *Compliance* below | Q9, R3, R4 |

Also listen for these, without a question of their own: what people use today instead (WeChat groups, school mentoring
programs); the real time cost per role per month; and whether Google Meet even reaches the person (`china_zh` in
`data/events.yml`).

## What breaks it: silent (we'd miss it) and loud (we won't)

`data/discovery.yml` `breaks`. The tally reports any break that is raised but has `detector: none`. That is the
robustness gap.

| Break | Kind | Detector today | Proposed detector if it is raised |
|---|---|---|---|
| `advisor_fade` | silent | check-ins per cell (P4) | Flag a cell with no advisor check-in for 30 days in `pulse` |
| `ceo_burnout` | silent | `check.capacity` (P5) | already enforced |
| `group_quiet` | silent | feed heartbeat | already weekly |
| `hub_only` | silent | **none** | Share of check-ins written by students vs alumni |
| `founder_bottleneck` | silent | **none** | Count cells where Paul holds a role; target 0 by season 2 |
| `politeness` | silent | ladder rung ≥ 2 | this tally |
| `minor_incident` | loud | `check.safety` (P6) | guardian on file, crisis → qualified help |
| `faith_complaint` | loud | **none** | R4: prayer leaves the main meeting |
| `data_leak` | loud | `feed.leaks`, gitignore | already enforced |
| `parent_upset` | loud | **none** | a one-question guardian check-in each month |

## Pre-committed rules

These were written before the first interview, so the data decides, not the mood of the week. Each one is a function
in `discovery.RULES`, and the test `test_every_rule_in_data_is_code_and_back` keeps the data and the code in step.

| Rule | When | Then |
|---|---|---|
| R1 | fewer than 2 CEO candidates on 12-02 | Breakouts become "find the thing you would lead", not by school |
| R2 | a break is raised by ≥ 3 people | It gets a detector or a fix before Dec 5 |
| R3 | parents rate the value below 2 | Season 1 takes no minors; university students only |
| R4 | ≥ 2 people raise faith content as a risk | Prayer moves out of the meeting into a separate optional time afterwards |
| R5 | fewer than 6 seats on 12-02 | Stop booking new people; go back to the people already met and ask what kept them from a yes |

## 操作 · 反馈 · 前馈

- **操作 (what runs):** `make discover` (plan + tally on the private files) and `make check`, which gates the card, the
  rules and the tests.
- **反馈 (the measurement, and what it cannot see):** the tally turns the notes into D1–D5, the rules that fire and the
  blind spots. It cannot see sincerity. A rung-3 "yes" can still fade, so D1 is a leading indicator and T1 on 12-19 is
  the real test. `value` is your own judgment, and one interviewer scoring their own interviews is biased. Ask a
  cofounder to score 2 write-ups blind and compare.
- **前馈 (the plan, and what we can see coming):** Thanksgiving availability (book the weekend early); time zones
  (China at 8–9 PM Beijing); Google Meet blocked on the mainland (ask about it in every China-side 1:1); hubs
  over-representing parents (the plan already counts voices per group). The tripwires R1–R5 are feedback rules written
  in advance. They fire on an observed number and do not predict anything.

## Compliance: minors, faith, data (mainland participants)

This is a risk map from the primary texts (read 2026-11-26). It is not legal advice; a lawyer should confirm anything
that ships.

| Risk | Rule (article) | What it means for Dec 5 |
|---|---|---|
| **Prayer in an online meeting with mainland attendees** | 互联网宗教信息服务管理办法 (2022-03-01) Art. 6: only permitted mainland bodies may serve online religious content; overseas bodies may not. Art. 17: no one else may organize religious activity online or broadcast rites. Art. 14(8): no organizing minors into religious activity. 宗教事务条例 (2018) Art. 41: non-religious groups may not organize religious activity | The agenda's optional 5-minute closing prayer exposes the **mainland participants**, not us. **The research finds this risk before any interview, so R4's threshold has in effect already been met.** Recommended: take it out of the public meeting and hold it afterwards as a separate, adults-only time that is not recorded and not in the China invitation. Whether to do this is your call (✋) |
| Sign-up data of mainland people stored on a US server | PIPL Art. 3(2) (reaches processing aimed at people in China), Art. 38–39 (cross-border: tell people who receives it, get separate consent) | The form asks for name, role, optional school, contact and an adult check. It asks nothing about faith, which is correct: religious belief is *sensitive* data (Art. 28). Missing: a one-line notice of where the data is stored, with a consent box |
| Under-14 data | PIPL Art. 28 and 31 (guardian consent); Minors Protection Law Art. 72 | The form already requires an adult check box. Keep minors off the form; their guardian signs them in (charter P6) |
| Volume exemption | CAC Order 16 (2024) Art. 5(4) | Fewer than 100k people a year is exempt only when there is no sensitive data. Another reason never to collect faith or minors' data |

## Research behind the choices

| Choice | Evidence | Read |
|---|---|---|
| Greedy picks with a reason each, not "top 8 by reach" | Kempe, Kleinberg & Tardos (KDD 2003): greedy is within 1−1/e (63%) of optimal for influence spread and beats degree centrality | fetched |
| 3 hubs in one circle | Centola, *Science* 2010 (1,528 people): behavior spread farther and faster in clustered networks; adoption rose with reinforcement from several contacts | fetched |
| Bridgers for intel and intros, not as adopters | Burt, *AJS* 2004: brokers across structural holes have better ideas | secondary |
| Q14 "who else must I talk to?" | Christakis & Fowler, *PLoS ONE* 2010: the friends of random people are more central (they caught flu 13.9 days earlier) | fetched |
| Q13 expected length and hours | Keller & Spencer, OJJDP brief (2018): about 30% of matches closed before 12 months; mentors ended 64%, mostly over time; pre-match expectations predicted length. Grossman & Rhodes (2002): matches that end in ≤ 3 months can leave youth worse off | fetched / secondary |
| Past events only, the ask ends the meeting | Fitzpatrick, *The Mom Test*: compliments are noise; a meeting succeeds when it ends with time, reputation or money committed | secondary |
| End users and a skeptic in the room | Blank: the user, the recommender and the payer are different roles; interview each | secondary |

**What this design cannot see.** Sincerity. Whether a seat committed on Dec 2 still holds on Dec 19 (T1 measures
that). Interviewer bias: the same person asks the questions and scores the answers.
