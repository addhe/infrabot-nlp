import os
import unittest
from unittest.mock import patch, MagicMock
from my_cli_agent.tools.mcp_tools import call_mcp_server
from my_cli_agent.models import ToolResult
import requests

class TestMcpTools(unittest.TestCase):

    @patch.dict(os.environ, {"MCP_SERVER_URL": "http://mock-mcp-server:8000"})
    @patch('requests.post')
    def test_call_mcp_server_success(self, mock_post):
        """Test a successful call to the MCP server."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "MCP process complete."}
        mock_post.return_value = mock_response

        # Act
        result = call_mcp_server("do a complex task")

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.result, "MCP process complete.")
        mock_post.assert_called_once_with(
            "http://mock-mcp-server:8000/",
            json={"prompt": "do a complex task"},
            headers={"Content-Type": "application/json"},
            timeout=120
        )

    @patch.dict(os.environ, {"MCP_SERVER_URL": "http://mock-mcp-server:8000"})
    @patch('requests.post')
    def test_call_mcp_server_http_error(self, mock_post):
        """Test a call that results in an HTTP error."""
        # Arrange
        mock_post.side_effect = requests.exceptions.HTTPError("500 Server Error")

        # Act
        result = call_mcp_server("do a task that fails")

        # Assert
        self.assertFalse(result.success)
        self.assertIn("Failed to connect to the MCP server", result.error_message)
        self.assertIn("500 Server Error", result.error_message)

    @patch.dict(os.environ, {"MCP_SERVER_URL": "http://mock-mcp-server:8000"})
    @patch('requests.post')
    def test_call_mcp_server_timeout(self, mock_post):
        """Test a call that times out."""
        # Arrange
        mock_post.side_effect = requests.exceptions.Timeout("Connection timed out")

        # Act
        result = call_mcp_server("do a very long task")

        # Assert
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "The request to the MCP server timed out (120 seconds).")

    def test_mcp_server_url_not_set(self):
        """Test when the MCP_SERVER_URL environment variable is not set."""
        # Arrange: Ensure the variable is not set
        if "MCP_SERVER_URL" in os.environ:
            del os.environ["MCP_SERVER_URL"]

        # Act
        result = call_mcp_server("any prompt")

        # Assert
        self.assertFalse(result.success)
        self.assertIn("MCP_SERVER_URL environment variable is not set", result.error_message)

if __name__ == '__main__':
    unittest.main()
