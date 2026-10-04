# PROJECT_STATE.md — handoff file for any LLM or human taking over

> **Last updated:** 4 Oct 2026, after completing Phase 3 (Report tool built and tested)
> **Update rule:** this file MUST be updated after every phase, gate, decision, bug found, or file change (see section 14). If this file and the repo disagree, trust the repo and fix this file.
> **Contains no customer data and no secrets.** It does name the client's staff (role context). Review before making any repo public.

---
## 0. TAKEOVER PROMPT (paste this into a new LLM, then attach this file)
```
You are taking over a half-finished hiring task from another AI assistant. Read the attached PROJECT_STATE.md completely before answering.
Then reply with: (1) a 8-line summary of the task, (2) current status and what is done vs not done, (3) the 5 most important risks or open issues, (4) the exact next step.
Rules: the user is a beginner who relies on AI to write code and must be able to explain everything in a later interview, so go one step at a time, explain in plain language, and never claim a number is verified unless section 8 says so. Do not invent data. Ask the user to attach any raw file you need (list in section 3). Do not ask for or store customer data beyond what is needed.
```

---

## 1. The task in one paragraph
A company called **Banao Technologies** sent **Task 1 of 3** (a shortlisting task for the role *AI Engineer / Applied AI — Forward Deployed Track*). Scenario: we are a vendor for **Vireo Audio** (Bengaluru consumer-audio/wearables brand; 44 support agents in Bengaluru and Indore, 3 shifts; channels chat, email, voice callback, social). The client manager (**Neha Kulkarni**, Support Operations Manager) asked for a **weekly first-response SLA breach report by agent and shift**. The task is to build a small AI-assisted tool, find a business number, validate it, and write a memo, in about **5 hours of effort (hard cap; going over is not rewarded)** within a **48-hour window**. Deadline: check the task portal clock (it showed about 1 day 22 hours left when the pack was first opened on 4 Oct 2026).

**What is really being tested:** judgment, not volume of code. The brief says it is "not a specification": candidates must question the ask, handle data traps, quantify a business outcome, validate honestly, and say what is wrong with their own work. Questions marked "can only raise your score" reward pushback and honest self-criticism.

## 2. Deliverables checklist (all must be done)
| # | Deliverable | Status |
|---|---|---|
| 1 | Working AI-assisted tool that starts from the README on a clean machine | NOT DONE (cleaning script done; report tool not built) |
| 2 | Business goal stated as a number with money (find it in the data) | DRAFT only (see section 9) |
| 3 | Evidence it works (sample size, error rate, kind of case it gets wrong) | NOT DONE (Phase 4) |
| 4 | One-page non-technical memo to Neha (max 11 minutes reading) | NOT DONE |
| 5 | Screen recording, max 3 minutes: prompts used, what changed between versions, what was thrown away. No slides | NOT DONE (notes being kept in logs/PROMPT_LOG.md) |
| 6 | Submission form (answered on the portal; no submission-form.md was in the pack) | NOT DONE (draft template in logs/FORM_DRAFT.md) |

**Form questions (10 + 2 links):** (1) what you built + number + money; (2) cost of one run and a month at ~650 tickets/week, show arithmetic; (3) how you know it works: sample size, method, error rate, failure type; (4) did you change/narrow/push back on the ask [can only raise score]; (5) what is wrong with what you hand over [can only raise score]; (6) what you left out and why; (7) anything built/found nobody asked for; (8) what you used AI for, tools/models, helped/wasted time/discarded, link to recording; (9) three things someone needs on Monday if you are unreachable; (10) honest hours spent (one number). Links: public Google Drive, public GitHub repo URL.

**Rule from the brief:** if something is unclear, decide, write the decision down, explain why. Nobody can be asked questions. AI use is allowed for anything but must be disclosed honestly (tools, cost, what was discarded). No credits are provided; bring your own.

