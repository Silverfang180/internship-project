import pandas as pd
import numpy as np
import os
from src.config import TARGETS_MINUTES, CREDIT_PER_BREACH_INR, SHIFTS

def get_shift(dt):
    if pd.isna(dt):
        return None
    hour = dt.hour
    if 6 <= hour < 14:
        return 'Morning'
    elif 14 <= hour < 22:
        return 'Day'
    else:
        return 'Night'

def is_failed_ivr(row):
    msg = row['customer_message']
    if pd.isna(msg):
        return False
        
    msg_str = str(msg)
    if "[inaudible]" in msg_str or "[line dropped]" in msg_str:
        return True
        
    if row['channel'] == 'voice':
        if msg_str.startswith("[IVR transcript]"):
            msg_str = msg_str[len("[IVR transcript]"):].strip()
        else:
            msg_str = msg_str.strip()
            
        import string
        if len(msg_str) > 0 and all(c in string.punctuation or c.isspace() for c in msg_str):
            return True
            
    return False

def clean_data(data_dir, output_dir):
    tickets_path = os.path.join(data_dir, 'tickets.csv')
    agents_path = os.path.join(data_dir, 'agents.csv')
    
    df_tickets = pd.read_csv(tickets_path)
    df_agents = pd.read_csv(agents_path)
    
    rows_in = len(df_tickets)
    
    df_tickets['is_helpdesk'] = df_tickets['source_system'] == 'helpdesk'
    df_tickets = df_tickets.sort_values(by=['ticket_id', 'is_helpdesk'], ascending=[True, False])
    df_tickets = df_tickets.drop_duplicates(subset='ticket_id', keep='first')
    df_tickets = df_tickets.drop(columns=['is_helpdesk'])
    
    dups_removed = rows_in - len(df_tickets)
    
    for col in ['created_at', 'first_response_at', 'resolved_at']:
        parsed = pd.to_datetime(df_tickets[col], format="%Y-%m-%d %H:%M", errors='coerce')
        invalid_mask = df_tickets[col].notna() & (df_tickets[col] != '') & parsed.isna()
        if invalid_mask.any():
            offending = df_tickets.loc[invalid_mask, 'ticket_id'].head(5).tolist()
            raise ValueError(f"Date parsing failed for {col}. Expected format YYYY-MM-DD HH:MM. Offending tickets: {offending}")
        df_tickets[col] = parsed.dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
        
    df_tickets['csat_score'] = pd.to_numeric(df_tickets['csat_score'], errors='coerce')
    legacy_zero_mask = (df_tickets['source_system'] == 'legacy_fd') & (df_tickets['csat_score'] == 0)
    csat_zeros_converted = legacy_zero_mask.sum()
    df_tickets.loc[legacy_zero_mask, 'csat_score'] = np.nan
    
    df_tickets['ivr_failed'] = df_tickets.apply(is_failed_ivr, axis=1)
    ivr_flagged = df_tickets['ivr_failed'].sum()
    
    channel_counts = df_tickets[df_tickets['ivr_failed']]['channel'].value_counts()
    
    df_tickets['created_shift_ist'] = df_tickets['created_at'].apply(get_shift)
    df_tickets['created_date'] = df_tickets['created_at'].dt.date
    
    df_agents['from_date'] = pd.to_datetime(df_agents['from_date']).dt.date
    df_agents['to_date'] = pd.to_datetime(df_agents['to_date']).dt.date
    df_agents['to_date'] = df_agents['to_date'].fillna(pd.to_datetime('2099-12-31').date())
    
    merged = df_tickets.merge(df_agents, on='agent_id', how='left')
    valid_roster = merged[
        (merged['created_date'] >= merged['from_date']) & 
        (merged['created_date'] <= merged['to_date'])
    ]
    
    roster_matches = len(valid_roster)
    unmatched = len(df_tickets) - roster_matches
    
    valid_roster = valid_roster[['ticket_id', 'shift', 'tier']]
    valid_roster = valid_roster.rename(columns={'shift': 'resolver_shift', 'tier': 'resolver_tier'})
    
    df_tickets = df_tickets.merge(valid_roster, on='ticket_id', how='left')
    
    df_tickets['response_minutes'] = (df_tickets['first_response_at'] - df_tickets['created_at']).dt.total_seconds() / 60
    df_tickets['target_minutes'] = df_tickets['channel'].map(TARGETS_MINUTES)
    df_tickets['breach'] = df_tickets['response_minutes'] > df_tickets['target_minutes']
    df_tickets['credit_inr'] = df_tickets['breach'].apply(lambda x: CREDIT_PER_BREACH_INR if x else 0)
    
    out_cols = ['ticket_id', 'created_at', 'first_response_at', 'resolved_at', 'status', 'channel', 
                'category', 'priority', 'assigned_team', 'transfers', 'csat_score', 'source_system', 
                'agent_id', 'resolver_shift', 'resolver_tier', 'created_shift_ist', 'target_minutes', 
                'response_minutes', 'breach', 'credit_inr', 'ivr_failed']
    df_out = df_tickets[out_cols]
    
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'clean_tickets.csv')
    df_out.to_csv(out_path, index=False)
    
    print(f"Rows in: {rows_in}")
    print(f"Duplicates removed: {dups_removed}")
    print(f"CSAT zeros converted: {csat_zeros_converted}")
    print(f"IVR total flagged: {ivr_flagged}")
    print("IVR flagged by channel:")
    for ch, count in channel_counts.items():
        print(f"  {ch}: {count}")
    print(f"Roster matches: {roster_matches}")
    print(f"Unmatched: {unmatched}")
    print(f"Output columns: {list(df_out.columns)}")

if __name__ == "__main__":
    clean_data('data', 'output')
