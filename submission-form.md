# FORM_DRAFT â€” fill in AFTER the project is finished
Put this file in `logs/FORM_DRAFT.md`. Copy the final answers into the portal.
Rule: every claim must be something you checked. Numbers come from your own re-run, not from chat notes.
Keep notes as you go in the "Notes while building" box under each question, then write the final answer at the end.

---
## 1. What did you build, and what business outcome does it move? (state the number and the money)
Include: what the tool does in one sentence; the business goal as a number (from A% to B%); the rupee value per quarter and the arithmetic (breaches avoided x Rs 350, plus any other cost you can support); the assumptions behind it.
- Notes while building:
- FINAL ANSWER:
I built a simple local Python script that analyzes SLA data and uses optional AI commentary to figure out which shifts and channels are costing us the most money.

The goal is to pilot moving some existing staff to the night shift for four weeks, hoping to drop the post-July first-response SLA breach rate from 24.9% down to 15% or less.

Right now, the verified credit exposure after July is about â‚¹65,012 a month. If we reduce the breach rate from 24.9% to 15%, that's roughly a 39.8% proportional drop. In that scenario, we'd save about â‚¹25,848 a month (â‚¹65,012 Ã— 39.8%), or roughly â‚¹77,544 a quarter (â‚¹25,848 Ã— 3).

This is just a scenario, though, not a guaranteed forecast. It assumes things stay consistent during the pilot and that moving people doesn't just cause new breaches during the day.

## 2. What does one run cost, and what would a month cost at ~650 tickets/week? (show the arithmetic)
Include: paid API calls, yes or no; if none, say "Rs 0 in model calls"; if any, tokens per ticket x price x (650 x ~4.3 tickets/month); compute and storage cost if relevant.
- Notes while building:
- FINAL ANSWER:
My tool runs completely locally, so a deterministic run costs â‚¹0 in model calls.

The Gemini AI feature is completely optional. If you use it, the tool only sends a tiny summary of the metrics to the LLM, not the raw tickets. So, processing 650 tickets costs the exact same as processing 177. Because it's a CLI tool running on your own machine, there are zero ongoing costs for servers, databases, or infrastructure.

## 3. How do you know it works? (sample size, how you checked, error rate, the kind of case it gets wrong)
Include: how many tickets you hand-checked and how you picked them; how many were right and wrong; the error rate; the typical failure (e.g. shift-boundary times, roster-date edges, duplicates); what you did not test.
- Notes while building:
- FINAL ANSWER:
I manually checked a random sample of 30 tickets. My code got the correct shift for 30 out of 30 tickets, and it correctly figured out if they breached the SLA for 30 out of 30. That's a 0.0% observed error rate in my sample.

One edge case I found is that there are 14 IVR-style transcripts in non-voice channels that might have the wrong SLA targets in the source data. Also, since I only checked 30 tickets, I can't guarantee there are zero errors across the entire population.

## 4. Did you change, narrow, or push back on the client's ask? (what, when, and why) [can only raise your score]
Include: what Neha asked for; what you did instead or in addition (e.g. shift of ticket creation vs resolving agent, no per-person league table, no hiring); what evidence made you change it; when in the process (which phase).
- Notes while building:
- FINAL ANSWER:
Yes, I pushed back on a few things. First, I changed the focus to look at when the ticket was created in IST, instead of looking at the agent who finally resolved it. Agents were inheriting tickets that had already breached overnight before they even started work, so making a leaderboard to blame individuals seemed really unfair.

I also excluded Tier 2 from Tier 1 comparisons. Because headcount is frozen, I pushed back on any ideas about hiring more people. Lastly, I noticed the provided export only has about 177 tickets a week, while the brief mentioned 650, so I highlighted that mismatch instead of ignoring it.

## 5. What is wrong with what you are handing us? (be specific: bugs, shortcuts, things you know are off) [can only raise your score]
Include: known bugs; shortcuts and assumptions (duplicate rule, breach definition, timezone handling); data you did not verify; anything AI wrote that you only partly understand; limits of the business-number estimate.
- Notes while building:
- FINAL ANSWER:
Here's what isn't perfect:
- There's a big mismatch in the volume (the data has ~177 tickets/week, but the brief says ~650).
- Three agents are missing roster records after June 29, 2025.
- There are 14 weird non-voice IVR records.
- I don't have queue or utilization data, so I can't prove mathematically that the lack of staff caused the breaches.
- Checking 30 cases doesn't prove it's flawless for every edge case.
- The financial savings are just a scenario, not a guarantee.
- The AI commentary is restricted so it doesn't invent numbers; the real numerical evidence is strictly generated by Python.

