# Phase 2 Notes
1. We successfully ran `src/analyze.py` to test the preliminary numbers from the initial data plan against our cleaned dataset.
2. Every single hypothesis tested from Section A passed within the allowed tolerance (1 percentage point or 2 percent count variance), confirming the preliminary numbers were robust.
3. Our new analyses in Section B confirmed that the July breach rate spike was not caused by volume growth (only 17% up), channel mix changes, or tier mix changes.
4. The sole driver of the spike is the elimination of the Night shift on June 30, causing ~32 night tickets per night to automatically breach SLA while waiting for Morning agents.
5. Daytime agents are currently handling fewer than 3 tickets per day on average, showing a massive overcapacity during the day while the Night shift suffers from zero coverage.
