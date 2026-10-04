Phase 1 Notes:
- Converted UTC timestamps to IST successfully using Pandas timezone functions.
- Removed 616 duplicated tickets, keeping the new helpdesk entries to retain accurate missing CSAT values rather than legacy zeros.
- Flagged 14 IVR transcripts as failed based on missing data, line drops, or inaudibility.
- Successfully merged 100% of tickets with the roster using the correct shift date boundaries.
- Computed and appended SLA response times, targets, and breach costs. No calculation issues found.
