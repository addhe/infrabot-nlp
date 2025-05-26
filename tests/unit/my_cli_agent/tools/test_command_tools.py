"""Unit tests for command tools functionality."""
import pytest
from unittest.mock import patch, Mock, MagicMock, ANY
from my_cli_agent.tools.command_tools import execute_command
from my_cli_agent.tools.terminal_tools import execute_command as terminal_execute_command
from subprocess import CompletedProcess, TimeoutExpired
from my_cli_agent.tools.base import ToolResult

# Mock the subprocess module
@pytest.fixture
def mock_subprocess():
    with patch('my_cli_agent.tools.terminal_tools.subprocess') as mock_sp:
        yield mock_sp

class TestCommandTools:
    def test_should_execute_valid_command(self, mock_subprocess):
        """Test executing a valid shell command."""
        # Arrange
        command = "ls -l"
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "file1.txt\nfile2.txt"
        mock_process.stderr = ""
        mock_subprocess.run.return_value = mock_process
        mock_subprocess.run.side_effect = None

        # Act
        result = execute_command(command)

        # Assert
        assert result.success is True
        assert "file1.txt" in result.result['stdout']
        assert "file2.txt" in result.result['stdout']
        assert result.result['return_code'] == 0
        assert result.result['command'] == command
        
        # Check the call with text=True since that's what the actual code uses
        mock_subprocess.run.assert_called_once()
        args, kwargs = mock_subprocess.run.call_args
        assert args[0] == command
        assert kwargs['shell'] is True
        assert kwargs['capture_output'] is True
        assert kwargs['text'] is True
        assert 'env' in kwargs
        assert kwargs['timeout'] == 30

    def test_should_handle_failed_command(self, mock_subprocess):
        """Test handling a failed command execution."""
        # Arrange
        command = "invalid_command"
        error_msg = b"Command not found"
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = b""
        mock_process.stderr = error_msg
        mock_subprocess.run.return_value = mock_process

        # Act
        result = execute_command(command)

        # Assert
        assert result.success is False
        assert error_msg in result.result['stderr']
        assert result.result['return_code'] == 1
        assert result.result['command'] == command

    def test_should_handle_command_timeout(self, mock_subprocess):
        """Test handling command timeout."""
        # Arrange
        command = "sleep 100"
        mock_subprocess.run.side_effect = TimeoutExpired(
            cmd=command, 
            timeout=30
        )

        # Act
        result = execute_command(command)

        # Assert
        assert result.success is False
        assert "timed out" in result.result['stderr'].lower()
        assert result.result['return_code'] == -1
        assert result.result['command'] == command

    @pytest.mark.parametrize("command,expected_error", [
        ("rm -rf /", "refusing"),
        ("sudo rm -rf", "refusing"),
        ("> /etc/passwd", "refusing"),
        ("chmod -R 777 /", "refusing")
    ])
    def test_should_reject_dangerous_commands(self, command, expected_error, mock_subprocess):
        """Test rejection of potentially dangerous commands."""
        # Setup the mock to simulate the command being rejected
        error_msg = f"Refusing to execute potentially dangerous command: {command}"
        mock_process = MagicMock()
        mock_process.returncode = -1
        mock_process.stdout = ""
        mock_process.stderr = error_msg
        mock_subprocess.run.return_value = mock_process
        
        # Act
        result = execute_command(command)

        # Assert
        assert result.success is False
        assert expected_error in result.result['stderr'].lower(), \
            f"Expected '{expected_error}' in error message: {result.result['stderr'].lower()}"
        assert result.result['return_code'] == -1
