import argparse
import pandas as pd
import numpy as np
import os
import sys

def escape_md(val):
    if isinstance(val, str) and val.startswith(('=', '+', '-', '@')):
        return "'" + val
    return val

def run_report(start_date, end_date, out_path, df_tickets=None, df_agents=None):
    if df_tickets is None:
        if not os.path.exists('output/clean_tickets.csv'):
            sys.exit("Run python -m src.clean first")
        df = pd.read_csv('output/clean_tickets.csv')
    else:
        df = df_tickets.copy()
        
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['created_at_ist'] = pd.to_datetime(df['created_at'], utc=True).dt.tz_convert('Asia/Kolkata')
    df['created_date'] = df['created_at_ist'].dt.date
    
    start_dt = pd.to_datetime(start_date).date()
    end_dt = pd.to_datetime(end_date).date()
    
    period_days = (end_dt - start_dt).days + 1
    prev_end_dt = start_dt - pd.Timedelta(days=1)
    prev_start_dt = start_dt - pd.Timedelta(days=period_days)
    
    # 1. Headline
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
    
    report_lines = []
    report_lines.append(f"# SLA Report: {start_date} to {end_date}")
    report_lines.append("")
    report_lines.append("## 1. Headline Summary")
    report_lines.append(f"**Current Period:** {curr_rate:.1f}% breach rate ({curr_breaches}/{curr_tickets} tickets), Rs {curr_credits} credits.")
    
    if prev_tickets > 0:
        report_lines.append(f"**Previous Period ({prev_start_dt} to {prev_end_dt}):** {prev_rate:.1f}% breach rate ({prev_breaches}/{prev_tickets} tickets), Rs {prev_credits} credits.")
    else:
        report_lines.append("**Previous Period:** No data available for comparison.")
    
    # 2. Breaches by ticket-creation shift (IST) and channel
    report_lines.append("\n## 2. Breaches by Creation Shift and Channel")
    if curr_tickets > 0:
        agg2 = df_curr.groupby(['created_shift_ist', 'channel']).agg(
            Tickets=('ticket_id', 'count'),
            Breaches=('breach', 'sum')
        ).reset_index()
        agg2['Breach Rate'] = (agg2['Breaches'] / agg2['Tickets'] * 100).round(1).astype(str) + '%'
        
        report_lines.append("| Shift | Channel | Tickets | Breaches | Breach Rate |")
        report_lines.append("|---|---|---|---|---|")
        for _, r in agg2.iterrows():
            shift = escape_md(str(r['created_shift_ist']))
            ch = escape_md(str(r['channel']))
            report_lines.append(f"| {shift} | {ch} | {r['Tickets']} | {r['Breaches']} | {r['Breach Rate']} |")
    else:
        report_lines.append("No tickets in this period.")

    # 3. Coverage-gap flag
    report_lines.append("\n## 3. Coverage Gaps")
    report_lines.append("*Note: Voice callbacks run 08:00-22:00 only, so Night gaps for Voice are expected.*")
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
        agents = pd.read_csv('data/agents.csv')
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
                    'Days with Zero Staff': days_zero_staff,
                    'Tickets Created in Gap': gap_tix_total,
                    'Breaches': gap_br_total,
                    'Breach Rate': f"{br_rate:.1f}%"
                })
                
    if gap_summary:
        report_lines.append("| Team | Shift | Days with Zero Staff | Tickets Created in Gap | Breaches | Breach Rate |")
        report_lines.append("|---|---|---|---|---|---|")
        for g in gap_summary:
            report_lines.append(f"| {escape_md(g['Team'])} | {escape_md(g['Shift'])} | {g['Days with Zero Staff']} | {g['Tickets Created in Gap']} | {g['Breaches']} | {g['Breach Rate']} |")
    else:
        report_lines.append("No coverage gaps found with created tickets.")
        
    # 4. Weekly trend table (Week starts on Monday)
    report_lines.append("\n## 4. Weekly Trend")
    if curr_tickets > 0:
        df_curr = df_curr.copy()
        # dt.to_period('W-SUN') means week ending on Sunday, starting on Monday.
        df_curr['week_start'] = df_curr['created_at_ist'].dt.tz_localize(None).dt.to_period('W-SUN').dt.start_time.dt.date
        agg4 = df_curr.groupby('week_start').agg(
            Tickets=('ticket_id', 'count'),
            Breaches=('breach', 'sum')
        ).reset_index()
        agg4['Breach Rate'] = (agg4['Breaches'] / agg4['Tickets'] * 100).round(1).astype(str) + '%'
        
        report_lines.append("| Week Start (IST) | Tickets | Breaches | Breach Rate |")
        report_lines.append("|---|---|---|---|")
        for _, r in agg4.iterrows():
            ws = escape_md(str(r['week_start']))
            report_lines.append(f"| {ws} | {r['Tickets']} | {r['Breaches']} | {r['Breach Rate']} |")
    else:
        report_lines.append("No tickets in this period.")

    # 5. Resolved by
    report_lines.append("\n## 5. Resolved By (Shift and Team)")
    report_lines.append("*Note: The resolving agent is not necessarily who should have responded first. Tier 2 is excluded from comparisons.*")
    report_lines.append("Breaches counted against a shift include tickets that arrived while no one was on shift.")
    
    if curr_tickets > 0:
        is_tier2 = (df_curr['resolver_tier'] == 'Tier 2') | (df_curr['assigned_team'] == 'Escalations & Warranty')
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
        
        # Calculate rate excluding night created tickets
        excl_night_tickets = agg5['Tickets'] - agg5['NightTickets']
        excl_night_breaches = agg5['Breaches'] - agg5['InheritedBreaches']
        agg5['ExclNightRate'] = np.where(excl_night_tickets > 0, (excl_night_breaches / excl_night_tickets * 100).round(1).astype(str) + '%', 'N/A')
        
        report_lines.append("| Resolver Shift | Assigned Team | Tickets | Breaches | Breach Rate | Breaches on tickets created at Night (inherited) | Breach rate excluding Night-created tickets |")
        report_lines.append("|---|---|---|---|---|---|---|")
        for _, r in agg5.iterrows():
            shift = escape_md(str(r['resolver_shift']))
            team = escape_md(str(r['assigned_team']))
            report_lines.append(f"| {shift} | {team} | {r['Tickets']} | {r['Breaches']} | {r['Breach Rate']} | {r['InheritedBreaches']} | {r['ExclNightRate']} |")
            
        report_lines.append(f"\n*Excluded Tier 2 / Escalations tickets: {tier2_count}*")
            
    # 6. Footer caveats
    report_lines.append("\n## Caveats")
    report_lines.append("- The export has about 177 tickets a week vs about 650 quoted.")
    report_lines.append("- 14 IVR-style transcripts in non-voice channels may have the wrong target.")
    report_lines.append("- 3 agents have no later roster row.")
    
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines) + '\n')
    print(f"Report written to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate weekly SLA report")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD (inclusive)")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD (inclusive)")
    parser.add_argument("--out", required=True, help="Output markdown file path")
    args = parser.parse_args()
    
    run_report(args.start, args.end, args.out)
