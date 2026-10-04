# PROMPT LOG

## Version 1 (Phase 0): read the docs and plan
Prompt I sent:
Read all files in /docs and /data. Do not write any code yet.
Reply with:
1. What the client really needs, in 10 lines.
2. The data problems to fix before counting breaches.
3. The findings in docs/02_DATA_AND_PLAN.md that you will try to reproduce.
4. Your plan in phases with time estimates.
5. Anything in my docs you disagree with, and why.

What Antigravity replied:
Listed directory docs
Listed directory data
Viewed 00_START_HERE.md:1-54
Viewed 01_TASK_AND_CONTEXT.md:1-59
Viewed 02_DATA_AND_PLAN.md:1-74
Viewed README.txt:1-41
Viewed email-thread.txt:1-66

1. **What the client really needs:**
Neha explicitly asked for a breach report by agent and shift to have "conversations with the right people," assuming the morning team is at fault for the "wall of red." However, what she *really* needs is a root-cause analysis showing that the spike in breaches is systemic, not a performance issue. The data shows the true cause is a gap in night-shift coverage since the June 2025 reshuffle. She needs a report that shifts the lens from "who resolved the ticket" to "when was the ticket created" to visualize this coverage gap. She also needs a cost-neutral recommendation (like re-rostering existing agents to the night shift) that respects the headcount freeze while reducing SLA credits, saving roughly Rs 1.4 lakh/quarter, without demoralizing the morning staff who are just inheriting an overnight backlog.

2. **The data problems to fix before counting breaches:**
- **Timezone mismatch:** Export timestamps are in UTC, but shift definitions are in IST. All timestamps must be converted to IST (UTC+5:30) before assigning shifts.
- **Duplicates:** There are ~616 duplicate `ticket_id`s due to migration. The `legacy_fd` duplicates must be dropped in favor of the `helpdesk` rows.
- **CSAT Survey scores:** Legacy tickets use `0` to indicate no response to the survey. These must be converted to `null/blank` so they don't drag down CSAT averages.
- **IVR Failures:** ~40 voice tickets have failed IVR transcripts. These must be flagged and excluded from text analysis.
- **Roster mapping:** Tickets must be mapped to the roster using both `agent_id` AND `created_at` falling within the agent's `from_date` and `to_date` window.

3. **The findings in docs/02_DATA_AND_PLAN.md to reproduce:**
- The overall breach rate is 21.8% (2,440 breaches out of 11,200 tickets), costing ~Rs 8.54 lakh.
- Breach rates vary by channel: chat 27.6%, social 22.0%, email 20.4%, voice 5.6%.
- There was a massive step change in July 2025, with breach rates jumping from ~9.4% to ~24.9%.
- Tickets *created* during the Night shift (IST) breach at 65.6% overall, jumping to 79% (and 100% for chat) after June 30, 2025.
- Night-shift coverage dropped from 5 agents to 0 after June 30, 2025. 
- Morning-shift agents are resolving the bulk of these Night-created breaches (~1,566 out of ~1,631 since June 30), inheriting the SLA failure.
- SLA credits roughly quintupled (validating Arjun's claim), while CSAT barely moved.
- The night coverage gap costs roughly Rs 1.4 lakh/quarter.

4. **Plan in phases with time estimates:**
- **Phase 1: Clean data (60 min).** Build `src/clean.py` to convert UTC to IST, deduplicate tickets, handle legacy CSAT zeros, and merge ticket data with the roster based on the date validity.
- **Phase 2: Analysis (75 min).** Build `src/analyze.py` to re-derive all 11 preliminary findings (overall rates, channel breakdown, July step-change, night-shift gap, financial cost), printing row counts for every claim to validate them.
- **Phase 3: Tool (60 min).** Build `src/report.py` as a CLI tool that outputs a weekly report focused on ticket-creation shift, channel, and coverage gaps, with a secondary view for resolving agents.
- **Phase 4: Validation (40 min).** Perform a manual spot-check on a stratified random sample of ~40-50 tickets to verify our logic, identifying the error rate and common edge-case failures.
- **Phase 5: Memo, video, form (55 min).** Write the 1-page memo for Neha, record the 3-minute video showing prompts and iterations, verify the README on a clean machine, and submit the final form.

5. **Anything I disagree with, and why:**
I disagree with the assumption in section 3 of `02_DATA_AND_PLAN.md` that reversing the June reshuffle to restore Night coverage will automatically be "cost-neutral" and perfectly viable with existing headcount. The preliminary findings state that out of the 5 night-shift agents, 2 were moved to the Day shift, but the other 3 "have no later assignment row." This suggests those 3 agents may have left the company. If headcount dropped in June and is now frozen till Q4 (as Arjun stated), we don't have those 5 agents anymore. To restore Night coverage, we would have to pull active agents away from the Morning or Day shifts. Given that overall ticket volume has doubled (from ~400 to ~700-870/month), pulling agents from the daytime shifts could easily cause new SLA breaches during the day. We must analyze the daytime capacity before confidently recommending a simple "re-roster" in the memo.

What I changed or noticed:
- It disagreed with my docs about re-rostering (see DECISIONS D2). I agreed.
- It treated my preliminary numbers as facts. I corrected that.