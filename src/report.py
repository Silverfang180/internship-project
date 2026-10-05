import argparse
import pandas as pd
import numpy as np
import os
import sys

from src.cli_input import getpass_asterisk
from src.config import NIGHT_FINDING_MIN_BREACH_PCT, NIGHT_FINDING_RATE_MULTIPLIER

def escape_md(val):
    if isinstance(val, str) and val.startswith(('=', '+', '-', '@')):
        return "'" + val
    return val

def build_ai_metrics(start_date, end_date, curr_tickets, curr_breaches, curr_rate, curr_credits, night_metrics):
    return {
        "reporting_period": f"{start_date} to {end_date}",
        "current_period_tickets": int(curr_tickets),
        "sla_breaches": int(curr_breaches),
        "breach_rate": f"{curr_rate:.1f}%",
        "night_specific_metrics": night_metrics
    }

def run_report(start_date, end_date, out_path=None, df_tickets=None, df_agents=None, **kwargs):
    input_csv = kwargs.get('input_csv', 'output/clean_tickets.csv')
    is_interactive = kwargs.get('is_interactive', False)
    api_key = kwargs.get('api_key')
    use_ai = kwargs.get('use_ai', False)

    if df_tickets is None:
        if not os.path.exists(input_csv):
            sys.exit(f"Run python -m src.clean first (missing {input_csv})")
        df = pd.read_csv(input_csv)
    else:
        df = df_tickets.copy()

    df['created_at'] = pd.to_datetime(df['created_at'])
    df['created_at_ist'] = pd.to_datetime(df['created_at'], utc=True).dt.tz_convert('Asia/Kolkata')
    df['created_date'] = df['created_at_ist'].dt.date

    try:
        start_dt = pd.to_datetime(start_date).date()
        end_dt = pd.to_datetime(end_date).date()
    except Exception:
        print("Error: Invalid date format. Please use YYYY-MM-DD.")
        sys.exit(2)

    if start_dt > end_dt:
        print("Error: Start date cannot be after end date.")
        sys.exit(2)

    period_days = (end_dt - start_dt).days + 1
    prev_end_dt = start_dt - pd.Timedelta(days=1)
    prev_start_dt = start_dt - pd.Timedelta(days=period_days)

    df_curr = df[(df['created_date'] >= start_dt) & (df['created_date'] <= end_dt)]
    df_prev = df[(df['created_date'] >= prev_start_dt) & (df['created_date'] <= prev_end_dt)]

    curr_tickets = len(df_curr)
    curr_breaches = df_curr['breach'].sum()
    curr_rate = curr_breaches / curr_tickets * 100 if curr_tickets > 0 else 0
    curr_credits = curr_breaches * 350

    prev_tickets = len(df_prev)
    prev_breaches = df_prev['breach'].sum()
    prev_rate = prev_breaches / prev_tickets * 100 if prev_tickets > 0 else 0
    prev_credits = prev_breaches * 350

    ch_to_team = {
        'chat': 'Chat Frontline',
        'social': 'Chat Frontline',
        'email': 'Email Frontline',
        'voice': 'Voice Frontline'
    }
    team_to_ch = {}
    for ch, team in ch_to_team.items():
        team_to_ch.setdefault(team, []).append(ch)

    if df_agents is None:
        agents_csv = kwargs.get('agents_csv', 'data/agents.csv')
        agents = pd.read_csv(agents_csv)
    else:
        agents = df_agents.copy()

    agents['from_date'] = pd.to_datetime(agents['from_date']).dt.date
    agents['to_date'] = pd.to_datetime(agents['to_date']).dt.date
    agents['to_date'] = agents['to_date'].fillna(pd.to_datetime('2099-12-31').date())

    date_range = [start_dt + pd.Timedelta(days=i) for i in range(period_days)]
    gap_summary = []

    for team, channels in team_to_ch.items():
        for shift in ['Morning', 'Day', 'Night']:
            days_zero_staff = 0
            gap_tix_total = 0
            gap_br_total = 0
            for d in date_range:
                staffed_agents = agents[(agents['from_date'] <= d) & (agents['to_date'] >= d)]
                count = len(staffed_agents[(staffed_agents['team'] == team) & (staffed_agents['shift'] == shift)])
                if count == 0:
                    days_zero_staff += 1
                    gap_tix = df_curr[(df_curr['created_date'] == d) & (df_curr['created_shift_ist'] == shift) & (df_curr['channel'].isin(channels))]
                    gap_tix_total += len(gap_tix)
                    gap_br_total += gap_tix['breach'].sum()

            if days_zero_staff > 0 and gap_tix_total > 0:
                br_rate = gap_br_total / gap_tix_total * 100
                gap_summary.append({
                    'Team': team,
                    'Shift': shift,
                    'Zero Staff Days': days_zero_staff,
                    'Gap Tickets': gap_tix_total,
                    'Gap Breaches': gap_br_total,
                    'Gap Rate': f"{br_rate:.1f}%"
                })

    night_metrics = {}
    night_finding_applies = False
    top_night_channels = []

    if curr_tickets > 0:
        agg2 = df_curr.groupby(['created_shift_ist', 'channel']).agg(
            Tickets=('ticket_id', 'count'),
            Breaches=('breach', 'sum')
        ).reset_index()

        night_breaches = 0
        night_tickets = 0
        md_breaches = 0
        md_tickets = 0
        night_channels = []

        for _, r in agg2.iterrows():
            if r['created_shift_ist'] == 'Night':
                rate = (r['Breaches'] / r['Tickets'] * 100) if r['Tickets'] > 0 else 0
                night_metrics[f"Night {r['channel'].capitalize()}"] = f"{r['Breaches']}/{r['Tickets']} breaches ({rate:.1f}%)"
                night_breaches += r['Breaches']
                night_tickets += r['Tickets']
                night_channels.append((r['channel'].capitalize(), r['Breaches']))
            else:
                md_breaches += r['Breaches']
                md_tickets += r['Tickets']

        night_rate = night_breaches / night_tickets if night_tickets > 0 else 0
        md_rate = md_breaches / md_tickets if md_tickets > 0 else 0

        has_zero_staff_gap = any(g['Gap Tickets'] > 0 for g in gap_summary)
        is_majority_breaches = (night_breaches / curr_breaches) >= NIGHT_FINDING_MIN_BREACH_PCT if curr_breaches > 0 else False
        is_2x_rate = night_rate >= (md_rate * NIGHT_FINDING_RATE_MULTIPLIER)

        if has_zero_staff_gap and is_majority_breaches and is_2x_rate:
            night_finding_applies = True
            night_channels.sort(key=lambda x: x[1], reverse=True)
            top_channels_list = [c[0] for c in night_channels if c[1] > 0]
            if len(top_channels_list) > 1:
                top_night_channels = ", ".join(top_channels_list[:-1]) + " and " + top_channels_list[-1]
            elif len(top_channels_list) == 1:
                top_night_channels = top_channels_list[0]
            else:
                top_night_channels = "various channels"

    if is_interactive:
        report_lines = []
        start_fmt = start_dt.strftime('%d %b %Y').lstrip('0')
        end_fmt = end_dt.strftime('%d %b %Y').lstrip('0')

        report_lines.append("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
        report_lines.append("  REPORT")
        report_lines.append("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€\n")
        report_lines.append(f"  {'Period':<16} {start_fmt} â†’ {end_fmt}")
        report_lines.append(f"  {'Tickets':<16} {curr_tickets}")
        report_lines.append(f"  {'SLA breaches':<16} {curr_breaches}")
        report_lines.append(f"  {'Breach rate':<16} {curr_rate:.1f}%")
        report_lines.append(f"  {'Credit exposure':<16} â‚¹{curr_credits:,.0f}\n")

        report_lines.append("  â”Œâ”€ TOP SIGNAL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”")
        if night_finding_applies:
            import textwrap
            msg = f"The largest concentration of SLA breaches is in Night-created tickets, particularly {top_night_channels}, coinciding with the absence of overnight frontline coverage."
            wrapped = textwrap.wrap(msg, width=51)
            for line in wrapped:
                report_lines.append(f"  â”‚ {line:<53} â”‚")
        else:
            report_lines.append("  â”‚ No single shift or channel stands out this period.    â”‚")
        report_lines.append("  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜\n")

        if use_ai:
            try:
                from src.ai_insight import generate_insight
                metrics_dict = build_ai_metrics(start_date, end_date, curr_tickets, curr_breaches, curr_rate, curr_credits, night_metrics)
                insight = generate_insight(metrics_dict, api_key=api_key)

                if not kwargs.get('header_already_printed'):
                    report_lines.append("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
                    report_lines.append("  AI Manager Commentary")
                    report_lines.append("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€\n")

                if insight == "WITHHELD":
                    report_lines.append("  AI commentary withheld by safety check; the report above is unaffected.")
                    report_lines.append("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
                elif insight:
                    report_lines.append("  What happened")
                    import textwrap
                    report_lines.append(textwrap.fill(insight.get('what_happened', ''), width=58, initial_indent="  ", subsequent_indent="  "))

                    report_lines.append("\n  Numerical evidence computed by Python")
                    for k, v in night_metrics.items():
                        report_lines.append(f"  â€¢ {k:<15} {v}")

                    report_lines.append("\n  What this suggests")
                    report_lines.append(textwrap.fill(insight.get('interpretation', ''), width=58, initial_indent="  ", subsequent_indent="  "))
                    report_lines.append("\n  Recommended test")
                    report_lines.append(textwrap.fill(insight.get('recommended_test', ''), width=58, initial_indent="  ", subsequent_indent="  "))
                    report_lines.append("\n  Caveat")
                    report_lines.append(textwrap.fill(insight.get('caveat', ''), width=58, initial_indent="  ", subsequent_indent="  "))

                    report_lines.append("\nâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
                    report_lines.append("  AI insight: enabled")
                    report_lines.append("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
                else:
                    report_lines.append("  AI insight unavailable; deterministic report generated successfully.")
                    report_lines.append("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
            except ImportError:
                if not kwargs.get('header_already_printed'):
                    report_lines.append("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
                    report_lines.append("  AI Manager Commentary")
                    report_lines.append("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€\n")
                report_lines.append("  AI insight unavailable; deterministic report generated successfully.")
                report_lines.append("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
        else:
            if kwargs.get('header_already_printed'):
                report_lines.append("  AI insight unavailable; deterministic report generated successfully.")
                report_lines.append("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
            else:
                report_lines.append("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
                report_lines.append("  AI Manager Commentary")
                report_lines.append("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€\n")
                report_lines.append("  AI insight unavailable; deterministic report generated successfully.")
                report_lines.append("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")

        print('\n'.join(report_lines))
        return

    report_lines = []
    report_lines.append("# VIREO AUDIO â€” SUPPORT SLA INTELLIGENCE")
    report_lines.append(f"**Reporting Period:** {start_date} to {end_date}")
    report_lines.append(f"Source: {input_csv}")
    report_lines.append("")
    report_lines.append("## 1. Headline Summary")
    report_lines.append(f"**Current Period:** {curr_rate:.1f}% breach rate ({curr_breaches}/{curr_tickets} tickets), Rs {curr_credits} credits.")

    if prev_tickets > 0:
        report_lines.append(f"**Previous Period ({prev_start_dt} to {prev_end_dt}):** {prev_rate:.1f}% breach rate ({prev_breaches}/{prev_tickets} tickets), Rs {prev_credits} credits.")
    else:
        report_lines.append("**Previous Period:** No data available for comparison.")

    report_lines.append("\n## 2. Breaches by Creation Shift and Channel")
    if curr_tickets > 0:
        agg2 = df_curr.groupby(['created_shift_ist', 'channel']).agg(
            Tickets=('ticket_id', 'count'),
            Breaches=('breach', 'sum')
        ).reset_index()
        agg2['Breach Rate'] = (agg2['Breaches'] / agg2['Tickets'] * 100).round(1).astype(str) + '%'

        report_lines.append("| Shift | Channel | Tickets | Breaches | Rate |")
        report_lines.append("|---|---|---|---|---|")
        for _, r in agg2.iterrows():
            shift = escape_md(str(r['created_shift_ist']))
            ch = escape_md(str(r['channel']))
            report_lines.append(f"| {shift} | {ch} | {r['Tickets']} | {r['Breaches']} | {r['Breach Rate']} |")
    else:
        report_lines.append("No tickets in this period.")

    report_lines.append("\n## 3. Coverage Gaps")
    report_lines.append("*Note: Voice callbacks run 08:00-22:00 only, so Night gaps for Voice are expected.*")

    if gap_summary:
        report_lines.append("| Team | Shift | Zero Staff Days | Gap Tickets | Gap Breaches | Gap Rate |")
        report_lines.append("|---|---|---|---|---|---|")
        for g in gap_summary:
            report_lines.append(f"| {escape_md(g['Team'])} | {escape_md(g['Shift'])} | {g['Zero Staff Days']} | {g['Gap Tickets']} | {g['Gap Breaches']} | {g['Gap Rate']} |")
    else:
        report_lines.append("No coverage gaps found with created tickets.")

    report_lines.append("\n## 4. Weekly Trend")
    if curr_tickets > 0:
        df_curr = df_curr.copy()
        df_curr['week_start'] = df_curr['created_at_ist'].dt.tz_localize(None).dt.to_period('W-SUN').dt.start_time.dt.date
        agg4 = df_curr.groupby('week_start').agg(
            Tickets=('ticket_id', 'count'),
            Breaches=('breach', 'sum')
        ).reset_index()
        agg4['Breach Rate'] = (agg4['Breaches'] / agg4['Tickets'] * 100).round(1).astype(str) + '%'

        report_lines.append("| Week Start (IST) | Tickets | Breaches | Rate |")
        report_lines.append("|---|---|---|---|")
        for _, r in agg4.iterrows():
            ws = escape_md(str(r['week_start']))
            report_lines.append(f"| {ws} | {r['Tickets']} | {r['Breaches']} | {r['Breach Rate']} |")
    else:
        report_lines.append("No tickets in this period.")

    report_lines.append("\n## 5. Resolved By (Shift and Team)")
    report_lines.append("*Note: The resolving agent is not necessarily who should have responded first. Tier 2 is excluded.*")
    report_lines.append("Breaches counted against a shift include tickets that arrived while no one was on shift.")

    if curr_tickets > 0:
        is_tier2 = (df_curr['resolver_tier'] == 2) | (df_curr['assigned_team'] == 'Escalations & Warranty')
        tier2_count = df_curr[is_tier2]['ticket_id'].count()

        df_t1 = df_curr[~is_tier2].copy()
        df_t1['is_night_created'] = df_t1['created_shift_ist'] == 'Night'
        df_t1['inherited_breach'] = df_t1['breach'] & df_t1['is_night_created']

        agg5 = df_t1.groupby(['resolver_shift', 'assigned_team']).agg(
            Tickets=('ticket_id', 'count'),
            Breaches=('breach', 'sum'),
            NightTickets=('is_night_created', 'sum'),
            InheritedBreaches=('inherited_breach', 'sum')
        ).reset_index()

        agg5['Breach Rate'] = (agg5['Breaches'] / agg5['Tickets'] * 100).round(1).astype(str) + '%'

        excl_night_tickets = agg5['Tickets'] - agg5['NightTickets']
        excl_night_breaches = agg5['Breaches'] - agg5['InheritedBreaches']
        agg5['ExclNightRate'] = np.where(excl_night_tickets > 0, (excl_night_breaches / excl_night_tickets * 100).round(1).astype(str) + '%', 'N/A')

        report_lines.append("| Shift | Team | Tickets | Breaches | Rate | Inherited | Excl. Night Rate |")
        report_lines.append("|---|---|---|---|---|---|---|")
        for _, r in agg5.iterrows():
            shift = escape_md(str(r['resolver_shift']))
            team = escape_md(str(r['assigned_team']))
            report_lines.append(f"| {shift} | {team} | {r['Tickets']} | {r['Breaches']} | {r['Breach Rate']} | {r['InheritedBreaches']} | {r['ExclNightRate']} |")

        report_lines.append(f"\n*Excluded Tier 2 / Escalations tickets: {tier2_count}*")

    report_lines.append("\n## Key Findings & Business Implication")
    if night_finding_applies:
        report_lines.append(f"- **Key Finding:** The largest concentration of SLA breaches is in Night-created tickets, particularly {top_night_channels}, coinciding with the absence of overnight frontline coverage.")
        report_lines.append("- **Business Implication:** Addressing Night coverage gaps should reduce credit exposure if the pattern holds; confirm with a pilot.")
    else:
        report_lines.append("- **Key Finding:** No single shift or channel stands out this period.")

    if use_ai:
        try:
            from src.ai_insight import generate_insight
            metrics_dict = build_ai_metrics(start_date, end_date, curr_tickets, curr_breaches, curr_rate, curr_credits, night_metrics)
            insight = generate_insight(metrics_dict, api_key=api_key)
            report_lines.append("\n## AI Manager Commentary")
            if insight == "WITHHELD":
                report_lines.append("*AI commentary withheld by safety check; the report above is unaffected.*")
            elif insight:
                report_lines.append(f"- **What Happened:** {insight.get('what_happened', '')}")
                report_lines.append(f"- **Numerical evidence computed by Python:**")
                for k, v in night_metrics.items():
                    report_lines.append(f"  - {k}: {v}")
                report_lines.append(f"- **Interpretation:** {insight.get('interpretation', '')}")
                report_lines.append(f"- **Recommended Action:** {insight.get('recommended_test', '')}")
                report_lines.append(f"- **Caveat:** {insight.get('caveat', '')}")
            else:
                report_lines.append("*AI insight unavailable; deterministic report generated successfully.*")
        except ImportError:
            report_lines.append("\n## AI Manager Commentary")
            report_lines.append("*AI insight unavailable; deterministic report generated successfully.*")

    report_lines.append("\n## Caveats")
    report_lines.append("- The export has about 177 tickets a week vs about 650 quoted.")
    report_lines.append("- 14 IVR-style transcripts in non-voice channels may have the wrong target.")
    report_lines.append("- 3 agents have no later roster row.")
    report_lines.append("- No queue or utilization data was provided, so causation cannot be confirmed.")

    if out_path:
        out_dir = os.path.dirname(out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines) + '\n')
        print(f"Report written to {out_path}")
    else:
        print('\n'.join(report_lines))

def load_dotenv(filepath=".env"):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Generate weekly SLA report")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive manager mode")
    parser.add_argument("--start", help="Start date YYYY-MM-DD (inclusive)")
    parser.add_argument("--end", help="End date YYYY-MM-DD (inclusive)")
    parser.add_argument("--out", help="Output markdown file path (optional, defaults to stdout)")
    parser.add_argument("--input", default="output/clean_tickets.csv", help="Input cleaned tickets CSV")
    parser.add_argument("--agents", default="data/agents.csv", help="Input agents CSV")
    args = parser.parse_args()

    is_interactive = args.interactive

    if is_interactive:
        print("â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—")
        print("â•‘              VIREO AUDIO                                 â•‘")
        print("â•‘          SUPPORT SLA INTELLIGENCE                        â•‘")
        print("â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•\n")
        print("  What would you like to analyze?\n")
        print("    [1] Latest available week")
        print("    [2] Choose a date range")
        print("    [3] Exit\n")

        choice = input("  Choice: ").strip()

        if choice == '1':
            if not os.path.exists(args.input):
                sys.exit(f"Run python -m src.clean first (missing {args.input})")
            df_temp = pd.read_csv(args.input)
            df_temp['created_at_ist'] = pd.to_datetime(df_temp['created_at'], utc=True).dt.tz_convert('Asia/Kolkata')
            max_date = df_temp['created_at_ist'].dt.date.max()
            args.end = str(max_date)
            args.start = str(max_date - pd.Timedelta(days=6))
        elif choice == '2':
            print()
            args.start = input("  Enter start date (YYYY-MM-DD): ").strip()
            args.end = input("  Enter end date (YYYY-MM-DD): ").strip()
        elif choice == '3':
            sys.exit(0)
        else:
            sys.exit("  Invalid choice.")

        print()
        args.header_already_printed = False
        print("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
        print("  AI Manager Commentary")
        print("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€\n")

        opt_in = input("  Enable AI insight? (y/n): ").strip().lower()
        if opt_in == 'y':
            if not os.environ.get("GEMINI_API_KEY"):
                print("  Gemini API key not configured.\n")
                print("  Enter a Gemini API key to enable live AI insight,")
                print("  or press Enter to continue without AI.\n")
                api_key = getpass_asterisk("  API key: ")
                print("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€\n")
                args.header_already_printed = True

                if api_key.strip():
                    args.api_key = api_key.strip()
                    args.use_ai = True
                else:
                    args.api_key = None
                    args.use_ai = False
            else:
                args.api_key = None
                args.use_ai = True
                print("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€\n")
                args.header_already_printed = True
        else:
            args.api_key = None
            args.use_ai = False
            print("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€\n")
            args.header_already_printed = True

    else:
        if not args.start or not args.end:
            parser.error("--start and --end are required unless using --interactive")
        args.use_ai = False
        args.api_key = None
        args.header_already_printed = False

    run_report(
        args.start, args.end, args.out,
        input_csv=args.input, agents_csv=args.agents,
        use_ai=args.use_ai, api_key=args.api_key,
        is_interactive=is_interactive, header_already_printed=args.header_already_printed
    )
