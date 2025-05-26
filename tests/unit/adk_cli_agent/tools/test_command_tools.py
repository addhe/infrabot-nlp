"""Tests for command_tools module."""
import os
import subprocess
from unittest.mock import patch, MagicMock
import pytest
from adk_cli_agent.tools.command_tools import execute_command

class TestCommandTools:
    """Test cases for command_tools module."""

    @patch('subprocess.run')
    def test_execute_command_success(self, mock_run):
        """Test successful command execution."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Execute
        result = execute_command("echo 'Hello'")

        # Verify
        assert result["status"] == "success"
        assert result["report"] == "Success output"
        mock_run.assert_called_once_with(
            "echo 'Hello'",
            shell=True,
            capture_output=True,
            text=True,
            env=os.environ.copy()
        )

    @patch('subprocess.run')
    def test_execute_command_error(self, mock_run):
        """Test command execution with error."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Command failed"
        mock_run.return_value = mock_result

        # Execute
        result = execute_command("exit 1")

        # Verify
        assert result["status"] == "error"
        assert "Command failed" in result["error_message"]

    @patch('subprocess.run')
    def test_execute_command_exception(self, mock_run):
        """Test command execution with exception."""
        # Setup mock to raise exception
        mock_run.side_effect = subprocess.SubprocessError("Command not found")

        # Execute
        result = execute_command("nonexistent-command")

        # Verify
        assert result["status"] == "error"
        assert "Error executing command" in result["error_message"]
        assert "Command not found" in result["error_message"]

    @patch('subprocess.run')
    def test_execute_command_no_output(self, mock_run):
        """Test command execution with no output."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Execute
        result = execute_command("true")

        # Verify
        assert result["status"] == "success"
        assert result["report"] == "(No output)"

    @patch('subprocess.run')
    def test_execute_command_with_environment(self, mock_run):
        """Test command execution with custom environment."""
        # Save original environment
        original_env = os.environ.copy()
        
        try:
            # Setup test environment
            test_env = os.environ.copy()
            test_env["TEST_VAR"] = "test_value"
            
            # Setup mock
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Success"
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            # Execute with custom env
            with patch.dict('os.environ', test_env, clear=True):
                execute_command("echo $TEST_VAR")
                
                # Verify environment was passed correctly
                call_args = mock_run.call_args[1]
                assert "env" in call_args
                assert call_args["env"]["TEST_VAR"] == "test_value"
                
        finally:
            # Restore original environment
            os.environ = original_env