## 3. Input files (the "pack") — not in the repo, must be re-supplied to a new LLM if needed
Located locally in `data/` (gitignored). **Original byte sizes:** tickets.csv 4,440,409; agents.csv 3,073; customers.csv 446,354; orders.csv 984,099; products.csv 979; support-policy.pdf 6,774; email-thread.txt 2,999; README.txt 2,724.
- `tickets.csv` (11,816 rows, 18 months Jan 2025–Jun 2026; columns incl. created_at, first_response_at, resolved_at, status, channel, customer_id, order_id, product_sku, category, priority, assigned_team, agent_id (= RESOLVER), transfers, csat_score, refund fields, customer_message, agent_notes, source_system)
- `agents.csv` roster: one row per assignment (agent_id, name, site, team, shift, tier, from_date, to_date)
- `orders.csv`, `customers.csv`, `products.csv` (reference; products has launch dates, Pulse 2 = VA-EB-PL2 launched 2025-07-15)
- `support-policy.pdf` v3.2, `email-thread.txt`, `README.txt` (column descriptions)

## 4. Key facts from the client's email thread
- **Sameer (IT admin):** export is **UTC**; policy shifts are **IST**; roster has date ranges (some people moved in June); some tickets appear twice (migration re-import); legacy rows use csat 0 for "no response"; about 40 messages are failed IVR transcripts.
- **Arjun (Finance Controller):** headcount frozen till Q4, so the answer **cannot be "hire"**. The SLA-credit P&L line has roughly tripled since last summer, unexplained.
- **Priya (Head of CX):** morning chat team is demoralised ("wall of red"); **do not build something that makes that worse**. She believes credits are flat and CSAT moved.
- **Neha:** says the morning team is the bulk of breaches, says the June Indore reshuffle was cost-neutral. Wants "by agent and shift, weekly, nothing fancy."

## 5. Policy facts that drive the logic (support-policy.pdf v3.2)
- First response = first **human** reply, measured from ticket creation. **Targets:** chat 15 min, voice callback 2 h, social 4 h, email 8 h.
- Every breach automatically issues a **Rs 350** store credit regardless of cause (SLA credit P&L line).
- Standard helpdesk reports charge breaches to the **resolving agent** (design flaw: the resolver may not be who was supposed to respond first).
- Shifts in IST: Morning 06:00–14:00, Day 14:00–22:00, Night 22:00–06:00. Chat is 24x7 with overnight coverage by the Indore Night shift. Out-of-hours queue is picked up by the next shift.
- Costs: contact cost chat 210 / email 260 / voice 520 / social 240 (blended 290); transfer Rs 305; agent Rs 165/hour, 8-hour shift. Tier 2 must not be compared with Tier 1 on volume.
- CSAT: blank = no response, exclude from averages (never treat as 0). New helpdesk live 14 Sep 2025; earlier tickets migrated from Freshdesk (`legacy_fd`).

## 6. Data traps and how each is handled
| Trap | Handling | Status |
|---|---|---|
| Timestamps are UTC, shifts are IST | Convert UTC+5:30 before assigning shift | DONE and hand-verified on 8 tickets |
| 616 duplicate ticket_ids (helpdesk + legacy_fd pairs) | Keep helpdesk row; verified pairs are identical except source_system and csat_score | DONE |
| Legacy CSAT 0 = no response | Converted to blank (1,730 rows) | DONE |
| Failed IVR transcripts (client says ~40) | Flag `ivr_failed`: any message in ANY channel containing [inaudible] or [line dropped] + 2 punctuation-only voice rows = **16 flagged** (7 chat, 6 email, 2 voice, 1 social). 14 IVR-style transcripts sit in non-voice channels, so their SLA target may be wrong. Gap vs ~40 documented, not forced | DONE (limitation) |
| Roster has date ranges | Join on agent_id and created_at between from_date and to_date | DONE (11,200 matched, 0 unmatched) |
| agent_id is the resolver, not the first responder | Use ticket-creation shift (IST) as the "responsible shift"; show resolver view as secondary | Design decided |
| **Local data file corruption (incident)** | `data/tickets.csv` on the user's machine was altered after first use (all dates rewritten as dd/mm/yyyy, 4,412,554 bytes, likely re-saved in Excel; cause unconfirmed). Replaced with the original; verified 4,440,409 bytes, 0 slash dates. Parser made **strict** (`%Y-%m-%d %H:%M`, error naming first 5 ticket_ids otherwise). Never open data files in Excel. | RESOLVED |
| Export looks like a sample | Export has ~177 tickets/week vs the brief's "~650/week". Rates treated as valid for the export; **workload/utilization per agent cannot be inferred**; rupee values are not scaled | OPEN (must state in memo/form) |

