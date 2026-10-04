# 01 TASK AND CONTEXT

## The client
Vireo Audio: Bengaluru consumer-audio and wearables brand (earbuds, headphones, speakers, watches). Support desk: 44 agents, Bengaluru + Indore, 3 shifts, channels = chat, email, voice callback, social. They are evaluating us as a vendor.

## The ask (Neha Kulkarni, Support Operations Manager)
"A breach report: which agents and which shift are breaching first-response SLA most, weekly, so I can have the conversation with the right people. Nothing fancy."

## What we must deliver
1. **A working AI-assisted tool.** Any stack/models. Must start from the README on a clean machine.
2. **A business goal stated as a number** (e.g. "cut X from A% to B%, worth about Rs Y a quarter"). Found in the data.
3. **Evidence it works:** how we know the output is correct, and how often it is wrong.
4. **A one-page memo to Neha.** Non-technical, max 11 minutes of reading.
5. **A screen recording, max 3 minutes:** prompts used, what changed between versions, what was thrown away. No slides.
6. **The submission form** (all fields) + public GitHub repo + public Google Drive link.

## Form questions (answer every one, honestly)
1. What did you build and what business outcome does it move? (number + money)
2. What does one run cost, and a month at ~650 tickets/week? Show the arithmetic. (If no paid calls, say so.)
3. How do you know it works? (sample size, how checked, error rate, kind of case it gets wrong)
4. Did you change, narrow or push back on the client's ask? (can only raise score)
5. What is wrong with what you are handing over? Be specific. (can only raise score)
6. What did you deliberately leave out, and why that rather than something else?
7. Anything you built or found that nobody asked for?
8. What did you use AI for? Tools, models, where it helped, where it wasted time, what you threw away. Link the recording.
9. Someone picks this up Monday and you are unreachable: the three things they need to know.
10. Honest hours spent (one number).
11. GitHub repo URL (public). Public Google Drive link.

## Rules of the task
- No one to ask. If something is unclear: decide, write down the decision, explain why. Those decisions are graded.
- AI use is allowed for anything. Tell the truth about what you used, what it cost, what you discarded.
- What you leave out matters as much as what you build.

## Email thread — who wants what (key points)
- **Sameer (IT):** export is in **UTC**; policy shifts are **IST**. Roster has one row per assignment with from/to dates; some people moved in June. Some tickets appear **twice** (migration re-import). Legacy rows use **csat 0** for no response (new system leaves blank). About **40 failed IVR transcripts**.
- **Arjun (Finance):** headcount frozen till Q4, so the answer **cannot be "hire"**. The **SLA credit line has roughly tripled** since last summer and nobody has explained it.
- **Priya (Head of CX):** morning chat team is demoralised, "a wall of red" they may not be able to influence. **Don't build something that makes that worse.** She believes credits are flat and CSAT moved.
- **Neha:** says the morning team is the bulk of breaches, "just the fact". Says the June Indore reshuffle was cost-neutral by Arjun's numbers. Wants report by agent and shift, weekly.

## Policy facts you need (support-policy.pdf v3.2)
- First response = first **human** reply, measured from ticket creation.
- Targets: chat 15 min, voice callback 2 h, social 4 h, email 8 h.
- **Every breach auto-issues a Rs 350 store credit**, regardless of reason (charged to the SLA credit P&L line).
- Breaches are reported **against the resolving agent** in standard reports (this is a design flaw to question: the resolver is not necessarily who was supposed to respond first).
- Shifts in IST: Morning 06:00–14:00, Day 14:00–22:00, Night 22:00–06:00. Coverage outside staffed hours is picked up by the **next shift**.
- Costs: contact cost chat 210 / email 260 / voice 520 / social 240; blended 290. Transfer Rs 305. Agent Rs 165 per hour (8 h shift).
- Tier 2 (Escalations & Warranty) is multi-touch and must not be compared with Tier 1 on volume metrics.
- Blank CSAT = no response; exclude from averages (never treat as 0).
- New helpdesk live 14 Sep 2025; earlier tickets are migrated from Freshdesk (`legacy_fd`); legacy stored money in its own native unit.
- No refund AND replacement on the same order (escalate if it happens).

## Decisions you must make and write down (graded)
- How you define "breach" per channel and handle timezones.
- Which duplicate row you keep and why.
- Whether to report by **resolving agent** (as asked) or by **who should have responded / shift in which the ticket was created** (probably the better lens), and why.
- How to present results so no individual is shamed by raw numbers they cannot control.
- What you leave out (refund/lot-code analysis, ticket-text classification, etc.).