## 6. What did you deliberately leave out, and why that rather than something else?
Include: 2-4 things (e.g. refund/replacement anomalies, ticket-text classification, per-agent ranking, dashboard UI) and the reason you chose to skip each over what you built.
- Notes while building:
- FINAL ANSWER:
1. I deliberately skipped building a fancy web UI, dashboard, or infrastructure so the tool could stay simple, run locally, and cost nothing to host.
2. I deliberately refused to make a per-agent blame ranking because the data showed agents were just getting stuck with overnight breaches that weren't their fault.
3. I deliberately decided not to send raw ticket transcripts to the LLM. I did this to protect customer privacy, keep API costs at zero, and stop the AI from hallucinating fake math.

## 7. Anything you built or found that nobody asked for?
Include: only verified findings (e.g. the July 2025 step change, Night coverage dropping to zero, the standard report charging the resolving agent). Say how you verified each.
- Notes while building:
- FINAL ANSWER:
I found a few verified patterns nobody specifically asked for:
- There was a clear jump in the breach rate starting in July 2025.
- Night staffing completely dropped to zero after June 30, 2025.
- Because of that, tickets created at night became the largest concentration of breaches after July.
- I realized the standard report was unfairly blaming the resolving agent for SLA breaches that happened before they logged on.
- I found 3 agents who mysteriously have no roster records after late June.

## 8. What did you use AI for? (tools, models, where they helped, where they wasted time, what you threw away) + link to the 3-minute screen recording
Include: Antigravity and which model it used; any chat assistant; what each did; one place AI was wrong and how you caught it; what you discarded; the video link (upload to Drive, set to public).
- Notes while building (copy from logs/PROMPT_LOG.md):
- FINAL ANSWER:
I used ChatGPT to help explore the data and get some guidance, Claude to help plan the strategy and review my constraints, and Google Antigravity to write, refactor, and debug the actual code. Finally, I plugged in the Gemini API to optionally generate qualitative commentary on the results.

To stop the AI from hallucinating math, Python computes all the authoritative numbers. Gemini only sees the final summary metrics, and I heavily filter its output.

Early on, the AI kept trying to invent numbers in its prose, which I caught during testing. I fixed this by adding a strict rule in Python to block it from outputting digits entirely. I also threw away early ideas to build heavy web dashboards or do raw-ticket LLM analysis because keeping it simple, private, and local was better.

- Recording link: https://drive.google.com/file/d/12sgjrtqEGZm6rlUYiOtAII8_-mqlDRgQ/view?usp=sharing

## 9. Someone picks this up on Monday and you are unreachable: the three things they need to know
Include exactly three: (1) how to run it, (2) the key finding and the main assumption, (3) the biggest known problem or next step.
- Notes while building:
- FINAL ANSWER:
1. **How to run it:** Run `python -m src.clean` to clean the data, then run `python -m src.report --interactive` to use the CLI (you can type the API key securely there).
2. **The key finding:** The largest concentration of SLA breaches happens with tickets created at night, exactly when we have no frontline staff. The main assumption is that this pattern holds true at full volume.
3. **The biggest problem:** We need to talk to data engineering about the massive volume mismatch (177/week in the data vs 650/week quoted) before we can promise any real money savings.

## 10. Honest hours spent (one number)
Add up logs/HOURS_LOG.md. Give a single number, including time spent reading and fixing AI output.
- FINAL ANSWER:
8

## Links
- Public Google Drive link (memo, video, any extra files; check that it opens in a private window): https://drive.google.com/file/d/12sgjrtqEGZm6rlUYiOtAII8_-mqlDRgQ/view?usp=sharing
- Public GitHub repo URL (check that it opens logged out, README runs from a fresh clone, no API keys committed): https://github.com/Silverfang180/internship-project

---
## Final checklist before submitting
- [x] Every number in the form matches the memo and the tool output
- [ ] README tested on a fresh clone
- [ ] Video is 3 minutes or less and shows prompts, changes, and what was thrown away
- [ ] Memo is one page and non-technical
- [x] No keys or secrets in the repo
- [ ] Drive and GitHub links open without logging in
- [x] Test suite count: 27
