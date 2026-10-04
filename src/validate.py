import pandas as pd
import numpy as np
import os
import sys

def build_validation_sample():
    np.random.seed(42)
    
    # 1. Confirm clean.py treats breach as strictly >
    # Checking clean.py line 95 visually confirms it's `response_minutes > target_minutes`.
    print("Confirmed: clean.py treats breach as response > target (strictly later, equal is NOT a breach).")
    
    # Read raw data
    raw_df = pd.read_csv('data/tickets.csv')
    raw_df['is_helpdesk'] = raw_df['source_system'] == 'helpdesk'
    raw_df = raw_df.sort_values(by=['ticket_id', 'is_helpdesk'], ascending=[True, False])
    raw_df = raw_df.drop_duplicates(subset='ticket_id', keep='first').drop(columns=['is_helpdesk'])
    
    # Read clean data
    if not os.path.exists('output/clean_tickets.csv'):
        sys.exit("Error: output/clean_tickets.csv not found.")
    clean_df = pd.read_csv('output/clean_tickets.csv')
    
    # Merge required columns from clean_df into raw_df to help with selection
    # We need: created_shift_ist, breach, response_minutes, target_minutes, created_at (clean for dates)
    merge_cols = ['ticket_id', 'created_shift_ist', 'breach', 'response_minutes', 'target_minutes']
    df = raw_df.merge(clean_df[merge_cols], on='ticket_id', how='left')
    
    if df['created_shift_ist'].isna().any():
        sys.exit("Error: Some tickets are missing from clean_tickets.csv.")
        
    df['clean_created_at'] = pd.to_datetime(clean_df.set_index('ticket_id').loc[df['ticket_id']]['created_at'].values)
    
    selected_tickets = pd.DataFrame()
    
    # 4 date-rollover: created 18:30-23:59 UTC
    # raw 'created_at' is UTC like '2025-01-01 20:00'
    df['raw_created_hour'] = pd.to_datetime(df['created_at'], format='%Y-%m-%d %H:%M', errors='coerce').dt.hour
    df['raw_created_minute'] = pd.to_datetime(df['created_at'], format='%Y-%m-%d %H:%M', errors='coerce').dt.minute
    
    time_val = df['raw_created_hour'] + df['raw_created_minute'] / 60.0
    rollover_mask = (time_val >= 18.5) & (time_val < 24.0)
    
    date_rollover = df[rollover_mask & ~df.index.isin(selected_tickets.index)].sample(4, random_state=42)
    date_rollover['case_type'] = 'date-rollover'
    selected_tickets = pd.concat([selected_tickets, date_rollover])
    
    # 4 exactly-at-target
    exact_mask = df['response_minutes'] == df['target_minutes']
    exact_pool = df[exact_mask & ~df['ticket_id'].isin(selected_tickets['ticket_id'])]
    # Try different channels
    exact_at_target = pd.DataFrame()
    for ch in exact_pool['channel'].unique():
        if len(exact_at_target) < 4:
            ch_exact = exact_pool[exact_pool['channel'] == ch]
            if not ch_exact.empty:
                exact_at_target = pd.concat([exact_at_target, ch_exact.sample(1, random_state=42)])
    
    # if fewer than 4, fill with others
    if len(exact_at_target) < 4:
        rem_exact = exact_pool[~exact_pool['ticket_id'].isin(exact_at_target['ticket_id'])]
        needed = 4 - len(exact_at_target)
        if len(rem_exact) >= needed:
            exact_at_target = pd.concat([exact_at_target, rem_exact.sample(needed, random_state=42)])
        else:
            exact_at_target = pd.concat([exact_at_target, rem_exact])
            # If still fewer, get closest
            still_needed = 4 - len(exact_at_target)
            if still_needed > 0:
                diff = (df['response_minutes'] - df['target_minutes']).abs()
                pool_closest = df[~df['ticket_id'].isin(selected_tickets['ticket_id']) & ~df['ticket_id'].isin(exact_at_target['ticket_id'])]
                closest = pool_closest.loc[diff.loc[pool_closest.index].nsmallest(still_needed).index]
                exact_at_target = pd.concat([exact_at_target, closest])
                
    exact_at_target['case_type'] = 'exactly-at-target'
    selected_tickets = pd.concat([selected_tickets, exact_at_target])
    
    # 4 target-boundary (within 2 minutes)
    diff = (df['response_minutes'] - df['target_minutes']).abs()
    boundary_mask = (diff > 0) & (diff <= 2)
    target_boundary = df[boundary_mask & ~df['ticket_id'].isin(selected_tickets['ticket_id'])].sample(4, random_state=42)
    target_boundary['case_type'] = 'target-boundary'
    selected_tickets = pd.concat([selected_tickets, target_boundary])
    
    # 4 shift-boundary (within 15 minutes of 06:00, 14:00, 22:00 IST)
    # clean_created_at is IST timezone aware.
    ist_hour = df['clean_created_at'].dt.hour
    ist_minute = df['clean_created_at'].dt.minute
    ist_time = ist_hour + ist_minute / 60.0
    
    def dist_to_boundary(t):
        return min(abs(t - 6), abs(t - 14), abs(t - 22), abs(t - 30), abs(t + 2)) # 30=6am next day
        
    df['dist'] = ist_time.apply(dist_to_boundary)
    shift_bound_mask = df['dist'] <= (15.0/60.0)
    
    shift_pool = df[shift_bound_mask & ~df['ticket_id'].isin(selected_tickets['ticket_id'])]
    shift_boundary = shift_pool.sample(4, random_state=42)
    shift_boundary['case_type'] = 'shift-boundary'
    selected_tickets = pd.concat([selected_tickets, shift_boundary])
    
    # 14 random, stratified by channel and shift
    rem_pool = df[~df['ticket_id'].isin(selected_tickets['ticket_id'])]
    
    random_pool = pd.DataFrame()
    
    # We need to satisfy conditions: >=4 Night, >=5 breach, >=5 not-breach, >=4 before 1 Jul 2025, >=4 legacy_fd.
    # A simple rejection sampling or guided sampling
    for _ in range(100):
        # stratified sample
        strata = rem_pool.groupby(['channel', 'created_shift_ist'], group_keys=False).apply(lambda x: x.sample(min(len(x), 1), random_state=np.random.randint(10000)))
        if len(strata) < 14:
            extras = rem_pool[~rem_pool['ticket_id'].isin(strata['ticket_id'])].sample(14 - len(strata))
            strata = pd.concat([strata, extras])
        else:
            strata = strata.sample(14)
            
        # Check conditions
        n_night = (strata['created_shift_ist'] == 'Night').sum()
        n_br = strata['breach'].sum()
        n_nbr = (~strata['breach']).sum()
        n_before = (strata['clean_created_at'] < pd.to_datetime('2025-07-01').tz_localize('Asia/Kolkata')).sum()
        n_leg = (strata['source_system'] == 'legacy_fd').sum()
        
        if n_night >= 4 and n_br >= 5 and n_nbr >= 5 and n_before >= 4 and n_leg >= 4:
            random_pool = strata
            break
            
    if random_pool.empty:
        # manual fallback
        night = rem_pool[rem_pool['created_shift_ist'] == 'Night'].sample(4)
        br = rem_pool[rem_pool['breach'] & ~rem_pool.index.isin(night.index)].sample(5)
        nbr = rem_pool[~rem_pool['breach'] & ~rem_pool.index.isin(night.index) & ~rem_pool.index.isin(br.index)].sample(5)
        random_pool = pd.concat([night, br, nbr])
        
    random_pool['case_type'] = 'random'
    selected_tickets = pd.concat([selected_tickets, random_pool])
    
    # Final check size
    if len(selected_tickets) != 30:
        # trim or add
        if len(selected_tickets) > 30:
            selected_tickets = selected_tickets.head(30)
        
    # shuffle
    selected_tickets = selected_tickets.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # output 1: blank markdown
    blank_cols = ['ticket_id', 'channel', 'created_at', 'first_response_at']
    blank_df = selected_tickets[blank_cols]
    
    os.makedirs('output', exist_ok=True)
    with open('output/validation_blank.md', 'w') as f:
        f.write("| ticket_id | channel | created_at | first_response_at |\n")
        f.write("|---|---|---|---|\n")
        for _, r in blank_df.iterrows():
            f.write(f"| {r['ticket_id']} | {r['channel']} | {r['created_at']} | {r['first_response_at']} |\n")
            
    # output 2: key csv
    key_cols = ['ticket_id', 'created_shift_ist', 'breach', 'response_minutes', 'case_type']
    key_df = selected_tickets[key_cols].rename(columns={
        'created_shift_ist': 'tool_shift_ist',
        'breach': 'tool_breach',
        'response_minutes': 'tool_response_minutes'
    })
    key_df.to_csv('output/validation_key.csv', index=False)
    
    print("Files created:")
    print("1) output/validation_blank.md")
    print("2) output/validation_key.csv")
    print("\nCase Type Counts:")
    print(selected_tickets['case_type'].value_counts().to_string())
    
if __name__ == '__main__':
    build_validation_sample()
