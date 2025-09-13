import unittest
from unittest.mock import patch
from my_cli_agent.tools.terminal_tools import execute_command
from my_cli_agent.models import ToolResult

class TestTerminalTools(unittest.TestCase):

    def test_execute_command_success(self):
        """Test a simple, successful command."""
        result = execute_command('echo "hello world"')
        self.assertIsInstance(result, ToolResult)
        self.assertTrue(result.success)
        self.assertEqual(result.result, "hello world")
        self.assertIsNone(result.error_message)

    def test_execute_command_success_no_output(self):
        """Test a successful command that produces no stdout."""
        # The `true` command is perfect for this as it does nothing but exit with 0.
        result = execute_command('true')
        self.assertTrue(result.success)
        self.assertEqual(result.result, "Command 'true' executed successfully with no output.")

    def test_execute_command_failure(self):
        """Test a command that fails (non-zero exit code)."""
        # 'false' exits with 1. 'ls' to a non-existent dir also works.
        command = "ls /non_existent_directory_12345"
        result = execute_command(command)
        self.assertFalse(result.success)
        self.assertIsNone(result.result)
        self.assertIn(f"Command '{command}' failed", result.error_message)
        self.assertIn("No such file or directory", result.error_message)

    def test_security_check_dangerous_command(self):
        """Test that a dangerous command is blocked."""
        result = execute_command("sudo rm -rf /")
        self.assertFalse(result.success)
        self.assertIn("Refusing to execute potentially dangerous command", result.error_message)

    @patch('subprocess.run')
    def test_command_timeout(self, mock_subprocess_run):
        """Test the timeout functionality."""
        from subprocess import TimeoutExpired
        command = "sleep 100"
        mock_subprocess_run.side_effect = TimeoutExpired(cmd=command, timeout=30)
        
        result = execute_command(command)
        self.assertFalse(result.success)
        self.assertIn("timed out after 30 seconds", result.error_message)

    @patch('subprocess.run')
    def test_unexpected_exception(self, mock_subprocess_run):
        """Test handling of other unexpected subprocess errors."""
        command = "some_command"
        mock_subprocess_run.side_effect = OSError("File not found")

        result = execute_command(command)
        self.assertFalse(result.success)
        self.assertIn("An unexpected error occurred", result.error_message)
        self.assertIn("File not found", result.error_message)

if __name__ == '__main__':
    unittest.main()