## 7. Approach (decided)
1. Do not simply build Neha's per-agent league table. Re-examine the premise using the data and the policy.
2. Report breaches by **ticket-creation shift (IST) and channel** (cause lens) with a clearly secondary "resolved by" view. Aggregates only; no ranked individuals, no blame wording (Priya's concern); Tier 2 excluded from comparisons.
3. Quantify the cost: breaches x Rs 350, and a scenario for fixing the main driver using **existing headcount** (Arjun's freeze).
4. Validate with a **hand-checked stratified sample of ~50 tickets** (user fills manual columns; AI does not grade itself), report the error rate and failure types.
5. Tool: small Python CLI (pandas), no framework, no paid API calls (cost line: Rs 0 in model calls).
6. Division of labour: **Antigravity** (AI coding agent in the user's IDE) implements code/tests in small phases with a gate prompt after each; **Claude chat** plans, reviews outputs against independent calculations, and prepares docs. The user reviews and hand-checks.

## 8. Findings — verification status
Verified = reproduced by `src/analyze.py` (section A, 17/17 PASS, plus the re-gate analyses) **and** independently by Claude on the raw file.
| Finding | Value | Status |
|---|---|---|
| Overall breach rate | 21.8% (2,440 of 11,200 tickets) = Rs 8.54 lakh credits over 18 months | VERIFIED |
| By channel | chat 27.6%, social 22.0%, email 20.4%, voice 5.6% | VERIFIED |
| Step change | 9.3% before 1 Jul 2025 (211/2,266) → 24.9% after (2,229/8,934) | VERIFIED |
| By creation shift (IST) | Morning 9.7%, Day 8.9%, **Night 65.6%** | VERIFIED |
| Night-created after 30 Jun 2025 | 79.1% (1,579 of 1,997); Night-created chat 100% (1,034 of 1,034) | VERIFIED |
| Night staffing | 5 staffed Night agents on 1 Jun 2025, 0 from 30 Jun 2025 | VERIFIED |
| Who "gets" the breach | 96% of Night-created breaches (1,566 of 1,631) are resolved by Morning agents, so the standard resolver report blames the morning team for an overnight gap | VERIFIED |
| Share of breaches from Night | Night-created tickets = 70.8% of all post-July breaches. By channel: chat 1,034 (65.5%), email 387 (24.5%), social 158 (10.0%) | VERIFIED |
| Email behaves differently | Night-created email breach: 81.0% for creation hours 22–23 vs 6.1% for hours 0–5 (8-hour target is mostly met by 06:00). The Night gap is mainly **chat and social** | VERIFIED |
| Transfers | breach 20.7% vs 21.9% without transfers: not the driver | VERIFIED |
| Credits | avg Rs 12,308/month before 1 Jul → Rs 65,012/month after (~5.3x). Arjun directionally right; Priya's "flat" is wrong | VERIFIED |
| CSAT (blanks excluded) | 3.46 before → 3.34 after: slight dip only | VERIFIED |
| Coverage gap, not routing bug | Night-created tickets after July get first reply only between 06:00 and 09:59 IST (06h 1,068; 07h 582; 08h 258; 09h 89); Night chat median wait 432 min, 90th pct 505 min | VERIFIED |
| Not a product-launch effect | Pulse 2 (VA-EB-PL2) share 1.2% → 35.6% of tickets, but Night chat breach after 30 Jun is 100% for Pulse 2 and for other SKUs alike | VERIFIED |
| Daytime not strained | Morning+Day breach 8.9% (159/1,777) before 1 Jul vs 9.4% (650/6,937) after, while monthly volume rose ~200 → ~680; correlation of monthly volume with breach rate 0.198 | VERIFIED |
| Night volume after 30 Jun | 1,997 Night tickets / 365 days = **5.5 per night** in the export (chat 2.8, email 2.1, social 0.5). Earlier agent figures (32.2/night, 2.6 tickets/agent/day) were WRONG (day-count bug) and are corrected | VERIFIED |
| Roster change | Staff 44 → 41 from July 2025. Two chat agents moved Night→Day on 30 Jun 2025 (Day 19 → 21). Three agents (1 Chat Frontline, 2 Email Frontline, all Indore) have no roster row after 29 Jun 2025, so staffing fell by 3; Neha's "cost-neutral" is questionable | VERIFIED; cause (left vs data gap) UNKNOWN |
| Business case | Agent-shift cost 8 x Rs 165 = Rs 1,320/night. Credits avoided/night in the 10% scenario at export volume = Rs 1,322.6 (≈ break-even). Scaled by 650/177 (assumption) = Rs 4,857/night. Break-even ≈ 171 tickets/week | VERIFIED arithmetic; the 650/177 scaling is an ASSUMPTION |

## 9. Business goal (DRAFT — to be finalised in the memo)
"Cut the overall first-response breach rate from ~24.9% (Jul 2025–Jun 2026) to ~9.5% by restoring overnight **chat and social** coverage (email only for the 22:00–24:00 window) using **existing headcount** (no hiring), worth about **Rs 1.2 lakh per quarter (~Rs 4.8 lakh/year)** in avoided SLA credits at the export's volume."
Arithmetic: 1,579 Night-created breaches in 365 days x Rs 350 = Rs 552,650/yr (Rs 138,162/qtr). If the Night-created breach rate falls to 10% (assumption: equals Morning/Day), the overall post-July rate falls 24.9% → 9.5% and the saving is Rs 120,689/quarter.
**Important honesty point:** at the export's volume the credits avoided per night (~Rs 1,323) are about equal to one agent-shift (Rs 1,320). In credits alone the case is break-even; it is stronger if true volume is ~650/week (Rs 4,857/night, assumption), and it also protects CSAT. Because headcount is frozen, the cost is moving someone from Day, not hiring; Morning+Day breaches are flat, which suggests some headroom but this is not proven. Residual 10% breach rate is unproven.
Draft recommendation: pilot returning 1 chat/social agent-shift to Night (e.g. one of the two chat agents moved to Day), watch Day breaches for 4 weeks; ask Neha about the 3 missing agents and the true weekly volume. **No hiring.**

## 10. Current status (progress: roughly 50% by planned time; 0 of 6 final deliverables complete)
| Phase | Plan | Status |
|---|---|---|
| P0 Understand | 30 min | DONE. Antigravity raised a good objection: re-rostering may not be free (3 agents gone; volume rose) |
| P1 Clean data (`src/clean.py`) | 60 min | DONE, 5 tests, hand-verified, **committed** (commit 92f2828 on master) |
| P2 Analysis (`src/analyze.py`, `docs/analysis_notes.md`) | 75 min | DONE. Section A 17/17 PASS; day-count bug fixed; notes rewritten with numbers; close-out added Morning+Day before/after and break-even. **Not yet committed.** `docs/PROJECT_STATE.md` is untracked in git until the Phase 2 commit |
| P3 Tool (`src/report.py`, README) | 60 min | DONE. Built, tests passing, README updated, ran for 2026-06-22 to 2026-06-28. |
| P4 Validation (30-ticket hand-checked sample) | 40 min | READY FOR MANUAL REVIEW. Tools built (`validate.py`, `score_validation.py`) and tested. |
| P5 Memo, video, form, final security audit | 55 min | NOT STARTED |
**Hours spent so far:** not recorded. The user must log real times in `logs/HOURS_LOG.md` (not yet created); include review/fix time. **Budget: 5 hours cap.** Fixes and data-corruption handling already used extra time, so keep P3 minimal.

## 11. Repo and environment
Local project folder: `C:\Users\shaik\Desktop\internship` (Windows, PowerShell, Anaconda "base" shell, Python 3.12.4, `.venv` inside project). Git initialised, one commit, **no remote and nothing pushed to GitHub yet**.
```
internship/
  data/        (8 pack files; gitignored — contains customer data, never commit)
  docs/        00_START_HERE.md, 01_TASK_AND_CONTEXT.md, 02_DATA_AND_PLAN.md, DECISIONS.md, analysis_notes.md, (PROJECT_STATE.md goes here)
  logs/        FORM_DRAFT.md, PHASE_NOTES.md, PROMPT_LOG.md   (HOURS_LOG.md, COST_LOG.md still to create)
  src/         config.py, clean.py, analyze.py   (report.py, validate.py to come)
  tests/       test_clean.py (5 tests passing)
  output/      clean_tickets.csv (gitignored)
  README.md, requirements.txt, .gitignore (data/, .env, .venv/, __pycache__/, output/)
```
Commands (PowerShell, from project root): `$env:PYTHONPATH="."; .\.venv\Scripts\pytest -v tests/test_clean.py` · `$env:PYTHONPATH="."; .\.venv\Scripts\python -m src.clean` · `$env:PYTHONPATH="."; .\.venv\Scripts\python -m src.analyze`
`output/clean_tickets.csv` columns (no customer fields): ticket_id, created_at (IST), first_response_at, resolved_at, status, channel, category, priority, assigned_team, transfers, csat_score, source_system, agent_id, resolver_shift, resolver_tier, created_shift_ist, target_minutes, response_minutes, breach, credit_inr, ivr_failed.

## 12. Decisions made (see docs/DECISIONS.md for the full text)
D1 numbers in docs are hypotheses until reproduced · D2 do not recommend "just re-roster" until daytime headroom is checked · duplicate rule (keep helpdesk row) · IVR rule (any channel, markers + punctuation-only voice; 16 flagged; gap vs ~40 documented) · D5 strict date parsing after the data-corruption incident · shift for reporting = ticket-creation shift in IST · agents shown only in aggregate · no paid API calls · raw data never committed.

## 13. Known issues, risks, and open questions
1. RESOLVED: Phase 2 day-count bug and unbacked claims (fixed; notes rewritten with printed numbers).
2. OPEN: export (~177 tickets/week) vs "~650/week" in the brief: sample or inconsistent? Rupees are not scaled in the headline; scaled figures are labelled assumptions. State in memo/form.
3. OPEN: 3 agents (1 Chat, 2 Email, Indore) with no roster row after 29 Jun 2025: left or data gap? Question for Neha; undermines "cost-neutral".
4. OPEN: 14 IVR-style transcripts in non-voice channels may carry a wrong SLA target (e.g. 15 min chat instead of voice 2 h).
5. OPEN: IVR gap: 16 found vs ~40 in Sameer's note.
6. OPEN: residual breach rate (10%) is an assumption; the credit saving is about break-even against one agent-shift at export volume (see section 9).
7. OPEN: coverage gap is strongly supported but not proven beyond the data (no utilization or queue data).
8. **AI reliability record (Antigravity) — keep checking its work:** claimed "no customer PI" while exporting the full table; narrowed an IVR rule and lost 14 rows; "fixed" a date error with `format='mixed'`/`dayfirst=True` instead of finding the corrupted file; per-night figures ~6x too high; unbacked claims in notes; edited `logs/PROMPT_LOG.md` though the user wanted to write it themselves; **created its own short PROJECT_STATE.md instead of updating the full one** and said all sections were intact and issues resolved. Always verify the state file with line/heading counts and `git diff`.
9. The user will likely be asked in a later interview round to explain this work; they have limited hands-on coding experience (they direct AI tools) and must understand every function.
10. Before publishing any repo: re-run the final security audit (no data, no customer names, no keys, check git history). Decide whether docs naming client staff should be public.
11. `logs/PROMPT_LOG.md` must be reviewed and rewritten in the user's own words; `HOURS_LOG.md` and `COST_LOG.md` still to create; Antigravity's model name still to record for the form.

## 14. UPDATE PROTOCOL (how this file stays current)
Update this file (a) after every phase, (b) after every gate review, (c) when a decision is made, a bug is found, or a number changes status, (d) when the user says anything that changes scope or deadline, (e) before the user switches to a different LLM or session.
What to update each time: the **Last updated** line (date + trigger) · section 8 statuses · section 10 table and hours · section 12 decisions · section 13 issues (close fixed ones, add new) · section 15 next step · append one line to the changelog (section 16). Do not delete history; mark items RESOLVED.
**Prompt for Antigravity (paste after each phase):**
```
Update docs/PROJECT_STATE.md to reflect the current repo and this session. Keep all existing sections. Update: Last updated, section 8 finding statuses (only mark VERIFIED if your printed output reproduces it), section 10 phase status, section 12 decisions, section 13 open issues, section 15 next step, and append one changelog line. Do not add customer data, secrets or invented numbers. Show a short diff of what changed, then stop.
```
**For a chat LLM:** paste the latest outputs and ask it to rewrite the file with the same structure.

## 15. NEXT STEP
1. Verify this file is the full version: `(Get-Content docs\PROJECT_STATE.md).Count` should be about 160+ and `(Select-String docs\PROJECT_STATE.md -Pattern '^## ').Count` about 17. If not, overwrite it with the latest copy.
2. Commit Phase 2: `git add -A; git commit -m "phase 2: analysis and notes"; git status; git ls-files` (data/, output/, .venv/ must not appear).
3. Phase 4 (user hand-checks a 30-ticket sample using `output/validation_blank.md` and `output/my_answers.txt`), Phase 5 (memo, video, form), final security audit, publish repo + Drive, submit on the portal.
4. Memo must say: gap is mainly chat/social; break-even at export volume; sample-size question; 3 missing agents; the report is by creation shift not by agent.

## 16. CHANGELOG
- 4 Oct 2026: Task received; docs pack (START_HERE, TASK_AND_CONTEXT, DATA_AND_PLAN, FORM_DRAFT) created from first-pass data analysis.
- 4 Oct 2026: P0 completed; agent raised the re-rostering objection (D2).
- 4 Oct 2026: P1 built; reviewed; fixed privacy/test/IVR issues; found and fixed local data corruption; strict date parsing; verified by hand; committed (92f2828).
- 4 Oct 2026: P2 ran; section A 17/17 PASS; Claude found day-count bug and unbacked claims; added independent checks (coverage vs routing, Pulse 2, daytime breach vs volume); fixes prompt issued, pending.
- 4 Oct 2026: PROJECT_STATE.md created.
- 4 Oct 2026: P2 re-gate: Claude found chat target typo (10 vs 15 min), circular comparison, overclaim of "primary cause", missing channel split; fixed. Close-out added Morning+Day 8.9% → 9.4% and break-even (~171 tickets/week).
- 4 Oct 2026: Antigravity appeared to replace this file with a shorter one; full version restored and updated by Claude.
- 4 Oct 2026: Phase 3 completed; report tool built, tests passing, README updated, run successfully without PYTHONPATH.
- 4 Oct 2026: Phase 3 fixes: Coverage gaps grouped by team/shift, inherited breaches explicitly handled in 'Resolved By' table (with Tier 2 excluded), warning fixed.
- 4 Oct 2026: Phase 4 validation tools built (`validate.py` and `score_validation.py`). `clean.py` confirmed to use strict inequality for breach. Tests passing.
