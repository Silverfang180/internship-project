# DECISIONS

## D1. Treat preliminary numbers as hypotheses (Phase 0)
The numbers in docs/02_DATA_AND_PLAN.md came from a quick first pass. They must be reproduced from the raw data in Phase 2 before being used anywhere.

## D2. Re-rostering may not be free (Phase 0, raised by Antigravity)
Three of the five Night-shift agents (A3001, A3016, A3017) have no assignment row after 29 Jun 2025. They may have left. Headcount is frozen, and ticket volume has roughly doubled. Moving agents from Morning or Day to Night could cause new breaches in the daytime. Decision: do not recommend "just re-roster" until Phase 2 checks daytime spare capacity.

## D3. Deduplication rule (Phase 1)
When duplicate `ticket_id`s are found, we keep the row with `source_system` equal to `helpdesk` and drop the `legacy_fd` row. This ensures we use the record with blank CSAT for no-response, rather than 0.

## D4. Failed IVR transcript detection (Phase 1 Fixes)
We set `ivr_failed = True` for any ticket in ANY channel whose `customer_message` contains `[inaudible]` or `[line dropped]`, plus any `voice` channel rows that contain only punctuation (after stripping the `[IVR transcript]` prefix, if any).

This resulted in 16 total flagged rows across all channels. Sameer's email estimated about 40 failed transcripts, so we found fewer. Note that 14 of these IVR-style transcripts sit in non-voice channels (chat, email, social) likely due to agent copy-pasting, meaning their SLA target may technically be wrong since they are evaluated under their assigned channel's SLA. This channel assignment was left unchanged.

## D5. Strict Date Parsing (Phase 1 Fixes)
The local copy of `tickets.csv` was found to have been altered to use slash dates (e.g. `13/01/2025 1:28`). It was replaced with the original raw data which correctly uses the format `YYYY-MM-DD HH:MM`. Date parsing for `created_at`, `first_response_at`, and `resolved_at` is now strictly enforced to use this exact format. If any non-blank value fails to parse with this format, the pipeline will raise an error and output the first 5 offending `ticket_ids`.