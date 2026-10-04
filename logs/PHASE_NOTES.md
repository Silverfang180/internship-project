# Phase 2 Notes
1. We successfully ran `src/analyze.py` to test the preliminary numbers from the initial data plan against our cleaned dataset.
2. Every single hypothesis tested from Section A passed within the allowed tolerance (1 percentage point or 2 percent count variance), confirming the preliminary numbers were robust.
3. Our new analyses in Section B confirmed that the July breach rate spike was not caused by volume growth (only 17% up), channel mix changes, or tier mix changes.
4. **SUPERSEDED (Day-count bug):** The initial analysis suggested that the sole driver caused "~32 night tickets per night" to breach. *Correction: This figure was incorrect due to a day-count bug. The corrected figure is Night volume after 30 Jun 2025 = 1,997 tickets / 365 days = approximately 5.5 tickets/night.*
5. **SUPERSEDED (Day-count bug):** We previously stated daytime agents were handling fewer than 3 tickets/day. *Correction: This was also impacted by the same bug. Workload/utilization per agent cannot be inferred because the export volume (~177 tickets/week) is significantly lower than the brief's "~650/week" estimate.*

# Phase 4 Bug Audit Notes
- Performed pre-CLI bug audit; system is stable overall.
- Reproduced Tier 2 bug in `src/report.py` (`resolver_tier` integer vs string comparison).
- Applied minimal fix: changed filter to `df_curr['resolver_tier'] == 2`.
- Added regression test `test_tier2_exclusion` to `tests/test_report.py`.
- Final test result: 14/14 tests pass, Tier 2 exclusion working as expected.
- **Phase 4 Validation COMPLETE**: 30/30 shift, 30/30 breach, zero observed errors. (Random: 14/14, shift-boundary: 4/4, target-boundary: 4/4, date-rollover: 4/4, exactly-at-target: 4/4). Rule of 3 (95% upper bound) = 10%.
