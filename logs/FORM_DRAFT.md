# FORM_DRAFT — fill in AFTER the project is finished
Put this file in `logs/FORM_DRAFT.md`. Copy the final answers into the portal.
Rule: every claim must be something you checked. Numbers come from your own re-run, not from chat notes.
Keep notes as you go in the "Notes while building" box under each question, then write the final answer at the end.

---
## 1. What did you build, and what business outcome does it move? (state the number and the money)
Include: what the tool does in one sentence; the business goal as a number (from A% to B%); the rupee value per quarter and the arithmetic (breaches avoided x Rs 350, plus any other cost you can support); the assumptions behind it.
- Notes while building:
- FINAL ANSWER:

## 2. What does one run cost, and what would a month cost at ~650 tickets/week? (show the arithmetic)
Include: paid API calls, yes or no; if none, say "Rs 0 in model calls"; if any, tokens per ticket x price x (650 x ~4.3 tickets/month); compute and storage cost if relevant.
- Notes while building:
- FINAL ANSWER:

## 3. How do you know it works? (sample size, how you checked, error rate, the kind of case it gets wrong)
Include: how many tickets you hand-checked and how you picked them; how many were right and wrong; the error rate; the typical failure (e.g. shift-boundary times, roster-date edges, duplicates); what you did not test.
- Notes while building:
- FINAL ANSWER:

## 4. Did you change, narrow, or push back on the client's ask? (what, when, and why) [can only raise your score]
Include: what Neha asked for; what you did instead or in addition (e.g. shift of ticket creation vs resolving agent, no per-person league table, no hiring); what evidence made you change it; when in the process (which phase).
- Notes while building:
- FINAL ANSWER:

## 5. What is wrong with what you are handing us? (be specific: bugs, shortcuts, things you know are off) [can only raise your score]
Include: known bugs; shortcuts and assumptions (duplicate rule, breach definition, timezone handling); data you did not verify; anything AI wrote that you only partly understand; limits of the business-number estimate.
- Notes while building:
- FINAL ANSWER:

## 6. What did you deliberately leave out, and why that rather than something else?
Include: 2-4 things (e.g. refund/replacement anomalies, ticket-text classification, per-agent ranking, dashboard UI) and the reason you chose to skip each over what you built.
- Notes while building:
- FINAL ANSWER:

## 7. Anything you built or found that nobody asked for?
Include: only verified findings (e.g. the July 2025 step change, Night coverage dropping to zero, the standard report charging the resolving agent). Say how you verified each.
- Notes while building:
- FINAL ANSWER:

## 8. What did you use AI for? (tools, models, where they helped, where they wasted time, what you threw away) + link to the 3-minute screen recording
Include: Antigravity and which model it used; any chat assistant; what each did; one place AI was wrong and how you caught it; what you discarded; the video link (upload to Drive, set to public).
- Notes while building (copy from logs/PROMPT_LOG.md):
- FINAL ANSWER:

## 9. Someone picks this up on Monday and you are unreachable: the three things they need to know
Include exactly three: (1) how to run it, (2) the key finding and the main assumption, (3) the biggest known problem or next step.
- Notes while building:
- FINAL ANSWER:

## 10. Honest hours spent (one number)
Add up logs/HOURS_LOG.md. Give a single number, including time spent reading and fixing AI output.
- FINAL ANSWER:

## Links
- Public Google Drive link (memo, video, any extra files; check that it opens in a private window):
- Public GitHub repo URL (check that it opens logged out, README runs from a fresh clone, no API keys committed):

---
## Final checklist before submitting
- [ ] Every number in the form matches the memo and the tool output
- [ ] README tested on a fresh clone
- [ ] Video is 3 minutes or less and shows prompts, changes, and what was thrown away
- [ ] Memo is one page and non-technical
- [ ] No keys or secrets in the repo
- [ ] Drive and GitHub links open without logging in
