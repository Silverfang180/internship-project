import pytest
import os
import json
import sys
from unittest.mock import patch, MagicMock
from src.ai_insight import generate_insight
from src.report import run_report
import pandas as pd

def test_ai_disabled_no_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert generate_insight({"test": 123}) is None

def test_ai_explicit_key_provided(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with patch('google.genai.Client') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.models.generate_content.return_value = MagicMock(text="{}")
        generate_insight({"test": 123}, api_key="interactive_key")
        mock_client_class.assert_called_once_with(api_key="interactive_key")

def test_aggregate_payload_no_raw_fields(monkeypatch):
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

    df_agents = pd.DataFrame({
        'agent_id': ['A1'],
        'team': ['Chat Frontline'],
        'shift': ['Morning'],
        'from_date': ['2026-01-01'],
        'to_date': ['2026-12-31']
    })

    captured_payload = None
    def mock_generate_insight(metrics_dict, api_key=None):
        nonlocal captured_payload
        captured_payload = metrics_dict
        return None

    with patch('src.ai_insight.generate_insight', mock_generate_insight):
        run_report('2026-06-22', '2026-06-22', None, df_tickets, df_agents, use_ai=True)

    assert captured_payload is not None
    payload_str = json.dumps(captured_payload)
    assert "T1" not in payload_str
    assert "A1" not in payload_str
    assert "ticket_id" not in payload_str

def test_ai_failure_fallback(monkeypatch, tmp_path):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    out_file = tmp_path / "report.md"

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
    df_agents = pd.DataFrame({
        'agent_id': ['A1'],
        'team': ['Chat Frontline'],
        'shift': ['Morning'],
        'from_date': ['2026-01-01'],
        'to_date': ['2026-12-31']
    })

    with patch('google.genai.Client') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.models.generate_content.side_effect = Exception("API Error")

        run_report('2026-06-22', '2026-06-22', str(out_file), df_tickets, df_agents, use_ai=True, api_key="fake_key")

    content = out_file.read_text(encoding='utf-8')
    assert "AI insight unavailable; deterministic report generated successfully." in content
    assert "fake_key" not in content

def test_interactive_no_key_enter_fallback(monkeypatch, capsys):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

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
    df_agents = pd.DataFrame({
        'agent_id': ['A1'],
        'team': ['Chat Frontline'],
        'shift': ['Morning'],
        'from_date': ['2026-01-01'],
        'to_date': ['2026-12-31']
    })

    run_report('2026-06-22', '2026-06-22', None, df_tickets, df_agents, use_ai=False, api_key=None, is_interactive=True, header_already_printed=True)
    
    captured = capsys.readouterr()
    assert "AI insight unavailable; deterministic report generated successfully." in captured.out

def test_ai_insight_valid_qualitative(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    with patch('google.genai.Client') as mock_client_class:
        mock_client = mock_client_class.return_value
        valid_json = json.dumps({
            "what_happened": "many breaches at night",
            "interpretation": "lack of staffing",
            "recommended_test": "pilot shift changes",
            "caveat": "no queue data"
        })
        mock_client.models.generate_content.return_value = MagicMock(text=valid_json)
        res = generate_insight({"test": 123})
        assert res is not None
        assert res["what_happened"] == "many breaches at night"

def test_ai_insight_digit_rejected(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    with patch('google.genai.Client') as mock_client_class:
        mock_client = mock_client_class.return_value
        digit_json = json.dumps({
            "what_happened": "we had 5 breaches",
            "interpretation": "bad",
            "recommended_test": "test",
            "caveat": "none"
        })
        mock_client.models.generate_content.return_value = MagicMock(text=digit_json)
        res = generate_insight({"test": 123}, retries=1)
        assert res == "WITHHELD"
        assert mock_client.models.generate_content.call_count == 2

def test_ai_insight_banned_phrase_rejected(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    with patch('google.genai.Client') as mock_client_class:
        mock_client = mock_client_class.return_value
        banned_json = json.dumps({
            "what_happened": "breaches",
            "interpretation": "hire more agents",
            "recommended_test": "test",
            "caveat": "none"
        })
        mock_client.models.generate_content.return_value = MagicMock(text=banned_json)
        res = generate_insight({"test": 123}, retries=1)
        assert res == "WITHHELD"
        assert mock_client.models.generate_content.call_count == 2

def test_ai_insight_malformed_json(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    with patch('google.genai.Client') as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.models.generate_content.return_value = MagicMock(text="{bad json")
        res = generate_insight({"test": 123}, retries=1)
        assert res is None
        assert mock_client.models.generate_content.call_count == 2

def test_ai_insight_missing_field(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    with patch('google.genai.Client') as mock_client_class:
        mock_client = mock_client_class.return_value
        missing_json = json.dumps({
            "what_happened": "breaches",
            "interpretation": "bad"
        })
        mock_client.models.generate_content.return_value = MagicMock(text=missing_json)
        res = generate_insight({"test": 123}, retries=1)
        assert res is None
        assert mock_client.models.generate_content.call_count == 2
