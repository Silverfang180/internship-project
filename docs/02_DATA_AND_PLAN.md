# 02 DATA, FINDINGS (PRELIMINARY) AND BUILD PLAN

> The numbers in section 2 come from a quick first pass in a chat session. They are **hypotheses to reproduce**, not facts to submit. Phase 1–2 must re-derive every one of them from /data, and show the rows.

## 1. Data traps and how to handle them
| Trap | Handling rule |
|---|---|
| All timestamps are UTC; shifts are IST | Convert to IST (UTC+5:30) before assigning a shift. Naively using UTC puts ~68% of tickets in the wrong shift. |
| 616 duplicate ticket_ids (11,816 rows → 11,200 unique), each appears as a `helpdesk` + `legacy_fd` pair | Keep the `helpdesk` row (it has blank CSAT, not legacy 0). Document the rule. |
| Legacy CSAT 0 = no response | Treat 0 as blank. Never average zeros. |
| ~40 failed IVR transcripts in `customer_message` | Detect (very short / garbled / empty after the "[IVR transcript]" prefix), flag, exclude from any text analysis. Do not let them affect breach metrics. |
| Roster = one row per assignment with date ranges | Join ticket → roster on `agent_id` AND `created_at` within `from_date..to_date` (to_date blank = still active). All 11,200 tickets matched in the first pass. |
| `agent_id` on a ticket is the RESOLVER | The resolver may differ from whoever should have answered first. Use ticket **creation time (IST) → shift** as the "responsible shift", and show resolver shift separately. |
| Legacy money in its own unit | Check `refund_amount_inr` by `source_system` before trusting any rupee total. Only matters if you do the refund analysis (optional). |
| Tier 2 is not comparable to Tier 1 on volume | Exclude Tier 2 from agent comparisons or show separately. |
| Voice transcripts, chat/email/social messages | Not needed for the core breach analysis. Only use text analysis if it earns its place. |

Breach = `first_response_at − created_at` (minutes) > target (chat 15, voice 120, social 240, email 480). No missing or negative first-response times were found.

## 2. Preliminary findings (reproduce these!)
1. Overall: **2,440 breaches of 11,200 tickets = 21.8%**. At Rs 350 each ≈ **Rs 8.54 lakh** in credits over 18 months. (This matches the "22%" style of number in the brief.)
2. By channel: chat 27.6%, social 22.0%, email 20.4%, voice 5.6%.
3. **Step change in July 2025.** Monthly breach rate ≈ 8–11% Jan–Jun 2025, then ≈ 23–28% from Jul 2025 onward (≈ 9.4% before vs ≈ 24.9% after).
4. **By ticket creation shift (IST):** Morning 9.7%, Day 8.9%, **Night 65.6%**. After 30 Jun 2025: Night-created tickets breach **79%**; Night-created chat tickets breach **100%** from July 2025.
5. **Roster:** on 1 Jun 2025 there were 5 Night-shift agents (Indore: 3 chat, 2 email). From 30 Jun 2025 there are **zero**. Two chat agents (A3002, A3003) were re-rostered Night → Day on 30 Jun; the others (A3001, A3016, A3017) have no later assignment row.
6. **Who "gets" the breach:** since 30 Jun 2025, 1,909 breached tickets were resolved by Morning-shift agents vs 324 by Day-shift. Of the Night-created breaches, ~1,566 of ~1,631 were resolved by Morning agents (they inherit the overnight backlog under "next shift picks up" and the standard report blames the resolver).
7. So Neha's "morning team is the bulk of breaches" is true **in the resolver report** and probably misleading as a cause. Morning-created tickets breach only ~10%.
8. **Volume also roughly doubled** (≈ 400/month in H1 2025 → ≈ 700–870/month afterwards). But Day and Morning breach rates stayed ≈ 9–10% despite the volume rise — which suggests a coverage gap at night, not a general capacity problem. (Must test: does Night breach stay ~100% even in low-volume hours?)
9. Credits: monthly breaches rose from ≈ 35 (Jun 2025) to ≈ 180–280 later → credits up roughly 5x, so Arjun's "roughly tripled" looks right and Priya's "credits flat" looks wrong. CSAT (excluding zeros) moved only slightly (~3.4–3.5 → ~3.3); verify.
10. Rough value of the night gap: ≈ 0.79 × 1,999 ≈ 1,580 night-created breaches since 30 Jun 2025 ≈ **Rs 5.5 lakh over ~12 months ≈ Rs 1.4 lakh/quarter** in credits alone. Recompute precisely; add the CSAT angle only if you can show it.
11. Transfers: transferred vs non-transferred tickets breach at similar rates (21% vs 22%) — transfers are not the driver.

