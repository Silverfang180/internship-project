import pytest
import sys
from unittest.mock import patch, MagicMock

try:
    from src.cli_input import getpass_asterisk
except ImportError:
    pass

@pytest.mark.skipif("msvcrt" not in sys.modules and sys.platform != "win32", reason="Requires Windows msvcrt")
def test_getpass_asterisk_typing():
    with patch('msvcrt.getch') as mock_getch, \
         patch('sys.stdout.write') as mock_write, \
         patch('sys.stdout.flush'):
        
        # Simulate typing 'a', 'b', then Enter
        mock_getch.side_effect = [b'a', b'b', b'\r']
        
        result = getpass_asterisk("Prompt: ")
        
        assert result == "ab"
        # Should write Prompt:, then *, then *, then \n
        mock_write.assert_any_call("Prompt: ")
        mock_write.assert_any_call("*")
        mock_write.assert_any_call("\n")
        assert mock_write.call_count == 4 # Prompt + 2 asterisks + newline

@pytest.mark.skipif("msvcrt" not in sys.modules and sys.platform != "win32", reason="Requires Windows msvcrt")
def test_getpass_asterisk_backspace():
    with patch('msvcrt.getch') as mock_getch, \
         patch('sys.stdout.write') as mock_write, \
         patch('sys.stdout.flush'):
        
        # Simulate 'a', 'b', backspace, 'c', Enter
        mock_getch.side_effect = [b'a', b'b', b'\x08', b'c', b'\n']
        
        result = getpass_asterisk("Prompt: ")
        
        assert result == "ac"
        mock_write.assert_any_call("\b \b")

@pytest.mark.skipif("msvcrt" not in sys.modules and sys.platform != "win32", reason="Requires Windows msvcrt")
def test_getpass_asterisk_ctrl_c():
    with patch('msvcrt.getch') as mock_getch:
        mock_getch.side_effect = [b'\x03']
        with pytest.raises(KeyboardInterrupt):
            getpass_asterisk("Prompt: ")
