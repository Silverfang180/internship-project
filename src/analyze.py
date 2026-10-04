import pandas as pd
import numpy as np

def check_hypothesis(name, actual_val, actual_num, actual_denom, expected_val, expected_num=None, expected_denom=None, is_rate=True):
    pass_flag = True
    reason = []
    
    if is_rate:
        if abs(actual_val - expected_val) > 1.0:
            pass_flag = False
            reason.append(f"Rate {actual_val:.1f}% != {expected_val:.1f}%")
        if expected_num is not None:
            if abs(actual_num - expected_num) > max(1, expected_num * 0.02):
                pass_flag = False
                reason.append(f"Num {actual_num} != {expected_num}")
        if expected_denom is not None:
            if abs(actual_denom - expected_denom) > max(1, expected_denom * 0.02):
                pass_flag = False
                reason.append(f"Denom {actual_denom} != {expected_denom}")
    else:
        if abs(actual_val - expected_val) > max(1, expected_val * 0.02):
            pass_flag = False
            reason.append(f"Count {actual_val} != {expected_val}")
            
    res_str = "PASS" if pass_flag else f"FAIL ({', '.join(reason)})"
    
    if is_rate:
        print(f"{name}: {actual_val:.1f}% ({actual_num}/{actual_denom}) -> {res_str}")
    else:
        print(f"{name}: {actual_val} -> {res_str}")

