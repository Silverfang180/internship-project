import pytest
import os
import pandas as pd
from src.validate import build_validation_sample
from src.score_validation import score_validation
import sys

def test_validation_reproducibility():
    if not os.path.exists('output/clean_tickets.csv'):
        pytest.skip("Run src.clean first")
        
    build_validation_sample()
    df1 = pd.read_csv('output/validation_key.csv')
    
    # Run again
    build_validation_sample()
    df2 = pd.read_csv('output/validation_key.csv')
    
    assert list(df1['ticket_id']) == list(df2['ticket_id']), "Validation sample is not reproducible."
    
def test_validation_blank_columns():
    if not os.path.exists('output/validation_blank.md'):
        pytest.skip("Run src.validate first")
        
    with open('output/validation_blank.md', 'r') as f:
        header = f.readline().strip()
        
    allowed_cols = ['ticket_id', 'channel', 'created_at', 'first_response_at']
    for col in header.split('|'):
        col = col.strip()
        if col:
            assert col in allowed_cols, f"Forbidden column {col} in blank file."
            
def test_validation_counts():
    if not os.path.exists('output/validation_key.csv'):
        pytest.skip("Run src.validate first")
        
    df = pd.read_csv('output/validation_key.csv')
    assert len(df) == 30, f"Sample size is {len(df)}, expected 30."
    
    counts = df['case_type'].value_counts()
    assert counts.get('random', 0) == 14
    assert counts.get('shift-boundary', 0) == 4
    assert counts.get('target-boundary', 0) == 4
    assert counts.get('exactly-at-target', 0) == 4
    assert counts.get('date-rollover', 0) == 4
    
def test_scorer_handles_formatting(tmp_path, monkeypatch, capsys):
    if not os.path.exists('output/validation_key.csv'):
        pytest.skip("Run src.validate first")
        
    # We will simulate output/my_answers.txt
    key_df = pd.read_csv('output/validation_key.csv')
    
    # Create my_answers.txt with BOM, CRLF, lowercase "true", and one mismatch
    lines = []
    for idx, row in key_df.iterrows():
        tid = row['ticket_id']
        t_shift = row['tool_shift_ist']
        t_breach = str(row['tool_breach']).lower()
        
        # introduce one mismatch on the first ticket
        if idx == 0:
            m_shift = 'Morning' if t_shift != 'Morning' else 'Night'
            lines.append(f"{tid},{m_shift},{t_breach}\r\n")
        else:
            lines.append(f"{tid},{t_shift.lower()},{t_breach}\r\n") # test lowercase shift
            
    # Write with BOM
    my_answers_path = 'output/my_answers.txt'
    with open(my_answers_path, 'w', encoding='utf-8-sig') as f:
        f.writelines(lines)
        
    # Run scorer
    score_validation()
    
    captured = capsys.readouterr()
    out = captured.out
    
    # Assert
    assert "Sample size: 30" in out
    assert "Shift mismatch:" in out, "Did not flag the shift mismatch correctly."
    
    # Clean up
    if os.path.exists('docs/validation_results.md'):
        os.remove('docs/validation_results.md')
    if os.path.exists(my_answers_path):
        os.remove(my_answers_path)
