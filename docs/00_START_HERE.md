# 00 START HERE — Vireo Audio Task 1 (Antigravity pack)

Budget: **about 5 hours of work, hard cap.** Deadline: 48 h from receipt (check the portal clock).
Going over is not rewarded. A small tool that runs beats a big one that doesn't.

## 1. Set up the project folder (10 min)
```
vireo-sla/
  data/                  <- copy all 8 task files here (tickets.csv, agents.csv, orders.csv,
                            customers.csv, products.csv, support-policy.pdf,
                            email-thread.txt, README.txt)
  docs/                  <- copy these 3 files here: 00_START_HERE, 01_TASK_AND_CONTEXT, 02_DATA_AND_PLAN
  src/                   <- code goes here (Antigravity creates it)
  logs/
    PROMPT_LOG.md        <- you paste every important prompt + what changed + what you discarded
    COST_LOG.md          <- tools, models, rough Rs/USD spent
    HOURS_LOG.md         <- honest start/stop times
  README.md              <- must run on a clean machine (Antigravity writes it, you test it)
```
Create `git init` and a public GitHub repo at the start. Commit after each phase.
Do NOT commit anything secret (API keys) — use a `.env` file and add it to `.gitignore`.

## 2. Kickoff prompt (paste into Antigravity's agent chat, Planning mode)
```
You are helping me complete a 5-hour hiring task. Read every file in /docs first
(01_TASK_AND_CONTEXT.md and 02_DATA_AND_PLAN.md), then the raw files in /data.
Do not write code yet. First reply with:
1. A 10-line summary of what the client actually needs (not just what Neha literally asked).
2. The data problems you will handle before computing any breach number.
3. Your phase plan with time boxes, following 02_DATA_AND_PLAN.md.
Then wait for my approval before starting Phase 1.
Rules: keep it small; plain pandas is fine; no paid API calls unless I approve;
after every phase write a 5-line plain-English explanation of what the code does
and what could be wrong, into logs/PHASE_NOTES.md.
```

## 3. Your rules (these protect you in the next interview round)
1. **Explain-back:** after each phase, read the code once and be able to say what each function does. A later round may ask you.
2. **Log as you go:** paste prompts into `PROMPT_LOG.md` with "version 1 → version 2: what I changed and why", and note anything you threw away. The 3-minute video is built from this log.
3. **Never trust the first number.** Ask the agent to show the rows behind every figure, then spot-check by hand.
4. **Verify claims from `02_DATA_AND_PLAN.md` yourself.** They were derived in a quick first pass and are marked preliminary.
5. **Do not overclaim.** The form rewards honesty about bugs, shortcuts and what AI got wrong.
6. Stop at hour 5. Write "what I left out and why" instead of squeezing in more.

## 4. Suggested time boxes
| Phase | Time |
|---|---|
| Read docs + approve plan | 30 min |
| P1 Clean data (UTC→IST, dedupe, roster join) | 60 min |
| P2 Breach metrics + root cause + business number | 75 min |
| P3 Small tool (CLI that outputs weekly report) | 60 min |
| P4 Validation (hand-checked sample, error rate) | 40 min |
| P5 Memo + 3-min video + form + README test | 55 min |
