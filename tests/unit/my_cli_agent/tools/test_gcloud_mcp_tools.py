import os
import unittest
from unittest.mock import patch, MagicMock
from my_cli_agent.tools.gcloud_mcp_tools import run_gcloud_command, _call_gcloud_mcp
from my_cli_agent.models import ToolResult
import requests

class TestGcloudMcpTools(unittest.TestCase):

    @patch.dict(os.environ, {"GCLOUD_MCP_SERVER_URL": "http://mock-gcloud-server/"})
    @patch('requests.post')
    def test_call_gcloud_mcp_primary_success(self, mock_post):
        """Primary path (root with input) returns non-empty 2xx and is used."""
        # Arrange: primary call success
        mock_response_primary = MagicMock()
        mock_response_primary.status_code = 200
        mock_response_primary.text = '{"status": "ok"}'
        mock_post.return_value = mock_response_primary

        # Act
        result = _call_gcloud_mcp("test_tool", {"param": "value"})

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.result, '{"status": "ok"}')
        mock_post.assert_called_once_with(
            "http://mock-gcloud-server/",
            json={"tool": "test_tool", "input": {"param": "value"}},
            headers={"Content-Type": "application/json", "Accept": "application/json, text/plain;q=0.8,*/*;q=0.5"},
            timeout=120
        )

    @patch.dict(os.environ, {"GCLOUD_MCP_SERVER_URL": "http://mock-gcloud-server"})
    @patch('requests.post')
    def test_call_gcloud_mcp_fallback_when_empty_body(self, mock_post):
        """When primary returns 2xx with empty body, fallback to /mcp with params is used."""
        # Arrange: primary empty, then fallback success
        mock_response_primary = MagicMock()
        mock_response_primary.status_code = 200
        mock_response_primary.text = ''

        mock_response_fallback = MagicMock()
        mock_response_fallback.status_code = 200
        mock_response_fallback.text = '{"status": "ok-fallback"}'

        mock_post.side_effect = [mock_response_primary, mock_response_fallback]

        # Act
        result = _call_gcloud_mcp("test_tool", {"param": "value"})

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.result, '{"status": "ok-fallback"}')
        self.assertEqual(mock_post.call_count, 2)
        # First call: primary
        mock_post.assert_any_call(
            "http://mock-gcloud-server/",
            json={"tool": "test_tool", "input": {"param": "value"}},
            headers={"Content-Type": "application/json", "Accept": "application/json, text/plain;q=0.8,*/*;q=0.5"},
            timeout=120
        )
        # Second call: fallback
        mock_post.assert_any_call(
            "http://mock-gcloud-server/mcp",
            json={"tool": "test_tool", "params": {"param": "value"}},
            headers={"Content-Type": "application/json", "Accept": "application/json, text/plain;q=0.8,*/*;q=0.5"},
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

if __name__ == '__main__':
    unittest.main()
