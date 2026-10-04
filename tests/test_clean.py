import pytest
import pandas as pd
import numpy as np
import os
from src.clean import clean_data, get_shift, is_failed_ivr

def test_get_shift():
    # Morning: 06:00 to 13:59
    assert get_shift(pd.to_datetime('2025-01-01 05:59:59')) == 'Night'
    assert get_shift(pd.to_datetime('2025-01-01 06:00:00')) == 'Morning'
    assert get_shift(pd.to_datetime('2025-01-01 13:30:00')) == 'Morning'
    assert get_shift(pd.to_datetime('2025-01-01 13:59:59')) == 'Morning'
    
    # Day: 14:00 to 21:59
    assert get_shift(pd.to_datetime('2025-01-01 14:00:00')) == 'Day'
    assert get_shift(pd.to_datetime('2025-01-01 21:30:00')) == 'Day'
    assert get_shift(pd.to_datetime('2025-01-01 21:59:59')) == 'Day'
    
    # Night: 22:00 to 05:59
    assert get_shift(pd.to_datetime('2025-01-01 22:00:00')) == 'Night'
    assert get_shift(pd.to_datetime('2025-01-01 23:59:59')) == 'Night'
    assert get_shift(pd.to_datetime('2025-01-02 00:00:00')) == 'Night'


def test_clean_data_roster_join(tmp_path):
    data_dir = tmp_path / "data"
    out_dir = tmp_path / "output"
    data_dir.mkdir()
    
    # Roster join for agent A3002 on 29 Jun and 30 Jun
    agents_csv = """agent_id,name,site,team,shift,tier,from_date,to_date
A3002,Tarun Mishra,Indore,Chat Frontline,Night,1,2023-02-12,2025-06-29
A3002,Tarun Mishra,Indore,Chat Frontline,Day,1,2025-06-30,
"""
    (data_dir / "agents.csv").write_text(agents_csv)
    
    tickets_csv = """ticket_id,created_at,first_response_at,resolved_at,status,channel,customer_id,order_id,product_sku,category,priority,assigned_team,agent_id,transfers,csat_score,refund_amount_inr,refund_reason_code,replacement_issued,customer_message,agent_notes,source_system
T1,2025-06-29 10:00,2025-06-29 10:05,2025-06-29 11:00,resolved,chat,C1,,SKU1,Other,Normal,Team1,A3002,0,5,,,,,,helpdesk
T2,2025-06-30 10:00,2025-06-30 10:05,2025-06-30 11:00,resolved,chat,C2,,SKU2,Other,Normal,Team1,A3002,0,5,,,,,,helpdesk
"""
    (data_dir / "tickets.csv").write_text(tickets_csv)
    
    clean_data(str(data_dir), str(out_dir))
    df = pd.read_csv(out_dir / "clean_tickets.csv")
    
    t1 = df[df['ticket_id'] == 'T1'].iloc[0]
    assert t1['resolver_shift'] == 'Night'
    
    t2 = df[df['ticket_id'] == 'T2'].iloc[0]
    assert t2['resolver_shift'] == 'Day'


def test_clean_data_duplicate_handling(tmp_path):
    data_dir = tmp_path / "data"
    out_dir = tmp_path / "output"
    data_dir.mkdir()
    
    agents_csv = "agent_id,name,site,team,shift,tier,from_date,to_date\nA1,Zoya,Indore,Chat,Night,1,2021-04-20,2025-06-29\n"
    (data_dir / "agents.csv").write_text(agents_csv)
    
    tickets_csv = """ticket_id,created_at,first_response_at,resolved_at,status,channel,customer_id,order_id,product_sku,category,priority,assigned_team,agent_id,transfers,csat_score,refund_amount_inr,refund_reason_code,replacement_issued,customer_message,agent_notes,source_system
DUP1,2025-06-28 10:00,2025-06-28 10:05,2025-06-28 11:00,resolved,chat,C1,,SKU1,Other,Normal,Team1,A1,0,0,,,,,,legacy_fd
DUP1,2025-06-28 10:00,2025-06-28 10:05,2025-06-28 11:00,resolved,chat,C1,,SKU1,Other,Normal,Team1,A1,0,,,,,,,helpdesk
"""
    (data_dir / "tickets.csv").write_text(tickets_csv)
    
    clean_data(str(data_dir), str(out_dir))
    df = pd.read_csv(out_dir / "clean_tickets.csv")
    
    assert len(df) == 1
    dup = df.iloc[0]
    assert dup['source_system'] == 'helpdesk'
    assert pd.isna(dup['csat_score'])


def test_clean_data_csat_zero(tmp_path):
    data_dir = tmp_path / "data"
    out_dir = tmp_path / "output"
    data_dir.mkdir()
    
    agents_csv = "agent_id,name,site,team,shift,tier,from_date,to_date\nA1,Zoya,Indore,Chat,Night,1,2021-04-20,2025-06-29\n"
    (data_dir / "agents.csv").write_text(agents_csv)
    
    tickets_csv = """ticket_id,created_at,first_response_at,resolved_at,status,channel,customer_id,order_id,product_sku,category,priority,assigned_team,agent_id,transfers,csat_score,refund_amount_inr,refund_reason_code,replacement_issued,customer_message,agent_notes,source_system
T_LEGACY,2025-06-28 10:00,2025-06-28 10:05,2025-06-28 11:00,resolved,chat,C1,,SKU1,Other,Normal,Team1,A1,0,0,,,,,,legacy_fd
T_NEW,2025-06-28 10:00,2025-06-28 10:05,2025-06-28 11:00,resolved,chat,C1,,SKU1,Other,Normal,Team1,A1,0,0,,,,,,helpdesk
"""
    (data_dir / "tickets.csv").write_text(tickets_csv)
    
    clean_data(str(data_dir), str(out_dir))
    df = pd.read_csv(out_dir / "clean_tickets.csv")
    
    t_legacy = df[df['ticket_id'] == 'T_LEGACY'].iloc[0]
    t_new = df[df['ticket_id'] == 'T_NEW'].iloc[0]
    
    assert pd.isna(t_legacy['csat_score'])
    assert t_new['csat_score'] == 0

def test_clean_data_strict_date_parsing(tmp_path):
    data_dir = tmp_path / "data"
    out_dir = tmp_path / "output"
    data_dir.mkdir()
    
    agents_csv = "agent_id,name,site,team,shift,tier,from_date,to_date\nA1,Zoya,Indore,Chat,Night,1,2021-04-20,2025-06-29\n"
    (data_dir / "agents.csv").write_text(agents_csv)
    
    # Using 28/06/2025 10:00 instead of 2025-06-28 10:00
    tickets_csv = """ticket_id,created_at,first_response_at,resolved_at,status,channel,customer_id,order_id,product_sku,category,priority,assigned_team,agent_id,transfers,csat_score,refund_amount_inr,refund_reason_code,replacement_issued,customer_message,agent_notes,source_system
T_BAD_DATE,28/06/2025 10:00,2025-06-28 10:05,2025-06-28 11:00,resolved,chat,C1,,SKU1,Other,Normal,Team1,A1,0,0,,,,,,helpdesk
"""
    (data_dir / "tickets.csv").write_text(tickets_csv)
    
    with pytest.raises(ValueError) as excinfo:
        clean_data(str(data_dir), str(out_dir))
    
    assert "Date parsing failed for created_at" in str(excinfo.value)
    assert "T_BAD_DATE" in str(excinfo.value)
