# 一对一访谈卡 · 1:1 interview card

_Generated from `data/discovery.yml` by `python -m honeycomb discovery card`. Do not edit by hand._

**先关系，后研究。** 先给，再问。只问过去发生的事和具体的行动，不问「你会不会」。
**Relationship first, research second.** Give before you ask. Ask about the past and concrete acts, never "would you".

30 分钟：5 分钟听对方正在做的事 → 20 分钟问题 → 5 分钟邀请（阶梯）。结束后 15 分钟内记录。
30 minutes: 5 on what they are building → 20 on questions → 5 on the ask (the ladder). Write it up within 15 minutes.

| # | 要弄清 · Unknown | 问题 | Question | 听什么 · Listen for |
|---|---|---|---|---|
| 1 | 我们能先给对方什么 · What we can give them first | 你现在最在意、正在做的一件事是什么？我们能帮上什么？ | What are you building or caring about most right now? How could we help? | Something we can actually give within a week. Write it down and deliver it. |
| 2 | 价值有多高 · How high is the value | 最近一次有学弟学妹或孩子来找你聊前途，是什么事？后来你做了什么？ | The last time a younger student or a child came to you about their future: what was it, and what did you do? | A specific story with a date. No story = low value for this person. |
| 3 | 哪类人需求最强 · How strong is demand | 你圈子里有谁已经试过做类似的事（导师计划、校友群、读书会）？结果怎样？ | Who in your circle already tried something like this (mentoring, an alumni group, a study circle)? What happened? | Time or money already spent = real demand. Name the group (student, teen, parent, advisor, organizer). |
| 4 | 什么让它点燃 · What makes it a sparking success | 你见过的最好的一段师徒/同伴关系，为什么撑过了第三个月？ | The best mentoring or peer relationship you have seen: why did it last past month 3? | The mechanism (a shared project, a deadline, a ritual), not a virtue word. |
| 5 | 什么让它昂贵地失败 · What makes it an expensive failure | 假设现在是 2027 年 3 月，这件事悄悄死了。最可能的故事是什么？ | Imagine it is March 2027 and this died quietly. What is the most likely story? | Map it to a break id. A new one goes into data/discovery.yml. |
| 6 | 什么让它闭环复利 · What makes it a closed | 一个学生做完一季 CEO，什么会让他下一季回来当别人的顾问或队员？ | After a student leads one season, what would make them come back as someone else's advisor or teammate? | The return reason is the loop. 'Gratitude' is a hope; 'their own next project needs a team' is a mechanism. |
| 7 | 系统有多结实 · How robust it is | 如果 Paul 消失三个月，谁会让它继续运转？ | If Paul disappeared for three months, who would keep it running? | A name, or silence. Silence = founder_bottleneck. |
| 8 | 什么会让它悄悄坏掉 · What breaks it silently | 什么会停下来而没有人注意到？ | What could stop without anyone noticing? | Each answer needs a detector; 'none' is the gap. |
| 9 | 什么会让它大声坏掉 · What breaks it loudly | 什么事一旦发生，会让家长、学校或你自己马上退出？ | What single event would make parents, the school or you yourself pull out at once? | Minors, faith content in China, data, being sold to. |
| 10 | 信任与名分（谁的许可） · Trust and legitimacy: whose permission | 做这件事，需要谁点头？谁会反对？ | Whose yes does this need? Who would say no? | The real gatekeeper (an association head, a parent, a school office). |
| 11 | 哪类人需求最强 · How strong is demand | 你能想到三个人，每人一个角色（CEO、顾问、队员）吗？愿意介绍吗？ | Can you think of three people, one per role (CEO, advisor, teammate)? Would you introduce them? | The ask. Record the rung, not the enthusiasm. |
| 12 | 我们能先给对方什么 · What we can give them first | 我们怎么做，才对你和你的圈子是好事，而不是又一个群？ | What would make this good for you and your circle, not one more group? | Their incentive. A hub with nothing to gain will fade (hub_only). |
| 13 | 什么会让它悄悄坏掉 · What breaks it silently | 上次你答应带一个人或做一件长期的事，实际坚持了多久？为什么停下？这次你每月真实能给几个小时？ | The last time you took on a person or a long commitment, how long did it actually last, and why did it stop? How many hours a month do you really have now? | Expected length predicts whether a match survives; mentors end about 64% of early closures, mostly over time (Keller & Spencer 2018). Under 2 hours a month = not an advisor seat yet. |
| 14 | 哪类人需求最强 · How strong is demand | 还有谁是我一定要先聊的？ | Who else must I talk to before Dec 5? | Friendship paradox: the people a person nominates are more central than a random pick (Christakis & Fowler 2010). Add each nominee to people.yml. |

