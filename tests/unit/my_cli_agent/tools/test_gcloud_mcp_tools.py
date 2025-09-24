import os
import unittest
from unittest.mock import patch, MagicMock
from my_cli_agent.tools.gcloud_mcp_tools import run_gcloud_command, _call_gcloud_mcp
from my_cli_agent.models import ToolResult
import requests

class TestGcloudMcpTools(unittest.TestCase):

    @patch.dict(os.environ, {"GCLOUD_MCP_SERVER_URL": "http://mock-gcloud-server/"})
    @patch('requests.post')
    def test_call_gcloud_mcp_success(self, mock_post):
        """Test the internal helper function for a successful call."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "ok"}'
        mock_post.return_value = mock_response

        # Act
        result = _call_gcloud_mcp("test_tool", {"param": "value"})

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.result, '{"status": "ok"}')
        mock_post.assert_called_once_with(
            "http://mock-gcloud-server/mcp",
            json={"tool": "test_tool", "params": {"param": "value"}},
            headers={"Content-Type": "application/json"},
            timeout=120
        )

    def test_url_not_set(self):
        """Test that tools fail gracefully when the URL is not set."""
        if "GCLOUD_MCP_SERVER_URL" in os.environ:
            del os.environ["GCLOUD_MCP_SERVER_URL"]
        
        result = run_gcloud_command(["compute", "instances", "list"])
        self.assertFalse(result.success)
        self.assertIn("GCLOUD_MCP_SERVER_URL environment variable is not set", result.error_message)

    @patch('my_cli_agent.tools.gcloud_mcp_tools._call_gcloud_mcp')
    def test_run_gcloud_command(self, mock_call):
        """Test the run_gcloud_command tool function."""
        cmd_list = ["compute", "instances", "list"]
        run_gcloud_command(command=cmd_list)
        # Verify the inner helper is still called with the correct 'args' key for the MCP server
        mock_call.assert_called_once_with("run_gcloud_command", {"args": cmd_list})

    def test_run_gcloud_command_invalid_input(self):
        """Test run_gcloud_command with invalid input type."""
        result = run_gcloud_command(command="this is not a list")
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Invalid input: command must be a list of strings.")

    @patch.dict(os.environ, {"GCLOUD_MCP_SERVER_URL": "http://mock-gcloud-server"}) # No trailing slash
    @patch('requests.post')
    def test_call_gcloud_mcp_url_no_slash(self, mock_post):
        """Test that the URL is correctly formatted when the env var has no trailing slash."""
        mock_post.return_value = MagicMock(status_code=200, text='ok')
        _call_gcloud_mcp("test", {})
        mock_post.assert_called_once_with(
            "http://mock-gcloud-server/mcp",
            json={"tool": "test", "params": {}},
            headers={"Content-Type": "application/json"},
            timeout=120
        )

    @patch('requests.post', side_effect=requests.exceptions.Timeout)
    @patch.dict(os.environ, {"GCLOUD_MCP_SERVER_URL": "http://mock-server.com/"})
    def test_call_gcloud_mcp_timeout(self, mock_post):
        """Test the helper's timeout exception handling."""
        result = _call_gcloud_mcp("test", {})
        self.assertFalse(result.success)
        self.assertIn("timed out", result.error_message)

    @patch('requests.post', side_effect=requests.exceptions.RequestException("Connection failed"))
    @patch.dict(os.environ, {"GCLOUD_MCP_SERVER_URL": "http://mock-server.com/"})
    def test_call_gcloud_mcp_request_exception(self, mock_post):
        """Test the helper's request exception handling."""
        result = _call_gcloud_mcp("test", {})
        self.assertFalse(result.success)
        self.assertIn("Failed to connect", result.error_message)

    @patch('requests.post', side_effect=Exception("Unexpected error"))
    @patch.dict(os.environ, {"GCLOUD_MCP_SERVER_URL": "http://mock-server.com/"})
    def test_call_gcloud_mcp_generic_exception(self, mock_post):
        """Test the helper's generic exception handling."""
        result = _call_gcloud_mcp("test", {})
        self.assertFalse(result.success)
        self.assertIn("An unexpected error occurred", result.error_message)

if __name__ == '__main__':
    unittest.main()
