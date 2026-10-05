# Vireo SLA Analysis
A local Python operations-intelligence tool for analyzing first-response SLA performance, identifying operational patterns, and generating optional AI-assisted manager commentary.

## 1. Overview
The project analyzes support-ticket SLA performance. Python is authoritative for all numerical calculations. The tool identifies patterns such as shift/time-of-ticket-creation and SLA breaches. Gemini is optional and only provides qualitative commentary. The system works fully without an AI API key. This is a local analysis/decision-support tool, not an autonomous production system.

## 2. Business Objective
The post-July first-response SLA breach rate is approximately 24.9%.
The pilot target is 15% or lower.
Verified credit exposure after July is approximately ₹65,012/month.
A proportional reduction from 24.9% to 15% is approximately 39.8%.
This produces a scenario of approximately ₹25,848/month or ₹77,544/quarter.

**IMPORTANT:** This is a scenario, NOT a guaranteed savings forecast. The major assumption is that the observed pattern continues during the pilot and that moving staff does not simply create new daytime breaches.

## 3. Key Findings
* SLA breach rate increased beginning in July 2025.
* Night staffing dropped to zero after June 30, 2025.
* Tickets created at night became the largest concentration of post-July breaches.
* The standard resolving-agent view can unfairly attribute overnight breaches to agents who inherited already-breached tickets.
* Three agents are missing roster records after June 29, 2025.

**Unresolved Validation Issue:**
There is a major data-volume discrepancy. The supplied data contains approximately 177 tickets/week, whereas the brief references approximately 650 tickets/week.

## 4. Project Architecture / How It Works
Raw data → cleaning → validation → SLA calculation → shift/channel analysis → report generation → optional AI commentary

Python produces the authoritative metrics. The AI layer does NOT determine the numerical results.

## 5. Requirements
* Python 3.12 or compatible Python 3 version
* Git (recommended for cloning)

The project uses a Python virtual environment.

## 6. Data Setup
The original raw pack contains these 8 files:
* `tickets.csv`
* `agents.csv`
* `orders.csv`
* `customers.csv`
* `products.csv`
* `support-policy.pdf`
* `email-thread.txt`
* `README.txt`

These should be placed in: `data/`

**IMPORTANT:** The raw files contain customer/source data and are intentionally excluded from Git. The project cannot reproduce the complete analysis from a fresh clone unless the required raw data is supplied separately.

## 7. Installation
**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

## 8. Run the Data Cleaning Step
```bash
python -m src.clean
```
This step cleans the raw data, applies strict date parsing, determines ticket creation shifts, and calculates SLA breaches based on predefined channel targets.

## 9. Run the Deterministic Report
```bash
python -m src.report --start 2026-06-22 --end 2026-06-28
```
This generates the report using deterministic Python calculations.

To save the report as Markdown:
```bash
python -m src.report --start 2026-06-22 --end 2026-06-28 --out output/report.md
```

## 10. Interactive Manager Mode
```bash
python -m src.report --interactive
```
This allows the user to:
* choose the reporting period
* run deterministic analysis
* optionally enable AI commentary
* enter an API key interactively if desired

The deterministic analysis does NOT require an API key.

## 11. Optional Gemini AI
Gemini is optional. The deterministic report works without it. Users need their own Gemini API key for live AI commentary. The key can be supplied through `.env` or interactively. The application does not intentionally commit/store API keys in Git. Raw ticket/customer records are not sent to the model. Only aggregate/summary metrics are passed for qualitative commentary. Python remains authoritative for numerical results. AI output is constrained to prevent it from inventing numerical evidence. If the API key is absent or the request fails, the application falls back to the deterministic report.

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**Mac/Linux:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

`.env` is ignored by Git and users must never commit their API key.

## 12. Output / Important Files
| Path | Description |
|---|---|
| `src/` | application code |
| `tests/` | automated tests |
| `docs/memo-neha-kulkarni.md` | client-facing memo |
| `logs/FORM_DRAFT.md` | detailed submission answer draft |
| `output/` | selected generated/validation artifacts that are intentionally included |
| `verification_report.md` | final engineering verification notes |
| `requirements.txt` | Python dependencies |

## 13. Client Memo
The client-facing memo is available at: `docs/memo-neha-kulkarni.md`

This is the concise business-facing summary and should be read before diving into the technical implementation.

## 14. Validation / Testing
* Manual sample: 30 tickets.
* Correct shift: 30/30.
* Correct SLA breach classification: 30/30.
* Observed sample error rate: 0.0%.
* Automated test suite: 27 tests.

The 30-ticket manual sample does NOT prove zero errors across the entire dataset.

## 15. Known Limitations
* Data volume mismatch: approximately 177 tickets/week vs approximately 650 in the brief.
* Three agents missing roster records after June 29, 2025.
* 14 IVR-style transcripts in non-voice channels may have incorrect SLA targets in the source data.
* No queue/utilization data is available to prove staffing causality mathematically.
* Manual validation covered only 30 tickets.
* Financial savings are a scenario, not a guarantee.
* The tool is local and is not presented as a production deployment.
* Tier 2 is excluded from Tier 1 comparisons.

## 16. What Was Deliberately Not Built
* No heavy web dashboard/UI.
* No per-agent blame leaderboard.
* No raw-ticket LLM analysis.
* No unnecessary infrastructure/hosting layer.

These choices were made to keep the tool simple, local, privacy-conscious, and focused on the business question.

## 17. Submission Links
* GitHub: [https://github.com/Silverfang180/internship-project](https://github.com/Silverfang180/internship-project)
* Screen Recording: [https://drive.google.com/file/d/12sgjrtqEGZm6rlUYiOtAII8_-mqlDRgQ/view?usp=sharing](https://drive.google.com/file/d/12sgjrtqEGZm6rlUYiOtAII8_-mqlDRgQ/view?usp=sharing)