## 阶梯 · The ladder (record what they DID)

| Rung | 中文 | English |
|---|---|---|
| 0 | 只是称赞 | Compliment only (noise) |
| 1 | 约了下一次 | Gave more time: a second conversation is booked |
| 2 | 按角色介绍了具体的人 | Introduced specific people, by role |
| 3 | 自己认领一个座位 | Took a seat themselves (CEO, advisor, core) |
| 4 | 用自己的名义邀请圈子来 12 月 5 日 | Invited their circle to Dec 5 under their own name |

## 会坏在哪 · What breaks it

| Break | Kind | 中文 | English | Detector today |
|---|---|---|---|---|
| `advisor_fade` | silent | 顾问第二个月不再出现 | Advisors stop showing up in month 2 | check.checkin_next_step + checkins per cell per month |
| `ceo_burnout` | silent | CEO 同时扛太多，悄悄放弃 | The CEO carries too much and quietly quits | check.capacity (P5) |
| `group_quiet` | silent | 微信群变安静，没人宣布结束 | The WeChat group goes quiet; nobody declares it over | feed heartbeat (federation pull) |
| `hub_only` | silent | 只有组织者在说话，学生没有声音 | Only organizers talk; students have no voice | none |
| `founder_bottleneck` | silent | 一切都要经过 Paul | Everything routes through Paul | none |
| `politeness` | silent | 大家客气地说好，但没人行动 | Everyone politely agrees; nobody acts | discovery tally: ladder rung >= intro |
| `minor_incident` | loud | 涉及未成年人的安全事件 | A safety incident with a minor | check.safety (P6) |
| `faith_complaint` | loud | 宗教内容在中国大陆引起投诉或风险 | Religious content draws a complaint or risk in mainland China | none |
| `data_leak` | loud | 名单或联系方式外泄 | A roster or contact detail leaks | feed.leaks + hives-private/ gitignored |
| `parent_upset` | loud | 家长觉得被推销或被越界 | A parent feels sold to or overstepped | none |

## 预先承诺的规则 · Pre-committed rules

| Rule | When | 那么 | Then |
|---|---|---|---|
| R1 | `ceo_candidates < 2 on 2026-12-02` | 12 月 5 日的分组改成「找到你的 CEO 之事」，不按学校分 | Dec 5 breakouts become 'find the thing you would lead', not by school |
| R2 | `a break is raised by >= 3 people` | 它在 12 月 5 日之前得到一个检测器或一个修正 | It gets a detector or a fix before Dec 5 |
| R3 | `parent value < 2 (mean of parents heard)` | 第一季不收未成年人，只做大学生 | Season 1 takes no minors; university students only |
| R4 | `faith_complaint raised by >= 2 people` | 祷告移出正式会议，改为会后自愿的单独时段 | Prayer moves out of the meeting into a separate, optional time afterwards |
| R5 | `seats_committed < 6 on 2026-12-02` | 停止约新人，回到已见过的人：问「什么让你还没说要」 | Stop booking new people; go back to those met and ask what kept them from a yes |