## 3. Candidate business goal (draft; recompute)
"Cut the overall first-response breach rate from ≈ 25% (Jul 2025–Jun 2026) to ≈ 12% by restoring Night coverage with **existing headcount** (re-roster, no hiring), worth about Rs X lakh a quarter in avoided SLA credits." Finance's constraint (no hire) is satisfied by re-rostering; Neha said the June reshuffle was "cost-neutral", so reversing part of it should be too. State your assumptions (how many agents, what residual breach rate you assume at night).

## 4. Phased plan with acceptance criteria
**P1 Clean data (60 min)** — `src/clean.py`
- Output `data/clean_tickets.parquet|csv` with: deduped tickets, IST timestamps, `created_shift_ist`, `resolver_shift`, `resolver_tier`, `breach` flag, `credit_inr`.
- Acceptance: 11,200 rows; counts printed for dups removed, CSAT zeros converted, IVR failures flagged; every ticket matched to exactly one roster row (or reported as unmatched).

**P2 Analysis (75 min)** — `src/analyze.py`
- Reproduce findings 1–11 with printed row counts. Add: breach rate by hour-of-day (IST) and channel; before/after 30 Jun 2025; Night coverage headcount over time.
- Acceptance: a short `analysis_notes.md` stating which findings held, which did not, and why.

**P3 Tool (60 min)** — `src/report.py` + `README.md`
- CLI: `python -m src.report --week 2026-06-22` (or a range) writes a weekly report (markdown/HTML/CSV).
- Report content: breach rate and count by **ticket-creation shift** and channel (the cause lens), plus a clearly secondary "resolved by" view; credit cost; coverage-gap flag (hours with no staffed agent for that team). **No ranked list of individual agents with shaming colour**; show agents only in aggregate or Tier-1-comparable ranges with volume and caveats (Priya's request).
- Acceptance: runs on a clean machine from README in under 5 commands; no API key needed unless you add an LLM step.

**P4 Validation (40 min)**
- Draw a random sample of ~40–50 tickets (stratified: channel and shift). Recompute breach and shift by hand (spreadsheet or by reading rows). Report mismatches and the kind of case that goes wrong (e.g. tickets created near shift boundaries, tickets with timezone edge cases, roster boundary dates).
- Acceptance: a table "sample size / correct / wrong / error rate / typical failure".

**P5 Memo, video, form (55 min)**
- Memo (one page, plain English): the finding, the number, what you recommend (re-roster, not hire), what you'd change about the ask, what you're unsure of.
- Video (≤ 3 min): show PROMPT_LOG v1 → v2 changes, what you threw away.
- Fill every form field; repo public; Drive link public; README tested from a fresh clone.

## 5. Memo skeleton for Neha (one page)
1. **What we found (2 sentences):** most breaches come from the overnight window since 30 Jun 2025, when Night coverage went to zero; morning agents appear in the report because they resolve the backlog.
2. **The number:** breach rate from A% to B%; Rs X lakh per quarter.
3. **What to do (no hiring):** re-roster N existing agents to Night / stagger shifts; expected effect.
4. **What we changed about your ask and why:** report by shift of ticket creation first; resolver view second; weekly; not a per-person league table.
5. **How sure we are:** sample check result; what could be wrong; what to verify first.
6. **Next step this week.**
Tone: do not blame the morning team; tell Neha plainly that her "morning team" premise doesn't hold once you look at creation time.

## 6. Optional extras (only if time remains; otherwise list under "left out")
- Refund/replacement anomalies: tickets with both a refund and a replacement (policy §5), `refund_reason_code` misuse, `lot_code` clusters by product (possible bad batch). Only mention if verified.
- LLM classification of ticket text. Probably not needed for the breach question; skip unless you can show it changes the answer.

## 7. Cost line for the form
If you make no paid API calls: "One run costs Rs 0 in model calls; compute is pandas on a laptop; a month at ~650 tickets/week is also Rs 0 in model calls." If you add an LLM step, show: tokens per ticket × price × tickets per month.
