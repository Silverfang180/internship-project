# Analysis Notes

## 1. Findings Evaluated
We tested the initial hypotheses from the preliminary data overview. All held within tolerance:
* The overall breach rate is 21.8% (2440/11200).
* The breach rate by channel is Chat 27.6%, Social 22.0%, Email 20.4%, Voice 5.6%.
* The breach rate jumped from 9.3% (Before 1 Jul) to 24.9% (After 1 Jul).
* The Night shift breach rate is 65.6%, while Morning is 9.7% and Day is 8.9%.
* Night-created breach rate after 30 Jun is 79.1%, and for Night-created chat it is 100.0%.
* Night-created breaches are resolved by Morning shift agents 96.0% of the time (1566 out of 1631).
* Night shift agents dropped from 5 on 1 Jun to 0 on 15 Jul.
* Transfers breach rate is 20.7%, versus 21.9% for non-transfers.

## 2. Alternative Explanations Evaluated
We evaluated explanations for the July 2025 SLA spike:
* **Volume Growth:** Ticket volume increased by 17.3% (from 405 in June to 475 in July).
* **Channel and Tier Mix:** Chat share remained flat (42.7% in Jun, 42.5% in Jul). Tier 1 handled 93.8% of tickets in June and 92.8% in July.
* **Product Launches:** Pulse 2 (VA-EB-PL2) share grew from 1.2% before 1 Jul to 35.6% after 1 Jul. However, the Night-chat breach rate after 30 Jun was 100.0% for Pulse 2 and 100.0% for all other SKUs, showing the product is not the cause of night breaches.
* **Daytime Load:** Morning+Day ticket volume correlates with the breach rate at only 0.198. Their combined breach rate was 8.9% before 1 Jul (159/1777) and 9.4% after 1 Jul (650/6937), showing Morning+Day breach rates did not spike like the overall rate.

## 3. Detailed Impacts of the Night Shift Removal
* **Breach Composition:** After 30 Jun, Night-created breaches by channel were: chat 1034 (65.5%), email 387 (24.5%), and social 158 (10.0%). Night-created tickets now account for 70.8% of all post-July breaches.
* **SLA Timing:** Night-created email breach rate was 81.0% for hours 22-23 compared to 6.1% for hours 0-5 (which have enough time to be resolved when the Morning shift arrives).
* **Cost and Quality:** Average credits issued per month increased from Rs 12,308 (before 1 Jul) to Rs 65,012 (after 1 Jul). Average CSAT (excluding blanks) dropped from 3.46 to 3.34 over the same periods.
* **Staffing Gap:** The roster shows that both Night email agents and one Night chat agent have no later roster row after 29 Jun 2025, meaning staffing actively fell by 3.

## 4. Conclusions
The elimination of the Night shift on June 30 is the main driver supported by the data (though this data alone cannot definitively prove it, as we lack individual agent utilization, exact volume distributions matching the brief, or detailed queue mechanics).
Starting July 1, there are 5.5 tickets per night (2.8 chat, 2.1 email, 0.5 social). Because the Night agent count dropped to 0, these tickets wait. The median wait time for Night chat is 432.0 minutes, with a 90th percentile wait of 505.0 minutes. When Morning agents begin responding, the first responses cluster at 06:00 (1068 responses) and 07:00 (582 responses) IST, by which time the SLA has breached for chat and social tickets.

**Business Scenario:**
* Agent-shift cost = 8 x Rs 165 per night = Rs 1,320.
* Credits avoided per night under a 10% breach rate scenario at export volume: Rs 1,322.6.
* Assumption: Scaled by 650/177 to match the brief's volume, credits avoided per night: Rs 4,857.1.
* Break-even weekly ticket volume: 171.0 tickets/week.
* Note: If headcount is frozen, the cost is a re-roster from Day, not a new hire. At export volume the credits avoided per night are roughly equal to the agent-shift cost, so the case depends on true volume, CSAT and the cost of moving a Day agent.

## 5. Limits of the Analysis
* **Sample Size:** The data export averages about 177 tickets a week, while the initial brief states a volume of about 650 tickets a week. Due to this discrepancy, exact workload and capacity per agent cannot be reliably inferred.
* **Missing Agents:** There are 3 agents (1 Chat Frontline, 2 Email Frontline in Indore) whose roster `to_date` ended on or before 29 Jun 2025 and who do not reappear in the roster data. 
* **IVR Tickets:** There are 14 failed IVR-style transcripts sitting in non-voice channels (chat, email, social). They are currently evaluated against those non-voice SLA targets (e.g. 15 mins for chat) rather than the voice SLA targets, which might technically misrepresent their breach status.