def run_analysis():
    df = pd.read_csv('output/clean_tickets.csv')
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['created_date'] = df['created_at'].dt.date
    df['created_month'] = df['created_at'].dt.to_period('M')
    
    agents = pd.read_csv('data/agents.csv')
    agents['from_date'] = pd.to_datetime(agents['from_date']).dt.date
    agents['to_date'] = pd.to_datetime(agents['to_date']).dt.date
    agents['to_date'] = agents['to_date'].fillna(pd.to_datetime('2099-12-31').date())

    print("=== Section A: Hypotheses ===")
    
    # overall breach rate
    total = len(df)
    breaches = df['breach'].sum()
    rate = breaches / total * 100 if total > 0 else 0
    check_hypothesis("Overall breach rate", rate, breaches, total, 21.8, 2440, 11200)
    
    # breach rate by channel
    for ch, exp in [('chat', 27.6), ('social', 22.0), ('email', 20.4), ('voice', 5.6)]:
        mask = df['channel'] == ch
        d_ch = df[mask]
        tot = len(d_ch)
        br = d_ch['breach'].sum()
        r = br / tot * 100 if tot > 0 else 0
        check_hypothesis(f"Breach rate {ch}", r, br, tot, exp)
        
    # before and after 1 Jul 2025
    d_before = df[df['created_at'] < '2025-07-01']
    d_after = df[df['created_at'] >= '2025-07-01']
    for name, d_sub, exp in [("Before 1 Jul", d_before, 9.4), ("After 1 Jul", d_after, 24.9)]:
        tot = len(d_sub)
        br = d_sub['breach'].sum()
        r = br / tot * 100 if tot > 0 else 0
        check_hypothesis(f"Breach rate {name}", r, br, tot, exp)
        
    # shift
    for sh, exp in [('Morning', 9.7), ('Day', 8.9), ('Night', 65.6)]:
        d_sub = df[df['created_shift_ist'] == sh]
        tot = len(d_sub)
        br = d_sub['breach'].sum()
        r = br / tot * 100 if tot > 0 else 0
        check_hypothesis(f"Breach rate {sh}", r, br, tot, exp)
        
    # Night-created after 30 Jun
    d_sub = df[(df['created_shift_ist'] == 'Night') & (df['created_at'] > '2025-06-30 23:59:59')]
    tot = len(d_sub)
    br = d_sub['breach'].sum()
    r = br / tot * 100 if tot > 0 else 0
    check_hypothesis("Night-created after 30 Jun", r, br, tot, 79)
    
    # Night-created chat after 30 Jun
    d_sub = df[(df['created_shift_ist'] == 'Night') & (df['created_at'] > '2025-06-30 23:59:59') & (df['channel'] == 'chat')]
    tot = len(d_sub)
    br = d_sub['breach'].sum()
    r = br / tot * 100 if tot > 0 else 0
    check_hypothesis("Night-created chat after 30 Jun", r, br, tot, 100)
    
    # staffed Night agents on 1 Jun vs 15 Jul
    d1 = pd.to_datetime('2025-06-01').date()
    d2 = pd.to_datetime('2025-07-15').date()
    a1 = len(agents[(agents['shift'] == 'Night') & (agents['from_date'] <= d1) & (agents['to_date'] >= d1)])
    a2 = len(agents[(agents['shift'] == 'Night') & (agents['from_date'] <= d2) & (agents['to_date'] >= d2)])
    check_hypothesis("Night agents 1 Jun", a1, a1, 1, 5, is_rate=False)
    check_hypothesis("Night agents 15 Jul", a2, a2, 1, 0, is_rate=False)
    
    # among Night-created breaches, resolved by Morning agents
    n_br = df[(df['created_shift_ist'] == 'Night') & df['breach']]
    tot = len(n_br)
    m_res = len(n_br[n_br['resolver_shift'] == 'Morning'])
    check_hypothesis("Night-created breaches resolved by Morning", m_res / tot * 100 if tot > 0 else 0, m_res, tot, (1566/1631*100), 1566, 1631)
    
    # transfer vs non-transfer breach rate
    d_t = df[df['transfers'] > 0]
    d_nt = df[df['transfers'] == 0]
    r_t = d_t['breach'].sum() / len(d_t) * 100
    check_hypothesis("Transfer breach rate", r_t, d_t['breach'].sum(), len(d_t), 21)
    r_nt = d_nt['breach'].sum() / len(d_nt) * 100
    check_hypothesis("Non-transfer breach rate", r_nt, d_nt['breach'].sum(), len(d_nt), 22)
    
    print("\n=== Section B: New analyses ===")
    # 1. Breach rate by IST hour of creation and channel
    df['hour'] = df['created_at'].dt.hour
    b1 = df.groupby(['hour', 'channel'])['breach'].agg(['sum', 'count']).reset_index()
    b1['rate'] = b1['sum'] / b1['count'] * 100
    print("1. Breach rate by hour and channel:")
    print(b1.pivot(index='hour', columns='channel', values='rate').round(1).fillna('-'))
    
    # 2. Monthly table
    print("\n2. Monthly table:")
    monthly = df.groupby('created_month').agg(
        volume=('ticket_id', 'count'),
        breaches=('breach', 'sum'),
        credits=('credit_inr', 'sum'),
        csat=('csat_score', 'mean')
    ).reset_index()
    monthly['breach_rate'] = monthly['breaches'] / monthly['volume'] * 100
    print(monthly.to_string(index=False))
    
    # 3. Staffed agents per month and missing agents
    print("\n3. Staffed agents per month:")
    months = pd.date_range(start='2025-01-01', end='2026-06-01', freq='MS').date
    staff_data = []
    for m in months:
        mid_month = pd.to_datetime(m) + pd.Timedelta(days=14)
        mid_month = mid_month.date()
        c = len(agents[(agents['from_date'] <= mid_month) & (agents['to_date'] >= mid_month)])
        staff_data.append({'month': m.strftime('%Y-%m'), 'total_agents': c})
    print(pd.DataFrame(staff_data).to_string(index=False))
    
    print("\nCount of agents with no roster row after 29 Jun 2025 by team and site:")
    agents_max_to = agents.groupby(['agent_id', 'team', 'site'])['to_date'].max().reset_index()
    missing_agents = agents_max_to[agents_max_to['to_date'] <= pd.to_datetime('2025-06-29').date()]
    print(missing_agents.groupby(['team', 'site']).size().reset_index(name='count').to_string(index=False))
    
    # 4. Capacity check
    print("\n4. Capacity check (Morning+Day monthly volume & breach rate):")
    d_md = df[df['created_shift_ist'].isin(['Morning', 'Day'])].copy()
    md_monthly = d_md.groupby('created_month').agg(
        volume=('ticket_id', 'count'),
        breaches=('breach', 'sum')
    ).reset_index()
    md_monthly['breach_rate'] = md_monthly['breaches'] / md_monthly['volume'] * 100
    corr = md_monthly['volume'].corr(md_monthly['breach_rate'])
    print(md_monthly.to_string(index=False))
    print(f"\nCorrelation between volume and breach rate: {corr:.3f}")
    print("Note: The data export has about 177 tickets a week while the brief says about 650, so workload per agent cannot be inferred.")
    
    # 5. Night need
    print("\n5. Night need after 30 Jun:")
    before_days = 181
    after_days = 365
    print(f"Days before 1 Jul: {before_days}, Days after 1 Jul: {after_days}")
    d_night_after = df[(df['created_shift_ist'] == 'Night') & (df['created_at'] >= '2025-07-01')]
    ch_counts = d_night_after['channel'].value_counts() / after_days
    print(ch_counts.round(1))
    total_night_after = len(d_night_after)
    per_night = total_night_after / after_days
    print(f"Total night tickets per night: {per_night:.1f}")
    assert abs(per_night * after_days - total_night_after) < 1, "Assertion failed: per_night * days != total"
    
    # 6. Alternative explanations & Additions for July 2025 jump
    print("\n6. Alternative explanations for July 2025 jump:")
    vol_jun = len(df[df['created_month'] == '2025-06'])
    vol_jul = len(df[df['created_month'] == '2025-07'])
    print(f"Volume growth: Jun={vol_jun}, Jul={vol_jul} ({(vol_jul/vol_jun-1)*100:.1f}% increase)")
    
    print("\nPulse 2 analysis:")
    df_raw = pd.read_csv('data/tickets.csv')
    df_raw['created_at_dt'] = pd.to_datetime(df_raw['created_at'], format='%Y-%m-%d %H:%M', errors='coerce')
    vol_before = len(df_raw[df_raw['created_at_dt'] < '2025-07-01'])
    vol_after = len(df_raw[df_raw['created_at_dt'] >= '2025-07-01'])
    pl2_before = len(df_raw[(df_raw['product_sku'] == 'VA-EB-PL2') & (df_raw['created_at_dt'] < '2025-07-01')])
    pl2_after = len(df_raw[(df_raw['product_sku'] == 'VA-EB-PL2') & (df_raw['created_at_dt'] >= '2025-07-01')])
    share_before = (pl2_before / vol_before * 100) if vol_before > 0 else 0
    share_after = (pl2_after / vol_after * 100) if vol_after > 0 else 0
    print(f"Pulse 2 share before 1 Jul: {share_before:.1f}%, after 1 Jul: {share_after:.1f}%")
    
    df_merged = df.merge(df_raw[['ticket_id', 'product_sku']], on='ticket_id', how='left')
    d_night_chat_after = df_merged[(df_merged['created_shift_ist'] == 'Night') & 
                                   (df_merged['created_at'] >= '2025-07-01') & 
                                   (df_merged['channel'] == 'chat')]
    pl2_subset = d_night_chat_after[d_night_chat_after['product_sku'] == 'VA-EB-PL2']
    other_subset = d_night_chat_after[d_night_chat_after['product_sku'] != 'VA-EB-PL2']
    pl2_br = pl2_subset['breach'].mean() * 100 if len(pl2_subset) > 0 else 0
    other_br = other_subset['breach'].mean() * 100 if len(other_subset) > 0 else 0
    print(f"Night-chat breach rate after 30 Jun for Pulse 2: {pl2_br:.1f}%, Other SKUs: {other_br:.1f}%")
    
    print("\nIST hour distribution of first_response_at for Night-created tickets after 30 Jun:")
    resp_hour = pd.to_datetime(d_night_after['first_response_at']).dt.hour
    print(resp_hour.value_counts().sort_index())
    night_chat = d_night_after[d_night_after['channel'] == 'chat'].copy()
    print(f"Median wait for Night chat: {night_chat['response_minutes'].median():.1f} mins")
    print(f"90th percentile wait for Night chat: {night_chat['response_minutes'].quantile(0.9):.1f} mins")
    
    print("\nBusiness scenario:")
    count_nb = len(d_night_after[d_night_after['breach']])
    cost_total = count_nb * 350
    print(f"Assumption: Night-created breaches cost Rs 350 each.")
    print(f"Current cost: Rs {cost_total:.0f}/year, Rs {cost_total/4:.0f}/quarter")
    
    new_nb = len(d_night_after) * 0.10
    savings_per_quarter = (cost_total - (new_nb * 350)) / 4
    df_after = df[df['created_at'] >= '2025-07-01']
    other_breaches = df_after['breach'].sum() - count_nb
    new_overall_br = (other_breaches + new_nb) / len(df_after) * 100
    print(f"Assumption: Night-created breach rate falls to 10%.")
    print(f"Resulting overall breach rate after 30 Jun: {new_overall_br:.1f}%")
    print(f"Rupee saving per quarter: Rs {savings_per_quarter:.0f}")

    print("\n=== Phase 2 Re-gate Analyses ===")
    
    # 2a. Night-created breaches after 30 Jun by channel
    print("\n2a. Night-created breaches after 30 Jun by channel:")
    night_breaches = d_night_after[d_night_after['breach']]
    nb_ch = night_breaches['channel'].value_counts()
    nb_ch_share = (nb_ch / len(night_breaches) * 100).round(1)
    for ch in nb_ch.index:
        print(f"{ch}: {nb_ch[ch]} counts ({nb_ch_share[ch]}%)")
        
    # 2b. Night-created email breach rate 22-23 vs 0-5
    print("\n2b. Night-created email breach rate (22-23 vs 0-5):")
    email_night = d_night_after[d_night_after['channel'] == 'email']
    e_22_23 = email_night[email_night['created_at'].dt.hour.isin([22, 23])]
    e_0_5 = email_night[email_night['created_at'].dt.hour.isin([0, 1, 2, 3, 4, 5])]
    br_22_23 = e_22_23['breach'].mean() * 100 if len(e_22_23) > 0 else 0
    br_0_5 = e_0_5['breach'].mean() * 100 if len(e_0_5) > 0 else 0
    print(f"Hours 22-23: {br_22_23:.1f}%")
    print(f"Hours 0-5: {br_0_5:.1f}%")
    
    # 2c. Credits per month before vs after 1 Jul and share of post-July breaches
    print("\n2c. Credits per month and Night share:")
    df_before = df[df['created_at'] < '2025-07-01']
    cred_before = df_before['credit_inr'].sum() / 6
    cred_after = df_after['credit_inr'].sum() / 12
    print(f"Average credits per month Before 1 Jul: Rs {cred_before:.0f}")
    print(f"Average credits per month After 1 Jul: Rs {cred_after:.0f}")
    
    breaches_after = df_after['breach'].sum()
    nb_share = (len(night_breaches) / breaches_after * 100) if breaches_after > 0 else 0
    print(f"Share of post-July breaches that were Night-created: {nb_share:.1f}%")
    
    # 2d. Average CSAT before vs after 1 Jul
    print("\n2d. Average CSAT (excl. blanks) before/after 1 Jul:")
    csat_before = df_before['csat_score'].dropna().mean()
    csat_after = df_after['csat_score'].dropna().mean()
    print(f"Before 1 Jul: {csat_before:.2f}")
    print(f"After 1 Jul: {csat_after:.2f}")
    
    # 2e. Missing agents
    print("\n2e. Missing agents details:")
    for index, row in missing_agents.iterrows():
        print(f"Agent {row['agent_id']} ({row['team']}, {row['site']}) - last date {row['to_date']}")
    print(f"Staffing fell by {len(missing_agents)}.")
    
    # 2f. Morning+Day breach rate before vs after 1 Jul
    print("\n2f. Morning+Day breach rate before vs after 1 Jul:")
    md_before = d_md[d_md['created_at'] < '2025-07-01']
    md_after = d_md[d_md['created_at'] >= '2025-07-01']
    md_br_before = md_before['breach'].sum() / len(md_before) * 100 if len(md_before) > 0 else 0
    md_br_after = md_after['breach'].sum() / len(md_after) * 100 if len(md_after) > 0 else 0
    print(f"Before 1 Jul: {md_br_before:.1f}% ({md_before['breach'].sum()}/{len(md_before)})")
    print(f"After 1 Jul: {md_br_after:.1f}% ({md_after['breach'].sum()}/{len(md_after)})")
    
    # 3. Business case
    print("\n3. Business case with arithmetic:")
    agent_cost_per_night = 8 * 165
    print(f"Agent-shift cost: 8 x Rs 165 = Rs {agent_cost_per_night} per night.")
    
    actual_night_br = len(night_breaches) / len(d_night_after)
    breaches_avoided_per_night = per_night * (actual_night_br - 0.10)
    credits_avoided_per_night = breaches_avoided_per_night * 350
    print(f"Credits avoided per night under the 10% scenario at export volume: Rs {credits_avoided_per_night:.1f}")
    
    scaled_credits_avoided = credits_avoided_per_night * (650 / 177)
    print(f"Assumption: Scaled to 650 tickets/week, credits avoided per night: Rs {scaled_credits_avoided:.1f}")
    
    # Break-even weekly volume
    # Credits avoided per night = (Weekly_Vol / 7) * night_share * (actual_br - 0.1) * 350
    # Want Credits avoided = 1320
    night_share = len(d_night_after) / len(df_after)
    breakeven_vol = (agent_cost_per_night * 7) / (night_share * (actual_night_br - 0.10) * 350)
    print(f"Break-even weekly ticket volume: {breakeven_vol:.1f} tickets/week")
    print("If headcount is frozen, the cost is a re-roster from Day, not a hire.")

if __name__ == '__main__':
    run_analysis()
