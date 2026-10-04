import pytest
import pandas as pd
from src.report import run_report
import os
import re

def test_weekly_bucketing(tmp_path):
    # Sunday 2026-06-21 23:59 IST vs Monday 2026-06-22 00:00 IST
    # Pandas W-MON starts on Monday, ends on Sunday. Wait, W-MON means the week ENDS on Monday, or STARTS on Monday?
    # W-SUN ends on Sunday (week starts Monday).
    # Wait, pandas `dt.to_period('W-MON').dt.start_time` for W-MON actually means week ending on Monday! So week starts on Tuesday!
    # Let me check pandas documentation. If we want week to start on Monday, we use W-SUN. W-SUN means week ending on Sunday, starting on Monday.
    # I should change report.py back to W-SUN if it was starting on Monday. Let's fix that.
    
    out_file = tmp_path / "report.md"
    
    df_tickets = pd.DataFrame({
        'ticket_id': ['T1', 'T2'],
        'created_at': ['2026-06-21 23:59:00+05:30', '2026-06-22 00:00:00+05:30'],
        'created_shift_ist': ['Night', 'Night'],
        'channel': ['chat', 'chat'],
        'breach': [True, False],
        'resolver_tier': ['Tier 1', 'Tier 1'],
        'resolver_shift': ['Morning', 'Morning'],
        'assigned_team': ['Chat Frontline', 'Chat Frontline']
    })
    
    df_agents = pd.DataFrame({
        'agent_id': ['A1'],
        'team': ['Chat Frontline'],
        'shift': ['Night'],
        'from_date': ['2026-01-01'],
        'to_date': ['2026-12-31']
    })
    
    # Generate report for 2026-06-21 to 2026-06-22
    run_report('2026-06-21', '2026-06-22', str(out_file), df_tickets, df_agents)
    
    content = out_file.read_text(encoding='utf-8')
    # Sunday 2026-06-21 week starts on Monday 2026-06-15
    # Monday 2026-06-22 week starts on Monday 2026-06-22
    assert "2026-06-15" in content, "Sunday ticket should fall into week starting 2026-06-15"
    assert "2026-06-22" in content, "Monday ticket should fall into week starting 2026-06-22"

def test_coverage_gap(tmp_path):
    out_file = tmp_path / "report_gap.md"
    
    df_tickets = pd.DataFrame({
        'ticket_id': ['T1'],
        'created_at': ['2026-06-22 10:00:00+05:30'],
        'created_shift_ist': ['Morning'],
        'channel': ['chat'],
        'breach': [True],
        'resolver_tier': ['Tier 1'],
        'resolver_shift': ['Morning'],
        'assigned_team': ['Chat Frontline']
    })
    
    # Missing Chat Frontline Morning agent
    df_agents = pd.DataFrame({
        'agent_id': ['A1', 'A2'],
        'team': ['Chat Frontline', 'Email Frontline'],
        'shift': ['Day', 'Morning'],
        'from_date': ['2026-01-01', '2026-01-01'],
        'to_date': ['2026-12-31', '2026-12-31']
    })
    
    run_report('2026-06-22', '2026-06-22', str(out_file), df_tickets, df_agents)
    
    content = out_file.read_text(encoding='utf-8')
    assert "| Chat Frontline | Morning | 1 | 1 | 1 | 100.0% |" in content

def test_inherited_breach(tmp_path):
    out_file = tmp_path / "report_inherited.md"
    
    df_tickets = pd.DataFrame({
        'ticket_id': ['T1', 'T2'],
        'created_at': ['2026-06-22 01:00:00+05:30', '2026-06-22 10:00:00+05:30'],
        'created_shift_ist': ['Night', 'Morning'],
        'channel': ['chat', 'chat'],
        'breach': [True, True],
        'resolver_tier': ['Tier 1', 'Tier 1'],
        'resolver_shift': ['Morning', 'Morning'],
        'assigned_team': ['Chat Frontline', 'Chat Frontline']
    })
    
    df_agents = pd.DataFrame({
        'agent_id': ['A1'],
        'team': ['Chat Frontline'],
        'shift': ['Morning'],
        'from_date': ['2026-01-01'],
        'to_date': ['2026-12-31']
    })
    
    run_report('2026-06-22', '2026-06-22', str(out_file), df_tickets, df_agents)
    
    content = out_file.read_text(encoding='utf-8')
    # Tickets = 2, Breaches = 2, NightTickets = 1, Inherited = 1
    # ExclNightRate = (2 - 1) / (2 - 1) * 100 = 100.0%
    assert "| Morning | Chat Frontline | 2 | 2 | 100.0% | 1 | 100.0% |" in content
    
def test_reconciliation_check(tmp_path):
    out_file = tmp_path / "report_recon.md"
    
    # Read the actual files for this test
    if not os.path.exists('output/clean_tickets.csv'):
        pytest.skip("Run src.clean first")
        
    run_report('2025-01-01', '2026-06-30', str(out_file))
    
    content = out_file.read_text(encoding='utf-8')
    
    # The headline should show 21.8% breach rate (2440/11200 tickets)
    assert "2440/11200 tickets" in content, "Reconciliation check failed!"
